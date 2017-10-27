from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from chatbot.serializers import (MessageSerializer,
    FeedbackSerializer, ComplaintSerializer)
from .models import (Feedbacks, Complaints, ClassTag, BanglaRequests, BanglaResponses, EnglishRequests, EnglishResponses)
from django.shortcuts import render, redirect
from django.utils.crypto import get_random_string
from .ContextualChatbotsWithTF.responderInterface import (response_message,
initAgents, trainEnglishAgent, trainBanglaAgent ,removeUser)

# Initialize Chatbots
initAgents()
users = []

def addUserId(userID):
    global users

    if userID not in users:
        users.append(userID)

def removeUserId(userID):
    global users

    if userID in users:
        users.remove(userID)

def userIdExists(userID):
    global users

    if userID in users:
        return True
    return False

def getUsers():
    global users
    return users

def getUniqueUser():
    users = getUsers()

    unique_id = get_random_string(length=32)

    while unique_id in users:
        unique_id = get_random_string(length=32)
    addUserId(unique_id)
    return unique_id

def chat(request):
    context = {}
    return render(request, 'chatbot/chatbot.html', context)

def deleteUserContext(userID):
    removeUser(userID)

    return

def respond_to_websockets(message):
    result_message = {
        'type': 'text'
    }
    result_message['text'] = response_message(message['text'], message['username'])

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
        query_response['userId'] = getUniqueUser()

        return Response(query_response)
    elif request.method == 'POST':
        serializer = MessageSerializer(data=request.data)

        if serializer.is_valid():
            if userIdExists(serializer.get_userId()):
                query_response['message'] = response_message(serializer.get_message(), serializer.get_userId())
            else:
                query_response['message'] = 'Incorrect user credential'

            return Response(query_response, status=status.HTTP_202_ACCEPTED)

@api_view(['GET', 'POST'])
def terminate_api(request):
    query_response = {'message': ''}

    if request.method == 'GET':
        return Response(query_response, status=status.HTTP_204_NO_CONTENT)
    elif request.method == 'POST':
        serializer = MessageSerializer(data=request.data)

        if serializer.is_valid():
            if userIdExists(serializer.get_userId()):
                removeUserId(serializer.get_userId())
                query_response['message'] = 'Successful Termination'
            else:
                query_response['message'] = 'Unsuccessful Termination'

            return Response(query_response, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(query_response, status=status.HTTP_405_METHOD_NOT_ALLOWED)


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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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

def complaintList(request):
    complaint_list = Complaints.objects.all()
    paginator = Paginator(complaint_list, 10)

    page = request.GET.get('page')
    try:
        complaints = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        complaints = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        complaints = paginator.page(paginator.num_pages)

    return render(request, 'chatbot/moderatorComplaints.html', {'complaint_list': complaints})

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
                else:
                    englishForm = EnglishTagForm()
                    context['eForm'] = englishForm
            elif "SubmitBundle" in request.POST:
                newTagForm = NewTagForm(request.POST)

                if newTagForm.is_valid():
                    tag, _ = ClassTag.objects.get_or_create(tagName=newTagForm.cleaned_data['new_tag'])
                    newMessage, _ = EnglishResponses.objects.get_or_create(responseMessage=newTagForm.cleaned_data['response'], tag=tag)
                    newPattern, _ = EnglishRequests.objects.get_or_create(requestMessage=complaint.requestMessage, tag=tag)

                    complaint.delete()
                    return redirect('chatbot:modComplaints')
                else:
                    newTagForm = NewTagForm()
                    context['newForm'] = newTagForm
        elif language == 1:
            banglaForm = BanglaTagForm(request.POST)

            if "SubmitTag" in request.POST:
                if banglaForm.is_valid:
                    tag = ClassTag.objects.get(tagName=banglaForm.data['tag'])
                    pattern, created = BanglaRequests.objects.get_or_create(requestMessage=complaint.requestMessage, tag=tag)
                    complaint.delete()
                    return redirect('chatbot:modComplaints')
                else:
                    banglaForm = BanglaTagForm()
                    context['bForm'] = banglaForm
            elif "SubmitBundle" in request.POST:
                newTagForm = NewTagForm(request.POST)

                if newTagForm.is_valid():
                    tag, _ = ClassTag.objects.get_or_create(tagName=newTagForm.cleaned_data['new_tag'])
                    newMessage, _ = BanglaResponses.objects.get_or_create(responseMessage=newTagForm.cleaned_data['response'], tag=tag)
                    newPattern, _ = BanglaRequests.objects.get_or_create(requestMessage=complaint.requestMessage, tag=tag)

                    complaint.delete()
                    return redirect('chatbot:modComplaints')
                else:
                    newTagForm = NewTagForm()
                    context['newForm'] = newTagForm
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

def feedbackView(request):
    feedback_list = Feedbacks.objects.all()
    paginator = Paginator(feedback_list, 5)

    page = request.GET.get('page')
    try:
        feedback = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        feedback = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        feedback = paginator.page(paginator.num_pages)

    return render(request, 'chatbot/feedbackList.html', {'feedbacks': feedback})

# Intents
from .intents import (updateBanglaIntents, updateEnglishIntents,
generateBanglaIntents, generateEnglishIntents)
import os, json
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

def updateEnglishFile(request):
    data = generateEnglishIntents()
    path = os.path.dirname(os.path.abspath('__file__'))
    path = os.path.join(path, 'chatbot', 'ContextualChatbotsWithTF', 'EnglishNLP', 'intents.json')

    try:
        with open(path, 'w') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        raise e
        return render(request, 'chatbot/intentFileStatus.html', {'status': 1})
    return render(request, 'chatbot/intentFileStatus.html', {'status': 0})

def updateBanglaFile(request):
    data = generateBanglaIntents()
    path = os.path.dirname(os.path.abspath('__file__'))
    path = os.path.join(path, 'chatbot', 'ContextualChatbotsWithTF', 'BanglaNLP', 'banglaintents.json')

    try:
        with open(path, 'w') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception:
        return render(request, 'chatbot/intentFileStatus.html', {'status': 1})
    return render(request, 'chatbot/intentFileStatus.html', {'status': 0})


# Training
def train_english(request):
    try:
        trainEnglishAgent()
    except Exception:
        return render(request, 'chatbot/trainStatus.html', {'status': 1})
    return render(request, 'chatbot/trainStatus.html', {'status': 0})



def train_bangla(request):
    try:
        trainBanglaAgent()
    except Exception:
        return render(request, 'chatbot/trainStatus.html', {'status': 1})
    return render(request, 'chatbot/trainStatus.html', {'status': 0})
