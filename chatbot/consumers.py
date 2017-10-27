import json
from channels import Channel
from channels.sessions import enforce_ordering, channel_session
from .views import (respond_to_websockets, saveFeedback, saveComplaint,
deleteUserContext, getUniqueUser, removeUserId)

@channel_session
@enforce_ordering
def ws_connect(message):
    # Initialise their session
    payload = {
        'accept': True,
    }

    message.channel_session['username'] = getUniqueUser()
    message.reply_channel.send(payload)


# Unpacks the JSON in the received WebSocket frame and puts it onto a channel
# of its own with a few attributes extra so we can route it
# we preserve message.reply_channel (which that's based on)
@channel_session
@enforce_ordering
def ws_receive(message):
    # All WebSocket frames have either a text or binary payload; we decode the
    # text part here assuming it's JSON.
    # You could easily build up a basic framework that did this
    # encoding/decoding
    # for you as well as handling common errors.
    payload = json.loads(message['text'])
    payload['reply_channel'] = message.content['reply_channel']
    payload['username'] = message.channel_session['username']
    Channel("chat.receive").send(payload)

@channel_session
@enforce_ordering
def ws_disconnect(message):
    # Unsubscribe from any connected rooms
    print(message.channel_session['username'])
    removeUser(message.channel_session['username'])
    print(users)


# Chat channel handling ###
def chat_start(message):
    pass

def chat_leave(message):
    pass

def chat_send(message):
    response = respond_to_websockets(message)

    # Reformat the response and send it to the html to print
    response['source'] = 'BOT'
    message.reply_channel.send({
        'text': json.dumps(response)
    })

def feedback_send(feedbackMessage):
    saveFeedback(feedbackMessage)

def complaint_save(complaintMessage):
    response = saveComplaint(complaintMessage['messagePair'])

    complaintMessage.reply_channel.send({
        'text': json.dumps(response)
    })

def removeUser(userId):
    removeUserId(userId)
    deleteUserContext(userId)
