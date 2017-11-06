from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from chatbot.serializers import (MessageSerializer,
    FeedbackSerializer, ComplaintSerializer)
from .models import (Feedbacks, Complaints, ClassTag, BanglaRequests, BanglaResponses, EnglishRequests, EnglishResponses, Agent, SessionTracker,
Message, TagAccessHistory)
from django.shortcuts import render, redirect
from django.utils.crypto import get_random_string
from .ContextualChatbotsWithTF.responderInterface import (response_message,
initAgents, trainEnglishAgent, trainBanglaAgent ,removeUser, isEnglish)
import logging

# Initialize Chatbots
initAgents()

logger = logging.getLogger(__name__)

def addUserId(userID):
    temp = SessionTracker(text_id=userID)
    temp.save()

def removeUserId(userID):
    tempSessionObj = SessionTracker.objects.get(text_id=userID)

    if not tempSessionObj.message_set.count() > 0:
        tempSessionObj.delete()

def userIdExists(userID):
    if SessionTracker.objects.filter(text_id=userID).exists():
        return True
    return False

def getUniqueUser():
    unique_id = get_random_string(length=32)

    while userIdExists(unique_id):
        unique_id = get_random_string(length=32)
    addUserId(unique_id)
    return unique_id

def addMessage(text, sessionId):
    if len(text) > 0:
        if userIdExists(sessionId):
            temp = Message(text=text, session_id=SessionTracker.objects.get(text_id=sessionId))
            temp.save()

def addTagAccess(tag, sessionId):
    if len(tag) > 0:
        en = 'english'
        bn = 'bangla'
        remove = ""

        if en in tag:
            remove= en
            tempAgent = Agent.objects.get(name="English Chowdhury")
        elif bn in tag:
            remove= bn
            tempAgent = Agent.objects.get(name="Bangla Chowdhury")
        tagParts = tag.split('_')
        removeIndex = tagParts.index(remove)
        tag = "_".join(tagParts[removeIndex+1:])
        tempTag = ClassTag.objects.get(tagName=tag, agentId=tempAgent)
        tempSessionObj = SessionTracker.objects.get(text_id=sessionId)

        tempAccess = TagAccessHistory(session_id=tempSessionObj, tag=tempTag)
        tempAccess.save()


def chat(request):
    context = {}
    banglaAgent, _ = Agent.objects.get_or_create(name="Bangla Chowdhury")
    englishAgent, _ = Agent.objects.get_or_create(name="English Chowdhury")

    context['bangla_topics'] = list(banglaAgent.classtag_set.values_list('tagName',flat=True))
    context['english_topics'] = list(englishAgent.classtag_set.values_list('tagName',flat=True))

    return render(request, 'chatbot/chatbot.html', context)

def deleteUserContext(userID):
    removeUser(userID)

    return

def respond_to_websockets(message):
    english = False
    if isEnglish(message['text']):
        english = True

    addMessage(message['text'], message['username'])

    result_message = {
        'type': 'text'
    }
    result_message['text'], result_message['tag'] = response_message(message['text'], message['username'])

    addMessage(result_message['text'], message['username'])
    addTagAccess(result_message['tag'], message['username'])

    return result_message

def saveFeedback(feedbackMessage):
    feedback = Feedbacks(name=feedbackMessage['name'],\
        comment=feedbackMessage['comment'])
    feedback.save()

    return

def saveComplaint(complaintMessage):
    logger.debug(complaintMessage.keys())

    result_message = {}
    result_message['type'] = 'complaintSaveStatus'
    complaint, created = Complaints.objects.get_or_create(requestMessage=complaintMessage['messagePair']['userMessageText'], responseMessage=complaintMessage['messagePair']['botMessageText'], session_id=SessionTracker.objects.get(text_id=complaintMessage['username']))

    if not created:
        result_message['text'] = 'exists'
    else:
        result_message['text'] = 'success'

    return result_message


