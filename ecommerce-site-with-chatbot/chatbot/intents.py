import json
import os
from .models import (BanglaRequests, BanglaResponses, EnglishRequests,
EnglishResponses, ClassTag, Agent, ContextMethod, Context)

def getDirName(path, depth):
    while depth > 0:
        path = os.path.dirname(path)
        depth = depth - 1
    return path

DIR_NAME = getDirName(os.path.abspath(__file__), 3)
suffix_dir = 'ContextualChatbotsWithTF'

def generateBanglaIntents():
    """Generate Bangla Intents from database and return a dict"""
    data = {'intents': []}

    agent, _ = Agent.objects.get_or_create(name="Bangla Chowdhury")
    tags = ClassTag.objects.filter(agentId=agent)
    filterMethod = ContextMethod.objects.get(methodName='filter')
    setMethod = ContextMethod.objects.get(methodName='set')

    for tag in tags:
        temp = {}
        temp['tag'] = tag.tagName
        temp['patterns'] = []
        temp['responses'] = []
        temp['context_filter'] = []
        temp['context_set'] = ''

        for pattern in BanglaRequests.objects.filter(tag=tag):
            temp['patterns'].append(pattern.requestMessage)

        for response in BanglaResponses.objects.filter(tag=tag):
            temp['responses'].append(response.responseMessage)

        for context in Context.objects.filter(contextParent=tag).filter(contextMethod=filterMethod):
            temp['context_filter'].append(context.contextClass.tagName)

        context = Context.objects.filter(contextParent=tag).filter(contextMethod=setMethod)

        if len(context) > 0:
            temp['context_set'] = context[0].contextClass.tagName

        if len(temp['context_set']) == 0:
            temp.pop('context_set')

        if len(temp['context_filter']) == 0:
            temp.pop('context_filter')

        if len(temp['patterns']) > 0 and len(temp['responses']) > 0:
            data['intents'].append(temp)
    return data


def generateEnglishIntents():
    """Generate English Intents from database and return a dict"""
    data = {'intents': []}

    agent, _ = Agent.objects.get_or_create(name="English Chowdhury")
    tags = ClassTag.objects.filter(agentId=agent)
    filterMethod = ContextMethod.objects.get(methodName='filter')
    setMethod = ContextMethod.objects.get(methodName='set')

    for tag in tags:
        temp = {}
        temp['tag'] = tag.tagName
        temp['patterns'] = []
        temp['responses'] = []
        temp['context_filter'] = []
        temp['context_set'] = ''

        for pattern in EnglishRequests.objects.filter(tag=tag):
            temp['patterns'].append(pattern.requestMessage)

        for response in EnglishResponses.objects.filter(tag=tag):
            temp['responses'].append(response.responseMessage)

        for context in Context.objects.filter(contextParent=tag).filter(contextMethod=filterMethod):
            temp['context_filter'].append(context.contextClass.tagName)

        context = Context.objects.filter(contextParent=tag).filter(contextMethod=setMethod)

        if len(context) > 0:
            temp['context_set'] = context[0].contextClass.tagName

        if len(temp['context_set']) == 0:
            temp.pop('context_set')

        if len(temp['context_filter']) == 0:
            temp.pop('context_filter')

        if len(temp['patterns']) > 0 and len(temp['responses']) > 0:
            data['intents'].append(temp)
    return data


def updateBanglaIntents():
    """Update database from banglaintents.json"""
    try:
        with open(os.path.join(DIR_NAME, 'chatbot-admin', 'tensor_model', suffix_dir, 'BanglaNLP', 'banglaintents.json'), 'r') as f:
            data = json.load(f)

            agent, _ = Agent.objects.get_or_create(name="Bangla Chowdhury")

            for bundle in data['intents']:
                tag, _ = ClassTag.objects.get_or_create(tagName=bundle['tag'], agentId=agent)

                for pattern in bundle['patterns']:
                    request, _ = BanglaRequests.objects.get_or_create(requestMessage=pattern, tag=tag)

                for answer in bundle['responses']:
                    response, _ = BanglaResponses.objects.get_or_create(responseMessage=answer, tag=tag)

                if bundle.get('context_filter', None):
                    if len(bundle['context_filter']) > 0:
                        contextMethodObject, _ = ContextMethod.objects.get_or_create(methodName='filter')

                        for filterTag in bundle['context_filter']:
                            filterTagObject, _ = ClassTag.objects.get_or_create(tagName=filterTag, agentId=agent)

                            context, _ = Context.objects.get_or_create(contextClass=filterTagObject, contextMethod=contextMethodObject, contextParent=tag)

                if bundle.get('context_set', None):
                    contextMethodObject, _ = ContextMethod.objects.get_or_create(methodName='set')

                    setTagObject, _ = ClassTag.objects.get_or_create(tagName=bundle['context_set'], agentId=agent)

                    context, _ = Context.objects.get_or_create(contextClass=setTagObject, contextMethod=contextMethodObject, contextParent=tag)
    except FileNotFoundError:
        print('{} - {} not found'.format(__name__, os.path.join(DIR_NAME, 'chatbot-admin', 'tensor_model', suffix_dir, 'BanglaNLP', 'banglaintents.json')))
        return 1

    return 0

def updateEnglishIntents():
    try:
        with open(os.path.join(DIR_NAME, 'chatbot-admin', 'tensor_model', suffix_dir, 'EnglishNLP', 'intents.json'), 'r') as f:
            data = json.load(f)

            agent, _ = Agent.objects.get_or_create(name="English Chowdhury")

            for bundle in data['intents']:
                tag, _ = ClassTag.objects.get_or_create(tagName=bundle['tag'], agentId=agent)

                for pattern in bundle['patterns']:
                    request, _ = EnglishRequests.objects.get_or_create(requestMessage=pattern, tag=tag)

                for answer in bundle['responses']:
                    response, _ = EnglishResponses.objects.get_or_create(responseMessage=answer, tag=tag)

                if bundle.get('context_filter', None):
                    if len(bundle['context_filter']) > 0:
                        contextMethodObject, _ = ContextMethod.objects.get_or_create(methodName='filter')

                        for filterTag in bundle['context_filter']:
                            filterTagObject, _ = ClassTag.objects.get_or_create(tagName=filterTag, agentId=agent)

                            context, _ = Context.objects.get_or_create(contextClass=filterTagObject, contextMethod=contextMethodObject, contextParent=tag)

                if bundle.get('context_set', None):
                    contextMethodObject, _ = ContextMethod.objects.get_or_create(methodName='set')

                    setTagObject, _ = ClassTag.objects.get_or_create(tagName=bundle['context_set'], agentId=agent)

                    context, _ = Context.objects.get_or_create(contextClass=setTagObject, contextMethod=contextMethodObject, contextParent=tag)
    except FileNotFoundError:
        print('{} - {} not found'.format(__name__, os.path.join(DIR_NAME, 'chatbot-admin', 'tensor_model', suffix_dir, 'EnglishNLP', 'intents.json')))
        return 1

    return 0
