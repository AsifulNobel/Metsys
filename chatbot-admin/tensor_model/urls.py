from django.conf.urls import url
from .views import (message_api, remove_user, train_english_chowdhury,
train_bangla_chowdhury)

app_name = 'tensor_model'

urlpatterns = [
    url(r'^chatbot/message$', message_api, name='chat'),
    url(r'^chatbot/user/delete$', remove_user, name='user_removal'),
    url(r'^chatbot/chowdhury/train/english$', train_english_chowdhury, name='english_training'),
    url(r'^chatbot/chowdhury/train/bangla$', train_bangla_chowdhury, name='bangla_training')
]