@api_view(['GET', 'POST'])
def message_api(request):
    query_response = {'message': '',
        'userId': '',
        'tag': ''
    }

    if request.method == 'GET':
        query_response['message'], query_response['tag'] = response_message('Hi')
        query_response['userId'] = getUniqueUser()

        return Response(query_response)
    elif request.method == 'POST':
        serializer = MessageSerializer(data=request.data)

        if serializer.is_valid():
            addMessage(serializer.get_message(), serializer.get_userId())

            query_response['message'], query_response['tag'] = response_message(serializer.get_message(), serializer.get_userId())

            addMessage(query_response['message'], serializer.get_userId())
            addTagAccess(query_response['tag'], serializer.get_userId())
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
import datetime
from .forms import (LoginForm, EnglishTagForm, BanglaTagForm, NewTagForm,
DurationForm)

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
    complaint_list = Complaints.objects.all().order_by('-created')
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
        if "Duration" in request.POST:
            durationForm = DurationForm(request.POST)

            if durationForm.is_valid:
                duration = durationForm.data['duration']
                duration = int(duration)

                messageList = Message.objects.filter(session_id=complaint.session_id).order_by('timestamp')
                listLength = len(messageList)
                complaintMessageIndex = 0

                if listLength > 6:
                    for index, tempMessage in enumerate(messageList):
                        if complaint.requestMessage == tempMessage.text:
                            complaintMessageIndex = index

                if not (complaintMessageIndex - duration > 0):
                    duration += (complaintMessageIndex - duration)

                if duration % 2 != 0:
                    duration += 1

                if complaintMessageIndex == 0:
                    messageList = messageList[:2]
                elif complaintMessageIndex >= 2 and complaintMessageIndex < 6:
                    messageList = messageList[:6]
                else:
                    messageList = messageList[complaintMessageIndex-duration:complaintMessageIndex+2]

                context['recentMessages'] = messageList
                context['dForm'] = durationForm
            else:
                durationForm = DurationForm()
                context['dForm'] = durationForm
        else:
            durationForm = DurationForm()
            context['dForm'] = durationForm

        if language == 0:
            agent = Agent.objects.get(name="English Chowdhury")

            if "SubmitTag" in request.POST:
                englishForm = EnglishTagForm(request.POST)

                if englishForm.is_valid:
                    tag = ClassTag.objects.get(pk=englishForm.data['tag'])
                    pattern, created = EnglishRequests.objects.get_or_create(requestMessage=complaint.requestMessage, tag=tag)
                    complaint.delete()
                    return redirect('chatbot:modComplaints')
                else:
                    englishForm = EnglishTagForm()
                    context['eForm'] = englishForm
            elif "SubmitBundle" in request.POST:
                newTagForm = NewTagForm(request.POST)

                if newTagForm.is_valid():
                    tag, _ = ClassTag.objects.get_or_create(tagName=newTagForm.cleaned_data['new_tag'], agentId=agent)
                    newMessage, _ = EnglishResponses.objects.get_or_create(responseMessage=newTagForm.cleaned_data['response'], tag=tag)
                    newPattern, _ = EnglishRequests.objects.get_or_create(requestMessage=complaint.requestMessage, tag=tag)

                    complaint.delete()
                    return redirect('chatbot:modComplaints')
                else:
                    newTagForm = NewTagForm()
                    context['newForm'] = newTagForm
            else:
                englishForm = EnglishTagForm()
                context['eForm'] = englishForm
                newTagForm = NewTagForm()
                context['newForm'] = newTagForm
        elif language == 1:
            agent = Agent.objects.get(name="Bangla Chowdhury")

            if "SubmitTag" in request.POST:
                banglaForm = BanglaTagForm(request.POST)

                if banglaForm.is_valid:
                    tag = ClassTag.objects.get(tagName=banglaForm.data['tag'], agentId=agent)
                    pattern, created = BanglaRequests.objects.get_or_create(requestMessage=complaint.requestMessage, tag=tag)
                    complaint.delete()
                    return redirect('chatbot:modComplaints')
                else:
                    banglaForm = BanglaTagForm()
                    context['bForm'] = banglaForm
            elif "SubmitBundle" in request.POST:
                newTagForm = NewTagForm(request.POST)

                if newTagForm.is_valid():
                    tag, _ = ClassTag.objects.get_or_create(tagName=newTagForm.cleaned_data['new_tag'], agentId=agent)
                    newMessage, _ = BanglaResponses.objects.get_or_create(responseMessage=newTagForm.cleaned_data['response'], tag=tag)
                    newPattern, _ = BanglaRequests.objects.get_or_create(requestMessage=complaint.requestMessage, tag=tag)

                    complaint.delete()
                    return redirect('chatbot:modComplaints')
                else:
                    newTagForm = NewTagForm()
                    context['newForm'] = newTagForm
            else:
                banglaForm = BanglaTagForm()
                context['bForm'] = banglaForm
                newTagForm = NewTagForm()
                context['newForm'] = newTagForm
    else:
        messageList = Message.objects.filter(session_id=complaint.session_id).order_by('timestamp')
        listLength = len(messageList)
        complaintMessageIndex = 0

        if listLength > 6:
            for index, tempMessage in enumerate(messageList):
                if complaint.requestMessage == tempMessage.text:
                    complaintMessageIndex = index
        if complaintMessageIndex == 0:
            messageList = messageList[:2]
        elif complaintMessageIndex >= 2 and complaintMessageIndex < 6:
            messageList = messageList[:complaintMessageIndex+2]
        else:
            messageList = messageList[complaintMessageIndex-4:complaintMessageIndex+2]

        context['recentMessages'] = messageList

        if language == 0:
            englishForm = EnglishTagForm()
            context['eForm'] = englishForm
        elif language == 1:
            banglaForm = BanglaTagForm()
            context['bForm'] = banglaForm
        newTagForm = NewTagForm()
        context['newForm'] = newTagForm
        durationForm = DurationForm()
        context['dForm'] = durationForm

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

