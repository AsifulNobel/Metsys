from rest_framework import serializers

class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()
    userId = serializers.CharField()

    def get_message(self):
        return self.data.get('message')

    def get_userId(self):
        return self.data.get('userId')

class UserSerializer(serializers.Serializer):
    userId = serializers.CharField()

    def get_userId(self):
        return self.data.get('userId')
