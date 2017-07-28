from rest_framework import serializers

class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()

    def get_message(self):
        return self.data.get('message')