def statsView(request):
    context = {}
    context['messageCount'] = Message.objects.all().count()
    context['sessionCount'] = SessionTracker.objects.all().count()
    context['complaintCount'] = Complaints.objects.all().count()
    context['tagAccess'] = []

    totalMessages = 0
    totalComplaints = 0
    for temp in SessionTracker.objects.all():
        totalMessages += temp.message_set.count()
        totalComplaints += temp.complaints_set.count()
    context['averageMessageCount'] = totalMessages // context['sessionCount']
    context['averageComplaintCount'] = totalComplaints // context['sessionCount']
    context['uniqueTagAccessCount'] = 0

    for tag in ClassTag.objects.all().order_by('tagName'):
        tempCount = tag.tagaccesshistory_set.count()

        if tag.agentId:
            context['tagAccess'].append((tag.tagName, tempCount, tag.agentId.name))
        else:
            context['tagAccess'].append((tag.tagName, tempCount, 'Unreferenced'))

        if tempCount > 0:
            context['uniqueTagAccessCount'] += 1

    return render(request, 'chatbot/moderatorStats.html', context)

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

def viewLog(request):
    path = os.path.dirname(os.path.abspath('__file__'))
    path = os.path.join(path, 'nohup.out')
    content = ''
    try:
        with open(path, 'r') as f:
            content = tail(f, 300)
    except Exception as e:
        content = 'No file found!'
        logger.debug("{}".format(e))
    return HttpResponse(content, content_type='text/plain; charset=utf-8')

def downloadLog(request):
    path = os.path.dirname(os.path.abspath('__file__'))
    path = os.path.join(path, 'nohup.out')
    content = ''
    response = None

    try:
        with open(path, 'r') as f:
            content = f.read()
            response = HttpResponse(content, content_type='text/plain; charset=utf-8')
            response['Content-Disposition'] = 'attachment; filename=nohup.out'

        return response
    except Exception as e:
        content = 'No file found!'

    return HttpResponse(content, content_type='text/plain')

def tail(f, lines=100, _buffer=4098):
    """Tail a file and get X lines from the end"""
    # place holder for the lines found
    lines_found = []

    # block counter will be multiplied by buffer
    # to get the block size from the end
    block_counter = -1

    # loop until we find X lines
    while len(lines_found) < lines:
        try:
            f.seek(block_counter * _buffer, os.SEEK_END)
        except IOError:  # either file is too small, or too many lines requested
            f.seek(0)
            lines_found = f.readlines()
            break

        lines_found = f.readlines()
        # decrement the block counter to get the
        # next X bytes
        block_counter -= 1

    return lines_found[-lines:]
