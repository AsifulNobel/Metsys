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
complaintList, complaintDetail, englishIntentAdd, banglaIntentAdd,
englishIntentDownload, banglaIntentDownload, train_english, train_bangla,
updateEnglishFile, updateBanglaFile, feedbackView, terminate_api, viewLog,
downloadLog, statsView)

app_name = 'chatbot'

urlpatterns = [
	url(r'^$', chat, name='chat'),
    url(r'^message$', message_api, name='chat_api_message'),
    url(r'^message/terminate$', terminate_api, name='chat_api_terminate'),
    url(r'^feedback/', feedback_api, name='chat_api_feedback'),
    url(r'^complain-make/', complaint_save, name='chat_api_complain'),
    url(r'^admin/login', moderator_login, name='modLogin'),
    url(r'^admin/logout', auth_views.logout, {'next_page': 'chatbot:modLogin'}, name='modLogout'),
    url(r'^admin/home', moderator_home, name='modHome'),
    url(r'^admin/log/view$', viewLog, name='modLogView'),
    url(r'^admin/log/download$', downloadLog, name='modLogDownload'),
    url(r'^admin/train-english$', train_english, name='trainEnglish'),
    url(r'^admin/train-bangla$', train_bangla, name='trainBangla'),
    url(r'^admin/complaints$', complaintList, name='modComplaints'),
    url(r'^admin/feedbacks$', feedbackView, name='modFeedbacks'),
    url(r'^admin/stats$', statsView, name='modStats'),
    url(r'^admin/complaint/(?P<complaint_id>\d+)$', complaintDetail, name='complaintDetails'),
    url(r'^admin/complaint/(?P<complaint_id>\d+)/delete/$', complaint_delete, name='complainWithdraw'),
    url(r'^admin/intents/english$', englishIntentAdd, name='englishIntentsAdd'),
    url(r'^admin/intents/english/download', englishIntentDownload, name='englishIntDown'),
    url(r'^admin/intents/english/file-update$', updateEnglishFile, name='updateEnglishFile'),
    url(r'^admin/intents/bangla$', banglaIntentAdd, name='banglaIntentsAdd'),
    url(r'^admin/intents/bangla/file-update$', updateBanglaFile, name='updateBanglaFile'),
    url(r'^admin/intents/bangla/download', banglaIntentDownload, name='banglaIntDown'),
]
