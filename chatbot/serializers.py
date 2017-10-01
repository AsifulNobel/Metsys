from rest_framework import serializers
from .models import Feedbacks

class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()

    def get_message(self):
        return self.data.get('message')

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedbacks
        fields = ('name', 'comment')
