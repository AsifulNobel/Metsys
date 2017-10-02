from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from chatbot.serializers import (MessageSerializer,
    FeedbackSerializer, ComplaintSerializer)
from .models import Feedbacks, Complaints
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

def saveFeedback(feedbackMessage):
    feedback = Feedbacks(name=feedbackMessage['name'],\
        comment=feedbackMessage['comment'])
    feedback.save()

    return

def saveComplaint(complaintMessage):
    result_message = {}
    result_message['type'] = 'complaintSaveStatus'
    complaint, created = Complaints.objects.get_or_create(requestMessage=complaintMessage['userMessageText'], responseMessage=complaintMessage['botMessageText'])

    if not created:
        result_message['text'] = 'exists'
    else:
        result_message['text'] = 'success'

    return result_message

def deleteComplaint(complaintMessage):
    result_message = {}
    result_message['type'] = 'complaintDeleteStatus'
    try:
        complaint = Complaints.objects.get(requestMessage=complaintMessage['userMessageText'], responseMessage=complaintMessage['botMessageText'])

        complaint.delete()
        result_message['text'] = 'deleted'
    except Complaints.DoesNotExist:
        result_message['text'] = 'does not exist'

    return result_message


@api_view(['GET', 'POST'])
def message_api(request):
    query_response = {'message': ''}

    if request.method == 'GET':
        query_response['message'] = response_message('Hi')

        return Response(query_response)
    elif request.method == 'POST':
        serializer = MessageSerializer(data=request.data)

        if serializer.is_valid():
            query_response['message'] = response_message(serializer.get_message())

            return Response(query_response, status=status.HTTP_202_ACCEPTED)

@api_view(['GET', 'POST'])
def feedback_api(request):
    if request.method == 'GET':
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    elif request.method == 'POST':
        serializer = FeedbackSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(status=status.HTTP_202_ACCEPTED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
def complaint_save(request):
    if request.method == 'GET':
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    elif request.method == 'POST':
        serializer = ComplaintSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(status=status.HTTP_202_ACCEPTED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
def complaint_delete(request):
    if request.method == 'GET':
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    elif request.method == 'POST':
        serializer = ComplaintSerializer(data=request.data)

        if serializer.is_valid():
            try:
                complaint = Complaints.objects.get(
                requestMessage=request.data['requestMessage'],
                responseMessage=request.data['responseMessage'])

                complaint.delete()
            except Complaints.DoesNotExist:
                return Response(status=status.HTTP_204_NO_CONTENT)

            return Response(status=status.HTTP_202_ACCEPTED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
