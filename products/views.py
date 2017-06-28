from django.shortcuts import render
from django.views import generic
from django.core.urlresolvers import reverse
from django.utils import timezone

from .models import Category, ProductSize, Product
# Create your views here.

class IndexView(generic.ListView):
    template_name = 'products/index.html'
    context_object_name = 'latest_products'

    def get_queryset(self):
        """Return the last four added products."""
        return Product.objects.order_by('-added_date')[:4]

class ProductDetailView(generic.DetailView):
    template_name = 'products/product_detail.html'
    model = Product
