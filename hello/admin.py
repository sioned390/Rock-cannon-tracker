from django.contrib import admin

from .models import (
	BanAppeal,
	Comment,
	ContributorProfile,
	RockCannon,
	RockCannonPhoto,
	Trail,
)


class RockCannonPhotoInline(admin.TabularInline):
	model = RockCannonPhoto
	extra = 0





class TrailInline(admin.TabularInline):
	model = Trail
	extra = 0


@admin.register(RockCannon)
class RockCannonAdmin(admin.ModelAdmin):
	list_display = ["name", "status", "is_reviewed", "created_at"]
	list_filter = ["status", "is_reviewed"]
	search_fields = ["name", "summary", "history"]
	prepopulated_fields = {"slug": ("name",)}


@admin.register(RockCannonPhoto)
class RockCannonPhotoAdmin(admin.ModelAdmin):
	list_display = ["rock_cannon", "uploaded_by", "uploaded_at", "is_reviewed"]
	list_filter = ["is_reviewed"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
	list_display = ["rock_cannon", "user", "created_at", "is_deleted"]
	list_filter = ["is_deleted"]




@admin.register(ContributorProfile)
class ContributorProfileAdmin(admin.ModelAdmin):
	list_display = ["user", "display_name", "is_moderator"]
	list_filter = ["is_moderator"]


@admin.register(BanAppeal)
class BanAppealAdmin(admin.ModelAdmin):
	list_display = ["user", "status", "created_at"]
	list_filter = ["status"]

