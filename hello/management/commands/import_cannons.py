"""
Management command to bulk-import rock cannon coordinates from a CSV file.

Usage:
    python manage.py import_cannons /path/to/file.csv
    python manage.py import_cannons /path/to/file.csv --epsg3857   # for Web Mercator coords

CSV formats supported:
  - With headers: lat/lon columns (or latitude/longitude/long variants)
  - Headerless: two columns assumed to be x, y (use with --epsg3857 for Web Mercator)
  - EPSG:3857: x (easting), y (northing) — auto-converted to WGS84 lat/lon

Optional columns (used if present): name, address, what3words, status, summary, history
"""

import csv
import math
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from hello.models import RockCannon


def epsg3857_to_wgs84(x, y):
    """Convert EPSG:3857 (Web Mercator) x/y metres to WGS84 lat/lon degrees."""
    R = 6378137.0
    lon = x * 180.0 / (math.pi * R)
    lat = math.degrees(math.atan(math.sinh(y / R)))
    return lat, lon


class Command(BaseCommand):
    help = "Import rock cannons from a CSV file (requires lat, lon columns or EPSG:3857 x/y)"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str, help="Path to the CSV file")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse and validate but do not write to the database",
        )
        parser.add_argument(
            "--epsg3857",
            action="store_true",
            help="Treat coordinates as EPSG:3857 Web Mercator (x/y metres) and convert to WGS84",
        )
        parser.add_argument(
            "--name-prefix",
            type=str,
            default="Cannon",
            help="Prefix used when auto-generating names (default: 'Cannon')",
        )
        parser.add_argument(
            "--start-index",
            type=int,
            default=1,
            help="Starting index number for auto-generated names (default: 1)",
        )

    def handle(self, *args, **options):
        csv_path = Path(options["csv_path"])
        if not csv_path.exists():
            raise CommandError(f"File not found: {csv_path}")

        dry_run = options["dry_run"]
        epsg3857 = options["epsg3857"]
        prefix = options["name_prefix"]
        idx = options["start_index"]

        created = 0
        skipped = 0
        errors = 0

        with csv_path.open(newline="", encoding="utf-8-sig") as f:
            raw = f.read()

        # Detect whether the file has a header row (headers contain letters)
        first_line = raw.splitlines()[0] if raw.strip() else ""
        has_header = any(c.isalpha() for c in first_line)

        import io
        if has_header:
            reader = csv.DictReader(io.StringIO(raw))
            rows = list(reader)
        else:
            # Headerless — treat columns as x, y (or lon, lat for non-EPSG3857)
            reader = csv.reader(io.StringIO(raw))
            rows = [{"_col0": r[0].strip(), "_col1": r[1].strip()} for r in reader if len(r) >= 2]

        self.stdout.write(f"Found {len(rows)} rows in {csv_path.name}")
        if epsg3857:
            self.stdout.write("  Converting from EPSG:3857 → WGS84")

        # Work out zero-padding width for auto names
        total = len(rows)
        pad = len(str(total + idx - 1))

        for row in rows:
            # Normalise keys
            row = {k.strip().lower(): v.strip() for k, v in row.items()}

            # --- Required fields ---
            try:
                if epsg3857 or ("_col0" in row):
                    # Headerless or explicit EPSG:3857 mode
                    x = float(row.get("_col0") or row.get("x") or "")
                    y = float(row.get("_col1") or row.get("y") or "")
                    if epsg3857:
                        lat_f, lon_f = epsg3857_to_wgs84(x, y)
                    else:
                        lon_f, lat_f = x, y  # headerless non-projected: col0=lon, col1=lat
                    lat = Decimal(str(round(lat_f, 6)))
                    lon = Decimal(str(round(lon_f, 6)))
                else:
                    lat = Decimal(row.get("lat") or row.get("latitude") or "")
                    lon = Decimal(row.get("lon") or row.get("longitude") or row.get("long") or "")
            except (InvalidOperation, ValueError, TypeError):
                self.stderr.write(f"  SKIP (bad coordinates): {row}")
                errors += 1
                idx += 1
                continue

            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                self.stderr.write(f"  SKIP (out-of-range coordinates): lat={lat}, lon={lon}")
                errors += 1
                idx += 1
                continue

            # --- Optional fields ---
            name = (
                row.get("name")
                or row.get("cannon_name")
                or f"{prefix} {str(idx).zfill(pad)}"
            )
            address = row.get("address", "")
            what3words = row.get("what3words", "")
            status = row.get("status", RockCannon.STATUS_ACTIVE)
            if status not in dict(RockCannon.STATUS_CHOICES):
                status = RockCannon.STATUS_ACTIVE
            summary = row.get("summary", "")
            history = row.get("history", "")

            # --- Slug collision avoidance ---
            base_slug = slugify(name)
            slug = base_slug
            suffix = 1
            while RockCannon.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{suffix}"
                suffix += 1

            if dry_run:
                self.stdout.write(
                    f"  [DRY RUN] Would create: {name!r} lat={lat} lon={lon}"
                )
            else:
                RockCannon.objects.create(
                    name=name,
                    slug=slug,
                    latitude=lat,
                    longitude=lon,
                    address=address,
                    what3words=what3words,
                    status=status,
                    summary=summary,
                    history=history,
                )
                self.stdout.write(self.style.SUCCESS(f"  Created: {name}  ({lat}, {lon})"))
                created += 1

            idx += 1

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Done — created: {created}, skipped/errors: {errors + skipped}"
            )
            if not dry_run
            else f"Dry run complete — would create: {total - errors}"
        )
