from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from django.db.models import Count, Prefetch, Q
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from pathlib import Path

from .forms import CommentForm, ProfileForm, RockCannonForm, RockCannonPhotoForm
from .models import Comment, ContributorProfile, RockCannon, RockCannonPhoto


def home(request):
    return render(request, "hello/home.html")

def about(request):
    return render(request, "hello/about.html")


def docs(request):
    doc_path = Path(__file__).resolve().parent.parent / "DOCUMENTATION.md"
    try:
        with open(doc_path, "r") as f:
            documentation = f.read()
    except FileNotFoundError:
        documentation = _("Documentation file not found.")
    
    return render(request, "hello/docs.html", {"documentation": documentation})


def map_view(request):
    cannons = RockCannon.objects.prefetch_related("photos").order_by("name")
    return render(
        request,
        "hello/map.html",
        {
            "cannons": cannons,
            "maptiler_api_key": settings.MAPTILER_API_KEY,
        },
    )


def filler(request):
    return render(request, "hello/filler.html")


def cannon_detail(request, slug):
    cannon = get_object_or_404(
        RockCannon.objects.select_related("created_by").prefetch_related(
            Prefetch("photos", queryset=RockCannonPhoto.objects.select_related("uploaded_by").order_by("-uploaded_at")),
            "trails",
            Prefetch(
                "comments",
                queryset=Comment.objects.filter(is_deleted=False).select_related("user").order_by("-created_at"),
            ),
        ),
        slug=slug,
    )
    comment_form = CommentForm()
    photo_form = RockCannonPhotoForm(initial={"rock_cannon": cannon})
    return render(
        request,
        "hello/cannon_detail.html",
        {
            "cannon": cannon,
            "comment_form": comment_form,
            "photo_form": photo_form,
            "maptiler_api_key": settings.MAPTILER_API_KEY,
        },
    )


def gallery(request):
    photos = RockCannonPhoto.objects.select_related("rock_cannon", "uploaded_by").order_by("-uploaded_at")
    return render(request, "hello/gallery.html", {"photos": photos})


def cannon_list(request):
    query = request.GET.get("q", "").strip()
    cannons = RockCannon.objects.annotate(photo_total=Count("photos"))

    if query:
        cannons = cannons.filter(Q(name__icontains=query))

    cannons = cannons.order_by("-created_at", "-id")
    return render(
        request,
        "hello/cannon_list.html",
        {
            "cannons": cannons,
            "search_query": query,
        },
    )


@login_required
def upload_cannon(request):
    if request.method == "POST":
        form = RockCannonForm(request.POST, request.FILES)
        if form.is_valid():
            cannon = form.save(commit=False)
            if request.user.is_authenticated:
                cannon.created_by = request.user
            cannon.save()
            form.save_m2m()
            for image in request.FILES.getlist("photos"):
                RockCannonPhoto.objects.create(
                    rock_cannon=cannon,
                    image=image,
                    uploaded_by=request.user if request.user.is_authenticated else None,
                )
            return redirect("cannon_detail", slug=cannon.slug)
    else:
        form = RockCannonForm()
    return render(request, "hello/upload_cannon.html", {"form": form})


@login_required
def edit_cannon(request, slug):
    cannon = get_object_or_404(RockCannon, slug=slug)

    can_edit = (
        request.user.is_superuser
        or cannon.created_by_id == request.user.id
        or cannon.created_by_id is None
    )
    if not can_edit:
        return HttpResponseForbidden(_("You do not have permission to edit this cannon."))

    if request.method == "POST":
        form = RockCannonForm(request.POST, request.FILES, instance=cannon)
        if form.is_valid():
            updated_cannon = form.save()
            return redirect("cannon_detail", slug=updated_cannon.slug)
    else:
        form = RockCannonForm(instance=cannon)

    return render(request, "hello/edit_cannon.html", {"form": form, "cannon": cannon})


@login_required
def upload_photo(request):
    if request.method != "POST":
        raise Http404()
    form = RockCannonPhotoForm(request.POST, request.FILES)
    if form.is_valid():
        photo = form.save(commit=False)
        if request.user.is_authenticated:
            photo.uploaded_by = request.user
        photo.save()
        return redirect("cannon_detail", slug=photo.rock_cannon.slug)

    rock_cannon_id = request.POST.get("rock_cannon")
    if rock_cannon_id:
        cannon = get_object_or_404(RockCannon, id=rock_cannon_id)
        return redirect("cannon_detail", slug=cannon.slug)
    return redirect("map_view")


def add_comment(request, slug):
    cannon = get_object_or_404(RockCannon, slug=slug)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.rock_cannon = cannon
            if request.user.is_authenticated:
                comment.user = request.user
            comment.save()
    return redirect("cannon_detail", slug=slug)


@login_required
def profile(request):
    profile_obj, _ = ContributorProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        if request.POST.get("clear_profile_picture") == "1":
            profile_obj.profile_picture = None
            profile_obj.profile_picture_data = None
            profile_obj.profile_picture_content_type = ""
            profile_obj.save()
            return redirect("profile")

        if request.POST.get("change_profile_picture") == "1":
            uploaded_picture = request.FILES.get("profile_picture")
            if uploaded_picture:
                profile_obj.profile_picture = uploaded_picture
                profile_obj.profile_picture_data = None
                profile_obj.profile_picture_content_type = ""
                profile_obj.save()
            return redirect("profile")

        form = ProfileForm(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile_obj)

    photos = RockCannonPhoto.objects.filter(uploaded_by=request.user).order_by("-uploaded_at")
    comments = Comment.objects.filter(user=request.user).order_by("-created_at")
    return render(
        request,
        "hello/profile.html",
        {"form": form, "photos": photos, "comments": comments},
    )


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


def photo_image(request, photo_id):
    photo = get_object_or_404(RockCannonPhoto, id=photo_id)
    if not photo.image_data:
        raise Http404()
    return HttpResponse(photo.image_data, content_type=photo.image_content_type or "image/jpeg")


def profile_image(request, profile_id):
    profile_obj = get_object_or_404(ContributorProfile, id=profile_id)
    if not profile_obj.profile_picture_data:
        raise Http404()
    return HttpResponse(
        profile_obj.profile_picture_data,
        content_type=profile_obj.profile_picture_content_type or "image/jpeg",
    )
