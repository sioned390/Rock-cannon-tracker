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
            "what3words",
            "status",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
            {"placeholder": "Rock Cannon Name"}
        )
        self.fields["summary"].widget.attrs.update(
            {"placeholder": "Description about the rock cannon...", "rows": 6}
        )
        self.fields["history"].widget.attrs.update(
            {"placeholder": "History, lore, or route details...", "rows": 4}
        )
        self.fields["address"].widget.attrs.update(
            {"placeholder": "e.g. Pen-y-Pass car park"}
        )
        self.fields["what3words"].widget.attrs.update(
            {"placeholder": "e.g. filled.count.soap"}
        )
        self.fields["latitude"].widget.attrs.update(
            {"placeholder": "00.000000"}
        )
        self.fields["longitude"].widget.attrs.update(
            {"placeholder": "00.000000"}
        )


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
