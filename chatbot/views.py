from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from chatbot.serializers import MessageSerializer
from django.shortcuts import render
from .ContextualChatbotsWithTF.responderInterface import response_message


def chat(request):
    context = {}
    return render(request, 'chatbot/chatbot.html', context)


def respond_to_websockets(message):
    result_message = {
        'type': 'text'
    }
    result_message['text'] = response_message(message['text'])

    return result_message


@api_view(['GET', 'POST'])
def api(request):
    query_response = {'message': ''}

    if request.method == 'GET':
        query_response['message'] = response_message('Hi')

        return Response(query_response)
    elif request.method == 'POST':
        serializer = MessageSerializer(data=request.data)

        if serializer.is_valid():
            query_response['message'] = response_message(serializer.get_message())

            return Response(query_response, status=status.HTTP_202_ACCEPTED)
