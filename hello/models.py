from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify

User = get_user_model()


class ContributorProfile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	display_name = models.CharField(max_length=120, blank=True)
	bio = models.TextField(blank=True)
	profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)
	profile_picture_data = models.BinaryField(blank=True, null=True)
	profile_picture_content_type = models.CharField(max_length=120, blank=True)
	is_moderator = models.BooleanField(default=False)

	def save(self, *args, **kwargs):
		if self.profile_picture and not self.profile_picture_data:
			self.profile_picture.open("rb")
			self.profile_picture_data = self.profile_picture.read()
			self.profile_picture_content_type = getattr(self.profile_picture.file, "content_type", "image/jpeg")
		super().save(*args, **kwargs)

	def __str__(self):
		return self.display_name or self.user.get_username()


class RockCannon(models.Model):
	STATUS_ACTIVE = "active"
	STATUS_INACCESSIBLE = "inaccessible"
	STATUS_DESTROYED = "destroyed"
	STATUS_CHOICES = [
		(STATUS_ACTIVE, "Active"),
		(STATUS_INACCESSIBLE, "Inaccessible"),
		(STATUS_DESTROYED, "Destroyed"),
	]

	name = models.CharField(max_length=200)
	slug = models.SlugField(max_length=220, unique=True, blank=True)
	summary = models.TextField(blank=True)
	history = models.TextField(blank=True)
	latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
	longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
	address = models.CharField(max_length=240, blank=True)
	status = models.CharField(max_length=24, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	is_reviewed = models.BooleanField(default=False)

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name)
		super().save(*args, **kwargs)

	def __str__(self):
		return self.name

class Trail(models.Model):
	rock_cannon = models.ForeignKey(RockCannon, on_delete=models.CASCADE, related_name="trails")
	name = models.CharField(max_length=200)
	map_url = models.URLField(blank=True)
	geojson = models.TextField(blank=True)

	def __str__(self):
		return self.name


class RockCannonPhoto(models.Model):
	rock_cannon = models.ForeignKey(RockCannon, on_delete=models.CASCADE, related_name="photos")
	image = models.ImageField(upload_to="rock_cannons/")
	image_data = models.BinaryField(blank=True, null=True)
	image_content_type = models.CharField(max_length=120, blank=True)
	caption = models.CharField(max_length=240, blank=True)
	uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	uploaded_at = models.DateTimeField(auto_now_add=True)
	is_reviewed = models.BooleanField(default=False)

	def save(self, *args, **kwargs):
		if self.image and not self.image_data:
			self.image.open("rb")
			self.image_data = self.image.read()
			self.image_content_type = getattr(self.image.file, "content_type", "image/jpeg")
		super().save(*args, **kwargs)

	def __str__(self):
		return f"{self.rock_cannon.name} photo"


class Comment(models.Model):
	rock_cannon = models.ForeignKey(RockCannon, on_delete=models.CASCADE, related_name="comments")
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	body = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	is_deleted = models.BooleanField(default=False)

	def __str__(self):
		return f"Comment on {self.rock_cannon.name}"



	



class BanAppeal(models.Model):
	STATUS_PENDING = "pending"
	STATUS_APPROVED = "approved"
	STATUS_DENIED = "denied"
	STATUS_CHOICES = [
		(STATUS_PENDING, "Pending"),
		(STATUS_APPROVED, "Approved"),
		(STATUS_DENIED, "Denied"),
	]

	user = models.ForeignKey(User, on_delete=models.CASCADE)
	reason = models.TextField()
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Ban appeal {self.user}"
