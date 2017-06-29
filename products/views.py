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

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

class ProductDetailView(generic.DetailView):
    template_name = 'products/product_detail.html'
    model = Product

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

class CategoryView(generic.ListView):
    model = Category
    template_name = 'products/category.html'
    context_object_name = 'category'

    def get_queryset(self):
        return Category.objects.filter(category=self.kwargs['category'])[0]

    def get_context_data(self, **kwargs):
        context = super(CategoryView, self).get_context_data(**kwargs)
        context['products'] = Product.objects.filter(category=context['category'])

        return context
