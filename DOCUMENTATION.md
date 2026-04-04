#  Rock Cannons App 

## What Is This App?

- Find rock cannons on a map
- Share photos of rock cannons they've visited
- Leave comments and stories about them
- Create user profiles to show their contributions
- Help protect these special places by documenting them

---

1. **The Building (Django Framework)** = The structure that holds everything
2. **The Rooms (URLs)** = Different sections of the library you can visit
3. **The Librarians (Views)** = People who help you find what you need
4. **The Card Catalog (Models/Database)** = Where all information is stored
5. **The Forms** = The sign-up sheets and request cards
6. **The Books (Templates/HTML)** = The pretty pages you see

---

## Part 0: HOW TRANSLATION WORKS (Internationalization / i18n)

This app supports **two languages**:

- **English** (`en`) - the default language
- **Welsh** (`cy`) - the translated language

Django calls this system **internationalization** (**i18n**). It lets the site show the same page in different languages without building two separate websites.

### Where the translation settings live

The main configuration is in [web_project/settings.py](web_project/settings.py).

```python
from django.utils.translation import gettext_lazy as _

LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('en', _('English')),
    ('cy', _('Welsh')),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

USE_I18N = True
```

### What each setting means

- `LANGUAGE_CODE = 'en'` = the site starts in English by default
- `LANGUAGES` = the list of languages users are allowed to switch between
- `gettext_lazy as _` = lets Django translate labels such as **English** and **Welsh** lazily
- `LOCALE_PATHS` = tells Django where translation files are stored
- `USE_I18N = True` = turns Django's translation system on

### Why `LocaleMiddleware` matters

Also in [web_project/settings.py](web_project/settings.py), the middleware list contains:

```python
'django.middleware.locale.LocaleMiddleware',
```

This middleware is what makes Django:

- read the user's current language choice
- load the correct translated text
- show templates in English or Welsh automatically

Without `LocaleMiddleware`, the translation files can exist, but Django will not switch language properly for each request.

### How the language switch button works

The language switcher is in [hello/templates/hello/base.html](hello/templates/hello/base.html).

```django
{% load static i18n %}

<form action="{% url 'set_language' %}" method="post" style="display:inline;">
    {% csrf_token %}
    <input name="next" type="hidden" value="{{ request.path }}" />
    {% get_current_language as CURRENT_LANG %}
    {% if CURRENT_LANG == 'cy' %}
        <input name="language" type="hidden" value="en" />
        <button class="btn" type="submit">English</button>
    {% else %}
        <input name="language" type="hidden" value="cy" />
        <button class="btn" type="submit">Cymraeg</button>
    {% endif %}
</form>
```

### What this form does

1. The form posts to Django's built-in language-switching URL
2. The hidden `language` field sends either `en` or `cy`
3. The hidden `next` field tells Django which page to return to after switching
4. `CURRENT_LANG` checks which language is active right now
5. The button text changes so the user can switch to the *other* language

The URL for this form works because [web_project/urls.py](web_project/urls.py) includes:

```python
path('i18n/', include('django.conf.urls.i18n')),
```

That gives Django the built-in `set_language` view used by the form.

### How templates get translated

Templates that use translation must load Django's i18n tags first:

```django
{% load i18n %}
```

Then text can be wrapped with the `trans` tag:

```django
{% trans "List" %}
{% trans "Map" %}
{% trans "Gallery" %}
```

### What `trans` means

Think of it like this:

- Django sees the English source text, such as `"Gallery"`
- It looks for the same text in the translation file
- If a Welsh translation exists, Django shows the Welsh version
- If no translation exists, Django falls back to the original English text

So the English text inside `{% trans "..." %}` acts like the **lookup key**.

### Where the Welsh translations are stored

The Welsh translations live in [locale/cy/LC_MESSAGES/django.po](locale/cy/LC_MESSAGES/django.po).

Example:

```po
msgid "Gallery"
msgstr "Oriel"

msgid "Upload"
msgstr "Lanlwytho"
```

### What `msgid` and `msgstr` mean

- `msgid` = the original source text, usually written in English in templates or Python
- `msgstr` = the translated version shown to the user

So this means:

- If the page is in English, show `Gallery`
- If the page is in Welsh, show `Oriel`

### The full translation flow

Here is the complete path from code to translated page:

1. A template contains text such as `{% trans "Map" %}`
2. Django sees that the active language is `cy`
3. `LocaleMiddleware` loads the Welsh translations
4. Django checks [locale/cy/LC_MESSAGES/django.po](locale/cy/LC_MESSAGES/django.po) for `msgid "Map"`
5. It finds `msgstr "Map"`
6. The page is rendered using the translated value

### How to add a new translation

If you add new visible text to a template or Python file, the normal workflow is:

1. Wrap the text in a translation function or tag
2. Regenerate translation messages
3. Add the Welsh translation
4. Compile the messages

#### In templates

```django
{% trans "View Gallery" %}
```

#### In Python

```python
from django.utils.translation import gettext as _

message = _("Profile updated successfully")
```

### Useful commands

Run these from the project root:

```bash
./djangoProject/bin/python manage.py makemessages -l cy
./djangoProject/bin/python manage.py compilemessages
```

### What these commands do

- `makemessages -l cy` = scans the project for new translatable text and updates the Welsh `.po` file
- `compilemessages` = turns the human-readable `.po` file into a machine-usable `.mo` file

This project already contains both:

- [locale/cy/LC_MESSAGES/django.po](locale/cy/LC_MESSAGES/django.po) = editable translation source
- [locale/cy/LC_MESSAGES/django.mo](locale/cy/LC_MESSAGES/django.mo) = compiled file Django reads at runtime

### Important rule to remember

Only text wrapped for translation can be translated.

That means:

