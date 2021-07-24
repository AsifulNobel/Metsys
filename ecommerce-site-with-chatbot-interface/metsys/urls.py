from django.conf.urls import url
from .views import home

app_name = 'metsys'

urlpatterns = [
	url(r'^$', home, name='home'),
]
