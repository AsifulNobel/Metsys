from rest_framework import serializers
from .models import Feedbacks, Complaints

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

class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaints
        exclude = ('created',)

    def create(self, validated_data):
        # Does not create new complaint if already exists
        instance, created = Complaints.objects.get_or_create(requestMessage=validated_data['requestMessage'],\
        responseMessage=validated_data['responseMessage'],\
        session_id=validated_data['session_id'])

        return instance
