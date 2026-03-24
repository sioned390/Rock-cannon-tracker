from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Prefetch
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from pathlib import Path

from .forms import CommentForm, ProfileForm, RockCannonForm, RockCannonPhotoForm
from .models import Comment, ContributorProfile, RockCannon, RockCannonPhoto


def home(request):
    return render(request, "hello/home.html")


def docs(request):
    doc_path = Path(__file__).resolve().parent.parent / "DOCUMENTATION.md"
    try:
        with open(doc_path, "r") as f:
            documentation = f.read()
    except FileNotFoundError:
        documentation = "Documentation file not found."
    
    return render(request, "hello/docs.html", {"documentation": documentation})


def map_view(request):
    cannons = RockCannon.objects.all().order_by("name")
    return render(request, "hello/map.html", {"cannons": cannons})


def cannon_list(request):
    cannons = RockCannon.objects.all().order_by("name")
    return render(
        request,
        "hello/cannon_list.html",
        {"cannons": cannons},
    )


def cannon_detail(request, slug):
    cannon = get_object_or_404(
        RockCannon.objects.prefetch_related(
            "photos",
            "trails",
            Prefetch("comments", queryset=Comment.objects.filter(is_deleted=False).order_by("-created_at")),
        ),
        slug=slug,
    )
    comment_form = CommentForm()
    photo_form = RockCannonPhotoForm(initial={"rock_cannon": cannon})
    return render(
        request,
        "hello/cannon_detail.html",
        {"cannon": cannon, "comment_form": comment_form, "photo_form": photo_form},
    )


def gallery(request):
    photos = RockCannonPhoto.objects.select_related("rock_cannon").order_by("-uploaded_at")
    return render(request, "hello/gallery.html", {"photos": photos})


def upload_cannon(request):
    if request.method == "POST":
        form = RockCannonForm(request.POST)
        if form.is_valid():
            cannon = form.save(commit=False)
            if request.user.is_authenticated:
                cannon.created_by = request.user
            cannon.save()
            form.save_m2m()
            return redirect("cannon_detail", slug=cannon.slug)
    else:
        form = RockCannonForm()
    return render(request, "hello/upload_cannon.html", {"form": form})


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
    return redirect("cannon_list")


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
