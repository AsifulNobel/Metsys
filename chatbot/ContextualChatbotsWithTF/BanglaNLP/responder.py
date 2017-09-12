import numpy as np
import tflearn
import tensorflow as tf
import random
import pickle
import json
import os
import logging
import nltk
from .stemming_bn import isEnglish, stemBanglaWord
# from stemming_bn import isEnglish, stemBanglaWord

DIR_NAME = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger(__name__)

data = pickle.load(open(os.path.join(DIR_NAME, "training_data"), "rb"))
words = data['words']
classes = data['classes']
train_x = data['train_x']
train_y = data['train_y']

with open(os.path.join(DIR_NAME, 'banglaintents.json')) as json_data:
    # print("Loading Intents...")
    print("Loading Intents...")
    intents = json.load(json_data)

# load our saved model
print("Loading Model...")
# logger.info("Loading Model...")

# Clears the default graph stack and resets the global default graph
tf.reset_default_graph()
net = tflearn.input_data(shape=[None, len(train_x[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(train_y[0]), activation='softmax')
net = tflearn.regression(net)
model = tflearn.DNN(net, tensorboard_dir='tflearn_logs')

DIR_NAME_MODEL = os.path.dirname(os.path.abspath('__file__'))
model.load(DIR_NAME_MODEL+'/chatbot/ContextualChatbotsWithTF/BanglaNLP/model.tflearn')
# model.load('model.tflearn')
# model.load('./chatbot/ContextualChatbotsWithTF/BanglaNLP/model.tflearn')

ERROR_THRESHOLD = 0.25

def clean_up_sentence(sentence):
    print("Input Sentence:", sentence)

    sentence_words = nltk.word_tokenize(sentence)
    print("\nTokenized words:", sentence_words)

    # stem each word
    sentence_words = [stemBanglaWord(word) for word in sentence_words]
    print("\nStemmed words:", sentence_words)
    return sentence_words

def bow(sentence, words, show_details=False):
    print("\nTraining words:", words)
    print("\nClasses:", classes)
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)

    # bag of words
    bag = [0]*len(words)
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    print("BOW output:", np.array(bag))
    return(np.array(bag))

def classify(sentence):
    # generate probabilities from the model
    results = model.predict([bow(sentence, words)])[0]

    print("\nNeural Net result:", results)
    # filter out predictions below a threshold
    results = [[i,r] for i,r in enumerate(results) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append((classes[r[0]], r[1]))
    # return tuple of intent and probability

    print("\nIntent and probability:", return_list)
    return return_list

def response_message(sentence, userID='123', show_details=False):
    global intents
    global model

    results = classify(sentence)

    # if we have a classification then find the matching intent tag
    if results:
        # loop as long as there are matches to process
        while results:
            for i in intents['intents']:
                # find a tag matching the first result
                if i['tag'] == results[0][0]:
                    # a random response from the intent
                    return random.choice(i['responses'])
            results.pop(0)
