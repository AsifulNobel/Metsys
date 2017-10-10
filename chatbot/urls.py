"""chatbot_tutorial URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from .views import (chat, message_api, feedback_api,
complaint_save, complaint_delete, moderator_login, moderator_home,
ComplaintsView, complaintDetail, englishIntentAdd, banglaIntentAdd,
englishIntentDownload, banglaIntentDownload)

app_name = 'chatbot'

urlpatterns = [
	url(r'^$', chat, name='chat'),
    url(r'^message/', message_api, name='chat_api_message'),
    url(r'^feedback/', feedback_api, name='chat_api_feedback'),
    url(r'^complain-make/', complaint_save, name='chat_api_complain'),
    url(r'^complain-delete/', complaint_delete, name='chat_api_complain_withdraw'),
    url(r'^admin/login', moderator_login, name='modLogin'),
    url(r'^admin/logout', auth_views.logout, {'next_page': 'chatbot:modLogin'}, name='modLogout'),
    url(r'^admin/home', moderator_home, name='modHome'),
    url(r'^admin/complaints$', ComplaintsView.as_view(), name='modComplaints'),
    url(r'^admin/complaint/(?P<complaint_id>\d+)', complaintDetail, name='complaintDetails'),
    url(r'^admin/intents/english$', englishIntentAdd, name='englishIntentsAdd'),
    url(r'^admin/intents/english/download', englishIntentDownload, name='englishIntDown'),
    url(r'^admin/intents/bangla$', banglaIntentAdd, name='banglaIntentsAdd'),
    url(r'^admin/intents/bangla/download', banglaIntentDownload, name='banglaIntDown'),
]
