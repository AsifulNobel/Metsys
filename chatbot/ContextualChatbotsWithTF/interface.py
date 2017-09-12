from .BanglaNLP.responder import response_message as banglaMessage
from .EnglishNLP.testingModel import response_message as englishMessage

def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

def response_message(message):
    if isEnglish(message):
        print("English Message found, passing to english agent")
        return englishMessage(message)
    else:
        print("Bangla Message found, passing to bangla agent")
        return banglaMessage(message)
