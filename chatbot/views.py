from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from chatbot.serializers import (MessageSerializer,
    FeedbackSerializer, ComplaintSerializer)
from .models import Feedbacks, Complaints
from django.shortcuts import render, redirect
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

# Authentication
from django.shortcuts import HttpResponse
from django.contrib.auth import authenticate, login
from django.views import generic
from django.utils import timezone
from .forms import LoginForm

def moderator_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            cleanData = form.cleaned_data
            user = authenticate(username=cleanData['userName'],
                                password=cleanData['password'])

            if user is not None:
                if user.is_active:
                    login(request, user)

                    return redirect('chatbot:modHome')
                else:
                    # Use custom page
                    return redirect('chatbot:modLogin')
            else:
                # Use custom page
                return redirect('chatbot:modLogin')
        else:
            form = LoginForm()
    else:
        form = LoginForm()
    return render(request, 'chatbot/login.html', {'form': form})


def moderator_home(request):
    return render(request, 'chatbot/moderatorHome.html', {'user': request.user})

class ComplaintsView(generic.ListView):
    template_name = 'chatbot/moderatorComplaints.html'
    context_object_name = 'complaints_list'

    def get_queryset(self):
        """Return all complaints."""
        return Complaints.objects.all()

def complaintDetail(request, complaint_id):
    complaint = Complaints.objects.filter(pk=complaint_id).first()
    context = {'complaint': complaint}
    return render(request, 'chatbot/complaintDetail.html', context)


# Intents
from .intents import (updateBanglaIntents, updateEnglishIntents,
generateBanglaIntents, generateEnglishIntents)
import os
from django.http import HttpResponse, JsonResponse

def englishIntentAdd(request):
    status = updateEnglishIntents()
    return render(request, 'chatbot/intentSuccess.html', {'status': status, 'language': "english"})


def banglaIntentAdd(request):
    status = updateBanglaIntents()
    return render(request, 'chatbot/intentSuccess.html', {'status': status, 'language': "bangla"})

def englishIntentDownload(request):
    data = generateEnglishIntents()

    if data:
        response = JsonResponse(data, json_dumps_params={'indent': 4})
        response['Content-Disposition'] = 'attachment; filename=intents.json'
        return response
    else:
        return HttpResponse('<h1>Data Does Not Exist</h1>')


def banglaIntentDownload(request):
    data = generateBanglaIntents()

    if data:
        response = JsonResponse(data, json_dumps_params={'indent': 4,
        'ensure_ascii': False}) # For Unicode Preservation
        response['Content-Disposition'] = 'attachment; filename=banglaintents.json'
        return response
    else:
        return HttpResponse('<h1>Data Does Not Exist</h1>')
