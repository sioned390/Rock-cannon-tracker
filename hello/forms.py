from django import forms

from .models import Comment, ContributorProfile, RockCannon, RockCannonPhoto


class RockCannonForm(forms.ModelForm):
    class Meta:
        model = RockCannon
        fields = [
            "name",
            "summary",
            "history",
            "latitude",
            "longitude",
            "address",
            "status",
        ]


class RockCannonPhotoForm(forms.ModelForm):
    class Meta:
        model = RockCannonPhoto
        fields = ["rock_cannon", "image", "caption"]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 3}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = ContributorProfile
        fields = ["display_name", "bio", "profile_picture"]
