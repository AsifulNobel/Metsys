import requests

URL = 'http://127.0.0.1:8005'

def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

def getDefaultResponse(message):
    DEFAULT_MESSAGE = 'Chatbot under maintanenace. Please try again after a few minutes'
    DEFAULT_TAG = 'default'

    if isEnglish(message):
        tag = 'english_' + DEFAULT_TAG
    else:
        tag = 'bangla_' + DEFAULT_TAG

    return (DEFAULT_MESSAGE, tag)

def response_message(message, userID='123'):
    response = None
    payload = {
        "message": message,
        "userId": userID
    }

    try:
        request = requests.post(URL+'/tensor/chatbot/message', json=payload)

        if request.status_code == 202:
             response = request.json()

             return (response['message'], response['tag'])
        else:
            return getDefaultResponse(message)

    except requests.exceptions.ConnectionError:
        return getDefaultResponse(message)

def initAgents():
    pass

def trainEnglishAgent():
    pass

def trainBanglaAgent():
    pass

def removeUser(userID):
    pass
