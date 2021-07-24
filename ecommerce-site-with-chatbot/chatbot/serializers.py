from rest_framework import serializers
from .models import Feedbacks, Complaints, SessionTracker

class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()
    userId = serializers.CharField()

    def get_message(self):
        return self.data.get('message')

    def get_userId(self):
        return self.data.get('userId')

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedbacks
        fields = ('name', 'comment')

class ComplaintSerializer(serializers.Serializer):
    requestMessage = serializers.CharField(label='RequestMessage', max_length=500)
    responseMessage = serializers.CharField(label='ResponseMessage', max_length=2000)
    session_id = serializers.CharField(required=True)

    def create(self, validated_data):
        # Does not create new complaint if already exists
        sess = SessionTracker.objects.get(text_id=validated_data['session_id'])

        instance, created = Complaints.objects.get_or_create(requestMessage=validated_data['requestMessage'],\
        responseMessage=validated_data['responseMessage'],\
        session_id=sess)

        return instance