- plain text written directly in a template will stay in English
- text inside `{% trans "..." %}` can be translated
- text wrapped with `_()` in Python can be translated

### Example in plain English

If the template says:

```django
<a href="{% url 'gallery' %}">{% trans "Gallery" %}</a>
```

Then Django does this:

- English mode -> `Gallery`
- Welsh mode -> `Oriel`

That is the whole translation system: **mark text**, **store translations**, **switch language**, and **Django renders the correct version automatically**.

---

## Part 1: THE CORE DATA (Models)

### What is a "Model"?
A model is like a **filing cabinet drawer**. It defines what information you're going to store about something. 

```
Real-world example: A file about a person has:
- Name
- Age
- Email
- Phone number

Django Model: Creates a table in the database with these exact fields
```


###  **ContributorProfile** - People's Personal Pages

**[hello/models.py](hello/models.py):**
```python
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
```

**What each field does:**
- `user`: Links to Django's built-in User model (one-to-one = each user has exactly one profile)
- `on_delete=models.CASCADE` = If user account is deleted, profile is deleted too
- `display_name`: Optional nickname (max 120 characters)
- `bio`: Optional about-me section (unlimited text)
- `profile_picture`: User uploads their photo file to `profiles/` folder
- `profile_picture_data`: **Binary data** = The actual image converted to computer code (0s and 1s)
- `profile_picture_content_type`: Stores whether it's JPEG, PNG, etc. (defaults to "image/jpeg")
- `is_moderator`: Boolean flag (True/False) - default is False (regular user)

**The `save()` method **
```python
def save(self, *args, **kwargs):
    # When you upload a new profile picture
    if self.profile_picture and not self.profile_picture_data:
        # Open the image file in read-binary mode
        self.profile_picture.open("rb")
        # Read the raw image data and store it as binary
        self.profile_picture_data = self.profile_picture.read()
        # Get what type of image it is (JPEG, PNG, etc)
        self.profile_picture_content_type = getattr(self.profile_picture.file, "content_type", "image/jpeg")
    # Then save everything to the database
    super().save(*args, **kwargs)
```

**Translation:** "Every time we save this profile, if someone uploaded a new photo, store both the file AND the raw image data (so we can display it later without needing the file system)"

**The `__str__()` method:**
- When you print this object, show either the display_name or their username (whichever exists)

**Purpose:**
- Keeps user info organized
- Shows who uploaded what (trust and accountability)
- Creates a community feeling
- Stores images as binary data so they work even if files move

---

### **RockCannon** 

*** [hello/models.py](hello/models.py):**
```python
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
```

**What each field does:**

**Status choices:**
```python
STATUS_CHOICES = [
    (STATUS_ACTIVE, "Active"),          # Can visit it
    (STATUS_INACCESSIBLE, "Inaccessible"),  # Can't reach it
    (STATUS_DESTROYED, "Destroyed"),    # No longer exists
]
```
These define the options for the `status` field.

