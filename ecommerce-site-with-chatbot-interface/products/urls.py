from django.conf.urls import url
from . import views

app_name = 'products'

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^category/(?P<category>[\w-]+)', views.CategoryView.as_view(), name='category_products'),
    url(r'^products/(?P<slug>[\w-]+)/$', views.ProductDetailView.as_view(), name='product_detail'),
]
