from django.conf.urls import url
from . import views

app_name = 'products'

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^products/(?P<slug>.+)/$', views.ProductDetailView.as_view(), name='product_detail'),
]