**Fields explained:**
- `name`: The cannon's name (max 200 characters)
- `slug`: URL-safe version like "stone-arch" (max 220 chars, unique=no two cannons have same slug)
- `summary`: Short description (unlimited text, optional)
- `history`: Long story about it (unlimited text, optional)
- `latitude/longitude`: GPS coordinates with 6 decimal places 
- `address`: Human-readable location (max 240 chars)
- `status`: One of the three choices above (defaults to "active")
- `created_by`: Links to the User who added it (ForeignKey - many cannons per user)
- `on_delete=models.SET_NULL` = If user is deleted, this field becomes NULL/empty (not deleted)
- `created_at`: Timestamp (auto_now_add=True = sets automatically when created)
- `updated_at`: Timestamp (auto_now=True = updates automatically whenever changed)
- `is_reviewed`: Boolean (moderators mark as True after checking it's real)

*** `save()` method:**
```python
def save(self, *args, **kwargs):
    if not self.slug:
        # If slug wasn't provided, create it from the name
        # "The Sling Rock Cannon" becomes "the-sling-rock-cannnon"
        self.slug = slugify(self.name)
    super().save(*args, **kwargs)
```

**Explanantion:** "Every time we save a cannon, if no slug was provided, automatically create one from the name"

**Purpose :**
- This is the heart of the app everything else connects to a rock cannon
- Stores location data so people can find them on maps
- Tracks who added what to credit them
- Status system lets moderators track cannon accessibility

---

###  **Trail** 

*** [hello/models.py]:**
```python
class Trail(models.Model):
	rock_cannon = models.ForeignKey(RockCannon, on_delete=models.CASCADE, related_name="trails")
	name = models.CharField(max_length=200)
	map_url = models.URLField(blank=True)
	geojson = models.TextField(blank=True)

	def __str__(self):
		return self.name
```

**What each field does:**
- `rock_cannon`: ForeignKey links to a RockCannon (one cannon can have many trails)
- `on_delete=models.CASCADE` = If the cannon is deleted, all its trails are deleted too
- `related_name="trails"` = In templates you can do `cannon.trails.all` to get all trails for that cannon
- `name`: The trail's name (max 200 chars)
- `map_url`: Optional link to external map service (URLField checks it's a valid URL)
- `geojson`: Optional technical map data in GeoJSON format (used for drawing paths)

**In templates:**
When you have a cannon object, you can access its trails like this:
```django
{% for trail in cannon.trails.all %}
    <li>{{ trail.name }}</li>
{% endfor %}
```

**Why:**
- Helps visitors plan their trip
- Shows different ways to reach each cannon
- Links external hiking apps

---

###  **RockCannonPhoto** Pictures Uploaded by Users

*** [hello/models.py]:**
```python
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
```

**What each field does:**
- `rock_cannon`: Which cannon this photo belongs to (many photos per cannon)
- `on_delete=models.CASCADE` = Deleting the cannon deletes all its photos
- `related_name="photos"` = Access via `cannon.photos.all` in templates
- `image`: The actual image file (stored in `media/rock_cannons/` folder)
- `image_data`: The image converted to binary
- `image_content_type`: Stores "image/jpeg" or "image/png" etc.
- `caption`: Optional description up to 240 chars
- `uploaded_by`: Which user uploaded it (ForeignKey to User)
- `on_delete=models.SET_NULL` = If user is deleted, this field becomes empty (photo stays)
- `uploaded_at`: Timestamp auto-set when created
- `is_reviewed`: Boolean for moderator approval

*** `save()` method:**
```python
def save(self, *args, **kwargs):
    if self.image and not self.image_data:
        # If there's an image and we haven't stored it as binary yet
        self.image.open("rb")  # Open the image file
        self.image_data = self.image.read()  # Read all the binary data
        # Store the content type (JPEG, PNG, etc.)
        self.image_content_type = getattr(self.image.file, "content_type", "image/jpeg")
    super().save(*args, **kwargs)
```

**Explaination:** "Every time we save a photo, if it's a new image file, convert it to binary data and store the type"
- `image` = file on disk (what you upload)
- `image_data` = binary in database (backup, works even if files move)

**In templates:**
```django
<img src="{% url 'photo_image' photo.id %}" alt="{{ photo.caption }}" />
```
This calls the `photo_image` view which returns the `image_data` as an image the browser can display.

**Purpose:**
- Creates a gallery 
- Binary storage means images are backed up in database

---

### **Comments** 

**[hello/models.py]:**
```python
class Comment(models.Model):
	rock_cannon = models.ForeignKey(RockCannon, on_delete=models.CASCADE, related_name="comments")
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	body = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	is_deleted = models.BooleanField(default=False)

	def __str__(self):
		return f"Comment on {self.rock_cannon.name}"
```

**What each field does:**
- `rock_cannon`: Which cannon this comment is about (many comments per cannon)
- `on_delete=models.CASCADE` = Deleting cannon deletes all its comments
- `related_name="comments"` = Access via `cannon.comments.all` in templates
- `user`: Who wrote the comment (can be anonymous/NULL)
- `on_delete=models.SET_NULL` = If user deleted, comment stays but user becomes NULL
- `body`: The actual comment text (unlimited)
- `created_at`: Auto-set timestamp when created
- `updated_at`: Auto-updated timestamp when modified
- `is_deleted`: Boolean (True = user deleted it, but we keep the data for records)

**Soft deletion:**
Notice `is_deleted` instead of deleting comments. This is called a "soft delete":
```python
# In view - only show non-deleted comments
comments = Comment.objects.filter(is_deleted=False)
```

**In templates:**
```django
{% for comment in cannon.comments.all %}
    <li>
        <strong>{{ comment.user|default:"Anonymous" }}</strong>
        {{ comment.created_at|date:"Y-m-d" }}
        {{ comment.body }}
    </li>
{% endfor %}
```

- Soft deletion keeps records but hides deleted comments

---

### **BanAppeal** - User Appeals System

**[hello/models.py]:**
```python
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
```

**What each field does:**
- `user`: Which user is appealing their ban (ForeignKey)
- `reason`: Their explanation for why they should be unbanned (unlimited text)
- `status`: One of three states - pending (waiting), approved (unbanned), or denied (rejected)
- `created_at`: When they submitted the appeal

**This feature:** Allows users who get banned to request a review from moderators

---

## Part 2: THE PAGES (URLs & Views) 



**URL** = The web address 
**View** = The Python function that decides what to show on that page





####  **HOME PAGE** (`/`)

*** [hello/views.py]:**
```python
def home(request):
    return render(request, "hello/home.html")
```

**What it does:**
- Takes the HTTP request
- Renders the home.html template
- Returns the HTML to the browser


**Template structure from [hello/templates/hello/base.html](hello/templates/hello/base.html):**
```django
<header>
    <nav>
        <div>
            <a href="{% url 'home' %}">Rock Cannons</a>
            <a href="{% url 'cannon_list' %}">List</a>
            <a href="{% url 'map_view' %}">Map</a>
            <a href="{% url 'gallery' %}">Gallery</a>
            <a href="{% url 'upload_cannon' %}">Upload</a>
        </div>
        <div>
            {% if user.is_authenticated %}
                <a href="{% url 'profile' %}">My Profile</a>
                <a href="{% url 'logout' %}">Sign out</a>
            {% else %}
                <a href="{% url 'login' %}">Sign in</a>
                <a href="{% url 'signup' %}">Register</a>
            {% endif %}
        </div>
    </nav>
</header>
```

This header appears on every page. It checks `user.is_authenticated` - if logged in, show Profile/Sign out, otherwise show Sign in/Register

---

####  **MAP VIEW** (`/map/`)

**[hello/views.py]:**
```python
def map_view(request):
    cannons = RockCannon.objects.all().order_by("name")
    return render(request, "hello/map.html", {"cannons": cannons})
```

**Step-by-step breakdown:**
1. `RockCannon.objects.all()` = Get all cannons from database
2. `.order_by("name")` = Sort them alphabetically by name
3. `return render(request, "hello/map.html", {"cannons": cannons})` = Pass them to template

**What the view passes to template:**
```python
{"cannons": cannons}  # Dictionary with key "cannons" containing all cannon objects
```

**In the template, you can access:**
```django
{% for cannon in cannons %}
    <!-- Access each cannon's data -->
    <li>{{ cannon.name }} - {{ cannon.latitude }}, {{ cannon.longitude }}</li>
{% endfor %}
```

- `RockCannon.objects.all()` is a Django ORM query (Object-Relational Mapping)
- `objects` = Manager that talks to the database
- `all()` = Get everything from the RockCannon table
- `.order_by("name")` = SQL equivalent: `ORDER BY name`

---

#### **CANNONS LIST** (`/cannons/`)

**[hello/views.py]:**
```python
def cannon_list(request):
    query = request.GET.get("q", "")

    cannons = RockCannon.objects.all().order_by("name")
    if query:
        cannons = cannons.filter(name__icontains=query)
    return render(
        request,
        "hello/cannon_list.html",
        {"cannons": cannons, "query": query},
    )
```

**Step-by-step:**
1. `request.GET.get("q", "")` = Get URL parameter named "q" (search query)
2. `RockCannon.objects.all().order_by("name")` = Get all cannons sorted alphabetically
3. `if query:` = Only if user typed something
4. `cannons.filter(name__icontains=query)` = Filter results
   - `name__icontains` = "Case-insensitive contains"
   - SQL equivalent: `WHERE name LIKE '%sling%'`
   - "The Sling Rock Cannon" matches "sling" 

**The template from [hello/templates/hello/cannon_list.html]:**
```django
<form method="get">
    <label for="q">Search by name</label>
    <input id="q" type="text" name="q" value="{{ query }}" />
    <button class="btn" type="submit">Apply</button>
</form>

<div class="grid">
    {% for cannon in cannons %}
        <div class="card">
            <h3>{{ cannon.name }}</h3>
            <p class="muted">{{ cannon.summary|default:"No summary yet" }}</p>
            <div style="margin-top: 1rem;">
                <a class="btn" href="{% url 'cannon_detail' cannon.slug %}">View details</a>
            </div>
        </div>
    {% empty %}
        <div class="card">
            <p class="muted">No rock cannons found.</p>
        </div>
    {% endfor %}
</div>
```

**How the form works:**
- `method="get"` = Sends search as URL parameter
- User types "sling" and clicks Apply
- Browser goes to `/cannons/?q=sling`
- View receives it and filters results


---

####  **CANNON DETAIL PAGE**

**Your actual code from [hello/views.py]:**
```python
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
```

**Step-by-step breakdown:**

**Part 1 - Finding the cannon:**
```python
cannon = get_object_or_404(
    RockCannon.objects.prefetch_related(...),
    slug=slug,
)
```
- `get_object_or_404()` = Get one object or show 404 error if not found
- `slug=slug` = Find cannon where slug matches URL parameter
- URL `/cannons/stone-arch/` → slug="stone-arch"

**Part 2 - Optimizing database queries with prefetch_related:**
```python
.prefetch_related(
    "photos",  # Load all RockCannonPhoto objects for this cannon
    "trails",  # Load all Trail objects for this cannon
    Prefetch("comments", queryset=Comment.objects.filter(is_deleted=False).order_by("-created_at")),
    # Load comments BUT filter out deleted ones AND sort newest first
)
```

**Why prefetch_related?**
Without it, each related item would be a separate database query (N+1 problem).
With prefetch_related, Django loads everything in 2-3 queries instead of 100+.

**Part 3 - Creating forms:**
```python
comment_form = CommentForm()  # Blank comment form
photo_form = RockCannonPhotoForm(initial={"rock_cannon": cannon})
# Photo form with cannon pre-filled
```

**The template from [hello/templates/hello/cannon_detail.html]:**
```django
{% extends 'hello/base.html' %}

{% block title %}{{ cannon.name }}{% endblock %}

{% block content %}
<div class="card">
    <h1>{{ cannon.name }}</h1>
    <p class="muted">Status: {{ cannon.get_status_display }}</p>
    <p>{{ cannon.summary }}</p>
    <h3>Local history</h3>
    <p>{{ cannon.history|default:"No history added yet." }}</p>
    <h3>Location</h3>
    <p>{{ cannon.address|default:"No address yet." }}</p>
    <p class="muted">{{ cannon.latitude }}, {{ cannon.longitude }}</p>
</div>

<div class="card">
    <h2>Walking & hiking trails</h2>
    <ul>
        {% for trail in cannon.trails.all %}
            <li>
                {{ trail.name }}
                {% if trail.map_url %}
                    - <a href="{{ trail.map_url }}">Map link</a>
                {% endif %}
            </li>
        {% empty %}
            <li class="muted">No trail data yet.</li>
        {% endfor %}
    </ul>
</div>

<div class="card">
    <h2>Photos</h2>
    <div class="grid">
        {% for photo in cannon.photos.all %}
            <div>
                <img class="responsive" src="{% url 'photo_image' photo.id %}" alt="{{ photo.caption }}" />
                <p class="muted">{{ photo.caption }}</p>
            </div>
        {% empty %}
            <p class="muted">No photos yet.</p>
        {% endfor %}
    </div>
</div>

<div class="card">
    <h2>Upload a photo</h2>
    <form method="post" enctype="multipart/form-data" action="{% url 'upload_photo' %}">
        {% csrf_token %}
        {{ photo_form.as_p }}
        <button class="btn" type="submit">Upload photo</button>
    </form>
</div>

<div class="card">
    <h2>Comments</h2>
    <form method="post" action="{% url 'add_comment' cannon.slug %}">
        {% csrf_token %}
        {{ comment_form.as_p }}
        <button class="btn" type="submit">Add comment</button>
    </form>
    <ul>
        {% for comment in cannon.comments.all %}
            <li>
                <strong>{{ comment.user|default:"Anonymous" }}</strong> - {{ comment.created_at|date:"Y-m-d" }}<br />
                {{ comment.body }}
            </li>
        {% empty %}
            <li class="muted">No comments yet.</li>
        {% endfor %}
    </ul>
</div>
{% endblock %}
```

**Template features explained:**
- `{{ cannon.get_status_display }}` = Shows "Active" instead of "active" (choice display names)
- `{% url 'photo_image' photo.id %}` = Generates URL to view the image
- `enctype="multipart/form-data"` = Required for file uploads
- `{% csrf_token %}` = Security token 
- `{{ form.as_p }}` = Renders form fields with paragraph tags

---

#### **GALLERY** (`/gallery/`)

*** [hello/views.py]:**
```python
def gallery(request):
    photos = RockCannonPhoto.objects.select_related("rock_cannon").order_by("-uploaded_at")
    return render(request, "hello/gallery.html", {"photos": photos})
```

**Breakdown:**
- `RockCannonPhoto.objects.select_related("rock_cannon")` = Get all photos AND their associated cannons
- `select_related()` = Efficient: gets related data in one query (vs separate queries)
- `.order_by("-uploaded_at")` = Sort by upload time, newest first (minus sign = descending)
- Returns all photos with cannon data pre-loaded

**Why select_related()?**
If you have 100 photos and don't use select_related, you'd make 101 queries:
1. One query to get all photos
2. 100 more queries to get each photo's cannon

With select_related, just 2 queries total (one for photos, one for all related cannons)

---

####  **UPLOAD CANNON** (`/upload/`)

**[hello/views.py]:**
```python
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
```

**Step-by-step for POST (form submission):**
```python
if request.method == "POST":
    # User clicked submit button
    form = RockCannonForm(request.POST)
    # Create form instance with submitted data
    
    if form.is_valid():
        # Django checks all fields (max length, required fields, etc.)
        cannon = form.save(commit=False)
        # Save to form's model but DON'T insert to database yet
        
        if request.user.is_authenticated:
            cannon.created_by = request.user
            # Set who created it before saving
        
        cannon.save()
        # NOW insert into database
        
        form.save_m2m()
        # Save many-to-many relationships (if any)
        
        return redirect("cannon_detail", slug=cannon.slug)
        # Redirect to the new cannon's detail page
```

**For GET (just visiting the page):**
```python
else:
    form = RockCannonForm()
    # Show blank form
return render(request, "hello/upload_cannon.html", {"form": form})
```

**The form from [hello/forms.py]:**
```python
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
```

**What ModelForm does:**
- Automatically generates form fields from model
- Includes validation (CharField = required, DecimalField = must be a number, etc.)
- Only shows fields in the `fields` list (hides `created_by`, `is_reviewed`, `slug`)

---

#### **UPLOAD PHOTO** (`/upload/photo/`)

*** [hello/views.py]:**
```python
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
```

**Explanation:**
```python
if request.method != "POST":
    raise Http404()
    # Only accept POST requests (form submissions)
    # If someone tries to visit /upload/photo/ directly, show 404 error
```

**Processing the upload:**
```python
form = RockCannonPhotoForm(request.POST, request.FILES)
# request.POST = form fields
# request.FILES = the image file(s)

if form.is_valid():
    photo = form.save(commit=False)  # Create but don't save yet
    if request.user.is_authenticated:
        photo.uploaded_by = request.user  # Track who uploaded
    photo.save()  # Insert into database
    
    return redirect("cannon_detail", slug=photo.rock_cannon.slug)
    # Go back to that cannon's page
```

**Error handling:**
```python
rock_cannon_id = request.POST.get("rock_cannon")
if rock_cannon_id:
    # If form invalid but we know the cannon, go back there
    cannon = get_object_or_404(RockCannon, id=rock_cannon_id)
    return redirect("cannon_detail", slug=cannon.slug)
return redirect("cannon_list")
# Otherwise go to list
```

**The form from [hello/forms.py]:**
```python
class RockCannonPhotoForm(forms.ModelForm):
    class Meta:
        model = RockCannonPhoto
        fields = ["rock_cannon", "image", "caption"]
```

**Why request.FILES?**
- Regular POST data is text (form fields)
- File uploads need special handling with `request.FILES`
- Form tag must have `enctype="multipart/form-data"`

---

#### **ADD COMMENT** (`/cannons/<cannon-name>/comment/`)

*** [hello/views.py]:**
```python
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
```

**Breakdown:**
```python
cannon = get_object_or_404(RockCannon, slug=slug)
# Find the cannon or show 404

if request.method == "POST":
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)  # Create but don't save
        comment.rock_cannon = cannon  # Attach to this cannon
        
        if request.user.is_authenticated:
            comment.user = request.user  # Track who wrote it
        
        comment.save()  # Insert into database

return redirect("cannon_detail", slug=slug)
# Go back to cannon page (whether it posted or not)
```

**always redirect back**
- Good UX: user sees their comment immediately
- Prevents accidental resubmissions (post/redirect/get pattern)

**The form from [hello/forms.py]:**
```python
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 3}),
        }
```

**The `widgets` dict:**
- Customizes HTML rendering
- `Textarea` with 3 rows instead of single-line input

---

####  **PROFILE** (`/profile/`)
**What it shows (if you're logged in):**
- Your profile info (name, bio, picture)
- All your uploaded photos
- All your comments
- Edit form for your profile

```python
@login_required  # Only logged-in users can see this
def profile(request):
    profile_obj, _ = ContributorProfile.objects.get_or_create(user=request.user)
    # Get profile or create blank one if first time visiting
    
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            form.save()  # Save profile updates
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile_obj)

    photos = RockCannonPhoto.objects.filter(uploaded_by=request.user)
    comments = Comment.objects.filter(user=request.user)
    # Load all their stuff
```

Translation:
1. Make sure user is logged in
2. Load or create their profile
3. If editing: save changes
4. Show all their photos and comments

---

#### **SIGNUP** (`/signup/`)

**Your actual code from [hello/views.py]:**
```python
def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})
```

**What it does:**
- `UserCreationForm` = Django built-in form (handles password validation)
- Checks password strength, confirms passwords match, etc.
- If valid: creates user account in database
- Redirects to login page

**Why UserCreationForm?**
Django provides this to handle password hashing securely (passwords aren't stored as plain text)

---

####  **LOGIN** (`/accounts/login/`)
**Built-in Django feature**
- URL route: automatically created by `include("django.contrib.auth.urls")`
- Template: `registration/login.html`
- Handles: username/password authentication

---

####  **LOGOUT** (`/accounts/logout/`)
**Built-in Django feature**
- Clears the session/cookies
- Redirects to URL specified in [web_project/settings.py](web_project/settings.py):
```python
LOGOUT_REDIRECT_URL = 'home'
```

---

####  **PHOTO IMAGE DISPLAY** (`/photos/<photo-id>/image/`)

***' [hello/views.py]:**
```python
def photo_image(request, photo_id):
    photo = get_object_or_404(RockCannonPhoto, id=photo_id)
    if not photo.image_data:
        raise Http404()
    return HttpResponse(photo.image_data, content_type=photo.image_content_type or "image/jpeg")
```

**What it does:**
1. Find the photo by ID
2. Check if binary image data exists
3. Return the raw image data with correct MIME type

**Why this exists:**
- Photos stored as binary in database
- Browsers need MIME type (image/jpeg, image/png) to render
- This view extracts the data and tells browser: "this is an image"

**How it's used in templates:**
```django
<img src="{% url 'photo_image' photo.id %}" alt="{{ photo.caption }}" />
```
- Generates URL: `/photos/42/image/`
- View returns binary image data
- Browser renders it

---

#### **PROFILE PICTURE DISPLAY** (`/profiles/<profile-id>/image/`)

**[hello/views.py]:**
```python
def profile_image(request, profile_id):
    profile_obj = get_object_or_404(ContributorProfile, id=profile_id)
    if not profile_obj.profile_picture_data:
        raise Http404()
    return HttpResponse(
        profile_obj.profile_picture_data,
        content_type=profile_obj.profile_picture_content_type or "image/jpeg",
    )
```

**Same as photo_image but for profiles**
- Finds profile by ID
- Returns binary picture data
- Sets correct MIME type

---

## Part 3: FORMS IN DETAIL 

### [hello/forms.py]

```python
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
```

**What ModelForm does:**
- Auto-generates form fields from model fields
- Includes validation rules from model
- `fields` list controls which ones appear in the form

**What's hidden:**
- `slug` - auto-generated from name
- `created_by` - set by view
- `created_at`, `updated_at` - auto-set by database
- `is_reviewed` - only moderators set this

---

```python
class RockCannonPhotoForm(forms.ModelForm):
    class Meta:
        model = RockCannonPhoto
        fields = ["rock_cannon", "image", "caption"]
```

**Fields:**
- `rock_cannon` - dropdown to select which cannon
- `image` - file upload
- `caption` - text description

**What's hidden:**
- `image_data`, `image_content_type` - auto-set by model's save() method
- `uploaded_by` - set by view
- `uploaded_at` - auto-timestamp
- `is_reviewed` - moderator approval

---

```python
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 3}),
        }
```

**What `widgets` does:**
- Customizes HTML rendering
- `Textarea` = multi-line text input
- `attrs={"rows": 3}` = 3 rows tall

**Generated HTML:**
```html
<textarea name="body" rows="3"></textarea>
```

**What's hidden:**
- `rock_cannon` - set by view
- `user` - set by view
- `created_at`, `updated_at` - auto-timestamps
- `is_deleted` - only admins set this

---

```python
class ProfileForm(forms.ModelForm):
    class Meta:
        model = ContributorProfile
        fields = ["display_name", "bio", "profile_picture"]
```

**Fields:**
- `display_name` - text (optional)
- `bio` - textarea (optional)
- `profile_picture` - file upload (optional)

**What's hidden:**
- `user` - linked to logged-in user
- `profile_picture_data`, `profile_picture_content_type` - auto-set
- `is_moderator` - admin only

---

## Part 4: ADMIN INTERFACE 

### [hello/admin.py]

Django provides an admin panel where moderators manage content. Here's the configuration:

```python
from django.contrib import admin

from .models import (
    BanAppeal,
    Comment,
    ContributorProfile,
    RockCannon,
    RockCannonPhoto,
    Trail,
)
```

**Admin Inlines :**

```python
class RockCannonPhotoInline(admin.TabularInline):
    model = RockCannonPhoto
    extra = 0
```

**What this does:**
- When editing a RockCannon, you can edit its photos inline
- `extra = 0` = don't add blank rows for new photos

```python
class TrailInline(admin.TabularInline):
    model = Trail
    extra = 0
```

**Same for trails edit them while editing a cannon**

---

**RockCannon Admin:**

```python
@admin.register(RockCannon)
class RockCannonAdmin(admin.ModelAdmin):
    list_display = ["name", "status", "is_reviewed", "created_at"]
    list_filter = ["status", "is_reviewed"]
    search_fields = ["name", "summary", "history"]
    prepopulated_fields = {"slug": ("name",)}
```

**Breakdown:**
- `list_display` = Columns shown in list view
- `list_filter` = Sidebar filters (status, is_reviewed)
- `search_fields` = Search these fields
- `prepopulated_fields` = Auto-fill slug from name

**In admin panel:**
- Moderators can see all cannons in a table
- Click to edit, approve (is_reviewed), change status
- Filter by active/inactive/destroyed

---

**RockCannonPhoto Admin:**

```python
@admin.register(RockCannonPhoto)
class RockCannonPhotoAdmin(admin.ModelAdmin):
    list_display = ["rock_cannon", "uploaded_by", "uploaded_at", "is_reviewed"]
    list_filter = ["is_reviewed"]
```

**For moderating photos:**
- See which cannon each photo is of
- Who uploaded it
- Whether it's approved

---

**Comment Admin:**

```python
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["rock_cannon", "user", "created_at", "is_deleted"]
    list_filter = ["is_deleted"]
```

**For moderating comments:**
- Which cannon it's about
- Who wrote it
- Can mark as deleted (soft delete)

---

**ContributorProfile Admin:**

```python
@admin.register(ContributorProfile)
class ContributorProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "display_name", "is_moderator"]
```

**For managing users:**
- User account
- Their display name
- Checkbox to make them moderator

---

## Part 5: THE DATABASE 

### What is SQLite?

SQLite is a **simple database** that stores all information as a file on disk (`db.sqlite3`).



### The Tables (Created from Models):

```
 ContributorProfile Table
├── ID | User | Display Name | Bio | Picture | Is Moderator


 RockCannon Table
├── ID | Name | Slug | Status | Latitude | Longitude | Created By

 RockCannonPhoto Table
├── ID | Rock Cannon ID | Caption | Uploaded By | Uploaded At


Comment Table
├── ID | Rock Cannon ID | User | Body | Created At

```



## Part 4: THE FORMS 


### The Forms:

####  **RockCannonForm**
Used on: Upload Cannon page
Fields you fill:
- name: "Name of the cannon"
- summary: "Quick description"
- history: "Full history story"
- latitude: "North-South GPS number"
- longitude: "East-West GPS number"
- address: "Street address"
- status: "Choose: active/inaccessible/destroyed"

---

#### **RockCannonPhotoForm**
Used on: Cannon detail page (photo upload button)
Fields you fill:
- rock_cannon: "Pick which cannon this photo is of"
- image: "Upload the photo file"
- caption: "Add a description"

---

#### **CommentForm**
Used on: Cannon detail page (comments section)
Fields you fill:
- body: "Write your comment" (shows as a big text box)

---

#### **ProfileForm**
Used on: Profile page
Fields you fill:
- display_name: "Your nickname"
- bio: "About you"
- profile_picture: "Upload your avatar"

---

## Part 5: SETTINGS & CONFIGURATION 

### settings.py - The Control Panel

**Key settings:**

```python
SECRET_KEY = 'xxxx'  # Secret password for encryption 
DEBUG = True  # Show detailed error messages (only for development)
ALLOWED_HOSTS = []  # Which websites can access this app
INSTALLED_APPS = ['hello', 'django.contrib.auth', ...]  # Which features to use
DATABASES = SQLite file location  # Where to store data
LOGIN_URL = 'login'  # Where to send non-logged-in users
MEDIA_ROOT = 'media'  # Where to save uploaded files
STATIC_ROOT = 'static'  # Where to save CSS/images
```

---



## Part 7: USER TYPES 👥

### Regular User
- Can browse cannons, photos, comments
- Can upload new cannons
- Can upload photos
- Can write comments
- Has a profile page
- Must create account to upload

### Moderator
- Has `is_moderator = True`
- Can do everything a regular user can do
- PLUS: Can approve new content (is_reviewed flag)
- Can delete comments (is_deleted flag)

### Anonymous/Not Logged In
- Can browse cannons, map, gallery
- Can search and read
- CANNOT upload, comment, or have profile
- Must signup/login first

---

## Part 8: KEY FEATURES EXPLAINED 

### Search Functionality
- User types in search box
- Django filters cannons by name containing that text
- Case-insensitive (uppercase/lowercase doesn't matter)

### GPS Mapping
- Each cannon has latitude/longitude numbers
- External map library (Leaflet) plots them
- Users can see exact locations

### Photo Storage
- Photos stored as binary data in database
- Also stored as actual files in `media/rock_cannons/` folder
- Database tracks metadata (caption, who uploaded, when)

### User Authentication
- Built into Django
- Tracks who's logged in via browser cookies
- Protects certain pages (profile only for logged-in users)

### Slug System
- Makes URL-friendly names
- Slug is unique (no two cannons with same slug)

---

## Part 9: FILE STRUCTURE 

```
Django/
├── db.sqlite3               The database (all data stored here)
├── manage.py                Command tool to run Django
│
├── web_project/             Project settings
│   ├── settings.py          Configuration
│   ├── urls.py              Main URL router
│   ├── wsgi.py              Server configuration
│   └── asgi.py              Alternative server config
│
├── hello/                   The main app
│   ├── models.py            Data definitions (RockCannon, Photo, etc.)
│   ├── views.py             Page logic (what to show)
│   ├── urls.py              App URL routes
│   ├── forms.py             Form definitions
│   ├── admin.py             Admin panel setup
│   ├── apps.py              App configuration
│   │
│   ├── templates/
│   │   └── hello/           HTML pages
│   │       ├── base.html    Main layout (used by all pages)
│   │       ├── home.html    Home page
│   │       ├── cannon_list.html
│   │       ├── cannon_detail.html
│   │       ├── gallery.html
│   │       ├── upload_cannon.html
│   │       └── profile.html
│   │
│   ├── static/
│   │   └── hello/
│   │       └── styles.css   Styling for all pages
│   │
│   └── migrations/          Database version history
│
├── templates/               Global HTML templates
│   └── registration/        Login/signup pages
│
├── media/                   Uploaded files (photos from users)
│   └── rock_cannons/        Photos go here
│
└── static/                  Global static files
    └── Rockcannon imgs/     Background images for pages
```

---

## Part 10: THE REQUEST-RESPONSE CYCLE 

**Here's how the whole thing works:**

```
User opens browser
    ↓
Types URL (e.g., /cannons/)
    ↓
Request reaches Django
    ↓
Django checks urls.py: "Which view should handle this?"
    ↓
Calls the right VIEW function
    ↓
View talks to DATABASE to get data
    ↓
View hands data to TEMPLATE (HTML file)
    ↓
Template combines data + HTML
    ↓
Generates complete HTML page
    ↓
Sends back to user's browser
    ↓
Browser displays the page
```

---

## Part 11: IMPORTANT CONCEPTS 

### One-to-Many Relationships
```
One RockCannon → Many Photos
  "The Sling Rock cannon" has 5 photos

One User → Many Comments
  "John" wrote 10 comments
```

### Foreign Keys

```
RockCannonPhoto has:
  rock_cannon = ForeignKey(RockCannon)
  
Meaning: "This photo belongs to a RockCannon"
When photo is deleted: What happens?
  on_delete=models.CASCADE means: "Delete me too"
```


---

## Part 12: HOW TO USE THE APP 

### For a Visitor:
```
1. Visit home page
2. Search for a cannon OR click on map
3. View cannon details, photos, comments
4. Read comments, see location
```

### For a Contributor:
```
1. Sign up for an account
2. Upload a new rock cannon (if you find one)
3. Upload photos of cannons you visit
4. Leave comments sharing knowledge
5. Visit your profile to see your contributions
```

### For a Moderator:
```
1. All contributor abilities
2. PLUS: Approve new cannons/photos (mark as reviewed)
3. PLUS: Delete bad comments
```

---

## Summary: It All Works Together 

```
┌─────────────────────────────────────┐
│          USER (Web Browser)         │
└────────┬────────────────────────────┘
         │ types URL
         ↓
┌─────────────────────────────────────┐
│      DJANGO URL ROUTER (urls.py)    │
│  "Which view handles this path?"    │
└────────┬────────────────────────────┘
         │ calls the right view
         ↓
┌─────────────────────────────────────┐
│      VIEW FUNCTION (views.py)       │
│  "Get data from database and        │
│   show it to the user"              │
└────────┬────────────────────────────┘
         │ queries database
         ↓
┌─────────────────────────────────────┐
│     DATABASE (db.sqlite3)           │
│  "Here's your rock cannons data"    │
└────────┬────────────────────────────┘
         │ returns data
         ↓
┌─────────────────────────────────────┐
│    TEMPLATE (HTML file)             │
│  "I'll arrange this data nicely"    │
└────────┬────────────────────────────┘
         │ generates HTML
         ↓
┌─────────────────────────────────────┐
│    BROWSER renders page             │
│    USER sees beautiful website      │
└─────────────────────────────────────┘
```

---

## Part 5: SETTINGS & CONFIGURATION 

### [web_project/settings.py]

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
```
- `BASE_DIR` = Root directory of project (where db.sqlite3 is)
- Used to define all file paths

```python
SECRET_KEY = 'django-insecure-wnx6^u278*$gk^asv44c5sz76-fq*6tw0k)rstvuc9z!x(w=^$'
DEBUG = True
ALLOWED_HOSTS = []
```
- `SECRET_KEY` = Encryption key 
- `DEBUG = True` = Show detailed error pages (only for development)
- `ALLOWED_HOSTS` = Which domains can access app (empty = localhost only)

```python
INSTALLED_APPS = [
    'django.contrib.admin',      # Admin panel
    'django.contrib.auth',       # User authentication
    'django.contrib.contenttypes',  # Content type framework
    'django.contrib.sessions',   # User sessions
    'django.contrib.messages',   # Flash messages
    'django.contrib.staticfiles',   # CSS/JS/Images
    'hello.apps.HelloConfig',    # Your app
]
```
- Built-in Django apps +  hello app
- Order matters (django apps first, then ours)

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```
- Middleware = code that runs on every request
- CSRF = prevents cross-site request forgery attacks
- Auth = handles login/logout
- Security = XFrame prevents clickjacking

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

```python
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'
```
- `LOGIN_URL` = Where to send non-logged-in users
- `LOGIN_REDIRECT_URL` = After login, go here
- `LOGOUT_REDIRECT_URL` = After logout, go here

---

## Part 6: URL ROUTING 

### Main URLs: [web_project/urls.py]

```python
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", include("hello.urls")),
    path('admin/', admin.site.urls)
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

**Breakdown:**
- `path("", include("hello.urls"))` = Include all hello app URLs at root
- `path('admin/', admin.site.urls)` = Admin panel at /admin/
- `if settings.DEBUG` = In development, serve uploaded files from `/media/`

---

### App URLs: [hello/urls.py]

```python
urlpatterns = [
    path("", views.home, name="home"),
    path("map/", views.map_view, name="map_view"),
    path("cannons/", views.cannon_list, name="cannon_list"),
    path("cannons/<slug:slug>/", views.cannon_detail, name="cannon_detail"),
    path("gallery/", views.gallery, name="gallery"),
    path("upload/", views.upload_cannon, name="upload_cannon"),
    path("upload/photo/", views.upload_photo, name="upload_photo"),
    path("cannons/<slug:slug>/comment/", views.add_comment, name="add_comment"),
    path("profile/", views.profile, name="profile"),
    path("photos/<int:photo_id>/image/", views.photo_image, name="photo_image"),
    path("profiles/<int:profile_id>/image/", views.profile_image, name="profile_image"),
    path("signup/", views.signup, name="signup"),
    path("accounts/", include("django.contrib.auth.urls")),
]
```

**URL parameters explained:**

**With slug (text):**
```python
path("cannons/<slug:slug>/", views.cannon_detail, name="cannon_detail")
```
- URL: `/cannons/stone-arch/`
- Captures "stone-arch" as `slug` parameter
- In view: `cannon_detail(request, slug="stone-arch")`

**With integer ID:**
```python
path("photos/<int:photo_id>/image/", views.photo_image, name="photo_image")
```
- URL: `/photos/42/image/`
- Captures 42 as `photo_id` parameter
- In view: `photo_image(request, photo_id=42)`

---

