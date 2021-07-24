from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import MessageSerializer, UserSerializer
from .ContextualChatbotsWithTF.responderInterface import (response_message,
initAgents, trainEnglishAgent, trainBanglaAgent ,removeUser, isEnglish)

# Create your views here.
initAgents()

@api_view(['GET', 'POST'])
def message_api(request):
    query_response = {'message': '',
        'userId': '',
        'tag': ''
    }

    if request.method == 'GET':
        query_response['message'], query_response['tag'] = response_message('Hi')

        return Response(query_response)
    elif request.method == 'POST':
        serializer = MessageSerializer(data=request.data)

        if serializer.is_valid():
            query_response['message'], query_response['tag'] = response_message(serializer.get_message(), serializer.get_userId())
        else:
            query_response['message'] = 'Incorrect user credential'

    return Response(query_response, status=status.HTTP_202_ACCEPTED)

@api_view(['GET', 'POST'])
def remove_user(request):
    query_response = {'message': ''}

    if request.method == 'GET':
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    elif request.method == 'POST':
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            removeUser(serializer.get_userId())

            query_response['message'] = 'Successfully removed context of user:'+serializer.get_userId()
        else:
            query_response['message'] = 'Incorrect JSON format'

    return Response(query_response, status=status.HTTP_202_ACCEPTED)

@api_view(['GET'])
def train_english_chowdhury(request):
    query_response = {'message': ''}

    if request.method == 'GET':
        try:
            trainEnglishAgent()

            query_response['message'] = "Successful Training of Chowdhury Bot English Agent"
        except Exception:
            query_response['message'] = "Unsuccessful Training of Chowdhury Bot English Agent"

    return Response(query_response, status=status.HTTP_202_ACCEPTED)

@api_view(['GET'])
def train_bangla_chowdhury(request):
    query_response = {'message': ''}

    if request.method == 'GET':
        try:
            trainBanglaAgent()

            query_response['message'] = "Successful Training of Chowdhury Bot Bangla Agent"
        except Exception:
            query_response['message'] = "Unsuccessful Training of Chowdhury Bot Bangla Agent"

    return Response(query_response, status=status.HTTP_202_ACCEPTED)
