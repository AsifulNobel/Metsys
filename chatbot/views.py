from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from chatbot.serializers import (MessageSerializer,
    FeedbackSerializer, ComplaintSerializer)
from .models import (Feedbacks, Complaints, ClassTag, BanglaRequests, BanglaResponses, EnglishRequests, EnglishResponses)
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

# Authentication
from django.shortcuts import HttpResponse
from django.contrib.auth import authenticate, login
from django.views import generic
from django.utils import timezone
from .forms import (LoginForm, EnglishTagForm, BanglaTagForm, NewTagForm)

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
        if request.user.is_authenticated():
            return redirect('chatbot:modHome')
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
    context = {}

    try:
        complaint.requestMessage.encode(encoding='utf-8').decode('ascii')
        language = 0
    except UnicodeDecodeError:
        language = 1

    if request.method == 'POST':
        if language == 0:
            if "SubmitTag" in request.POST:
                englishForm = EnglishTagForm(request.POST)

                if englishForm.is_valid:
                    tag = ClassTag.objects.get(tagName=englishForm.data['tag'])
                    pattern, created = EnglishRequests.objects.get_or_create(requestMessage=complaint.requestMessage, tag=tag)
                    complaint.delete()
                    return redirect('chatbot:modComplaints')
            elif "SubmitBundle" in request.POST:
                newTagForm = NewTagForm(request.POST)

                if newTagForm.is_valid():
                    tag, _ = ClassTag.objects.get_or_create(tagName=newTagForm.cleaned_data['tag'])
                    newMessage, _ = EnglishResponses.objects.get_or_create(responseMessage=newTagForm.cleaned_data['response'], tag=tag)
                    newPattern, _ = EnglishRequests.objects.get_or_create(requestMessage=complaint.requestMessage, tag=tag)

                    complaint.delete()
                    return redirect('chatbot:modComplaints')
        elif language == 1:
            banglaForm = BanglaTagForm(request.POST)

            if "SubmitTag" in request.POST:
                if banglaForm.is_valid:
                    tag = ClassTag.objects.get(tagName=banglaForm.data['tag'])
                    pattern, created = BanglaRequests.objects.get_or_create(requestMessage=complaint.requestMessage, tag=tag)
                    complaint.delete()
                    return redirect('chatbot:modComplaints')
            elif "SubmitBundle" in request.POST:
                newTagForm = NewTagForm(request.POST)

                if newTagForm.is_valid():
                    tag, _ = ClassTag.objects.get_or_create(tagName=newTagForm.cleaned_data['tag'])
                    newMessage, _ = BanglaResponses.objects.get_or_create(responseMessage=newTagForm.cleaned_data['response'], tag=tag)
                    newPattern, _ = BanglaRequests.objects.get_or_create(requestMessage=complaint.requestMessage, tag=tag)

                    complaint.delete()
                    return redirect('chatbot:modComplaints')
    else:
        if language == 0:
            englishForm = EnglishTagForm()
            context['eForm'] = englishForm
        elif language == 1:
            banglaForm = BanglaTagForm()
            context['bForm'] = banglaForm
        newTagForm = NewTagForm()
        context['newForm'] = newTagForm
    context['complaint'] = complaint
    return render(request, 'chatbot/complaintDetail.html', context)

def complaint_delete(request, complaint_id):
    complaint = Complaints.objects.get(pk=complaint_id)

    if complaint:
        complaint.delete()
        return redirect('chatbot:modComplaints')
    else:
        return HttpResponse("<h1>Why u tryna delete what's not there!</h1>")


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
