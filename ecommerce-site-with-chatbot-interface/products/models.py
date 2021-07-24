from django.db import models
from django.utils.crypto import get_random_string

# Create your models here.
class Category(models.Model):
    category = models.CharField(max_length=25)
    count = models.PositiveIntegerField(editable=False, default=0)

    def __str__(self):
        return self.category

class ProductSize(models.Model):
    size = models.CharField(max_length=20)

class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=50, unique=True, editable=False)
    company = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    description = models.CharField(max_length=400)
    price = models.PositiveIntegerField(default=0)
    added_date = models.DateTimeField(auto_now_add=True)
    size = models.ForeignKey(ProductSize, on_delete=models.SET_NULL, null=True, blank=True)
    available_quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='product_images')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """ Add Slug creating/checking to save method. """
        slug_save(self) # call slug_save, listed below
        super(Product, self).save(*args, **kwargs)

def slug_save(obj):
    """ A function to generate a 12 character slug and see if it has been used."""
    if not obj.slug: # if there isn't a slug
        obj.slug = get_random_string(12) # create one
        slug_is_wrong = True
    else:
        slug_is_wrong = False

    while slug_is_wrong: # keep checking until we have a valid slug
        slug_is_wrong = False
        other_objs_with_slug = type(obj).objects.filter(slug=obj.slug)
        if len(other_objs_with_slug) > 0:
            # if any other objects have current slug
            slug_is_wrong = True
