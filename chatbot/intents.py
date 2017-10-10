import json
import os
from .models import (BanglaRequests, BanglaResponses, EnglishRequests,
EnglishResponses, ClassTag)

DIR_NAME = os.path.dirname(os.path.abspath(__file__))
suffix_dir = 'ContextualChatbotsWithTF'

def generateBanglaIntents():
    """Generate Bangla Intents from database and return a dict"""
    data = {'intents': []}

    tags = ClassTag.objects.all()

    for tag in tags:
        temp = {}
        temp['tag'] = tag.tagName
        temp['patterns'] = []
        temp['responses'] = []

        for pattern in BanglaRequests.objects.filter(tag=tag):
            temp['patterns'].append(pattern.requestMessage)

        for response in BanglaResponses.objects.filter(tag=tag):
            temp['responses'].append(response.responseMessage)

        if len(temp['patterns']) > 0 and len(temp['responses']) > 0:
            data['intents'].append(temp)
    return data


def generateEnglishIntents():
    """Generate English Intents from database and return a dict"""
    data = {'intents': []}

    tags = ClassTag.objects.all()

    for tag in tags:
        temp = {}
        temp['tag'] = tag.tagName
        temp['patterns'] = []
        temp['responses'] = []

        for pattern in EnglishRequests.objects.filter(tag=tag):
            temp['patterns'].append(pattern.requestMessage)

        for response in EnglishResponses.objects.filter(tag=tag):
            temp['responses'].append(response.responseMessage)

        if len(temp['patterns']) > 0 and len(temp['responses']) > 0:
            data['intents'].append(temp)
    return data


def updateBanglaIntents():
    """Update database from banglaintents.json"""
    try:
        with open(os.path.join(DIR_NAME, suffix_dir, 'BanglaNLP', 'banglaintents.json'), 'r') as f:
            data = json.load(f)

            for bundle in data['intents']:
                tag, created = ClassTag.objects.get_or_create(tagName=bundle['tag'])

                for pattern in bundle['patterns']:
                    request, created = BanglaRequests.objects.get_or_create(requestMessage=pattern, tag=tag)

                for answer in bundle['responses']:
                    response, created = BanglaResponses.objects.get_or_create(responseMessage=answer, tag=tag)
    except FileNotFoundError:
        print('{} - {} not found'.format(__name__, os.path.join(DIR_NAME, suffix_dir, 'BanglaNLP', 'banglaintents.json')))
        return 1

    return 0

def updateEnglishIntents():
    try:
        with open(os.path.join(DIR_NAME, suffix_dir, 'EnglishNLP', 'intents.json'), 'r') as f:
            data = json.load(f)

            for bundle in data['intents']:
                tag, created = ClassTag.objects.get_or_create(tagName=bundle['tag'])

                for pattern in bundle['patterns']:
                    request, created = EnglishRequests.objects.get_or_create(requestMessage=pattern, tag=tag)

                for answer in bundle['responses']:
                    response, created = EnglishResponses.objects.get_or_create(responseMessage=answer, tag=tag)
    except FileNotFoundError:
        print('{} - {} not found'.format(__name__, os.path.join(DIR_NAME, suffix_dir, 'EnglishNLP', 'intents.json')))
        return 1

    return 0