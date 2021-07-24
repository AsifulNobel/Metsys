from django.contrib import admin
from .models import Category, Product, ProductSize

# Register your models here.
class ProductInLine(admin.TabularInline):
    model = Product
    extra = 2

class CategoryAdmin(admin.ModelAdmin):
    inlines = [ProductInLine]

admin.site.register([Product, ProductSize])
admin.site.register(Category, CategoryAdmin)
