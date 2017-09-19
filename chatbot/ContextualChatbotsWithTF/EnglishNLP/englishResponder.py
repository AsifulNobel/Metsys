import numpy as np
import tflearn
import tensorflow as tf
import random
import pickle
import json
import nltk
from nltk.stem.lancaster import LancasterStemmer
import os
import logging
from .timethis import timethis

DIR_NAME = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger(__name__)

stemmer = LancasterStemmer()

data = pickle.load(open(os.path.join(DIR_NAME, "training_data"), "rb"))
words = data['words']
classes = data['classes']
train_x = data['train_x']
train_y = data['train_y']

with open(os.path.join(DIR_NAME, 'intents.json')) as json_data:
    logger.info("Loading Intents...")
    intents = json.load(json_data)

# load our saved model
logger.info("Loading Model...")

# Clears the default graph stack and resets the global default graph
tf.reset_default_graph()
net = tflearn.input_data(shape=[None, len(train_x[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(train_y[0]), activation='softmax')
net = tflearn.regression(net)
model = tflearn.DNN(net, tensorboard_dir='tflearn_logs')

DIR_NAME_MODEL = os.path.dirname(os.path.abspath('__file__'))
model.load(DIR_NAME_MODEL+'/chatbot/ContextualChatbotsWithTF/EnglishNLP/model.tflearn')
# model.load('model.tflearn')

context = {}

ERROR_THRESHOLD = 0.25

@timethis
def clean_up_sentence(sentence):
    logger.debug("Input Sentence: {}".format(sentence))

    # tokenize the pattern
    sentence_words = nltk.word_tokenize(sentence)
    logger.debug("Tokenized words: {}".format(sentence_words))
    # stem each word
    sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
    logger.debug("Stemmed words: {}".format(sentence_words))
    return sentence_words

@timethis
def bow(sentence, words, show_details=False):
    logger.debug("Training words: {}".format(words))
    logger.debug("Classes: {}".format(classes))
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)

    # bag of words
    bag = [0]*len(words)
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    logger.debug("Found in bag: %s" % w)
    logger.debug("BOW output: {}".format(np.array(bag)))
    return(np.array(bag))

@timethis
def classify(sentence):
    # generate probabilities from the model
    results = model.predict([bow(sentence, words)])[0]

    logger.debug("Neural Net result: {}".format(results))
    # filter out predictions below a threshold
    results = [[i,r] for i,r in enumerate(results) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append((classes[r[0]], r[1]))
    # return tuple of intent and probability

    logger.debug("Intent and probability: {}".format(return_list))
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
                    # set context for this intent if necessary
                    if 'context_set' in i:
                        if show_details:
                            logger.debug('context:'.format(i['context_set']))
                        context[userID] = i['context_set']

                    # check if this intent is contextual and applies to this user's conversation
                    if not 'context_filter' in i or \
                        (userID in context and 'context_filter' in i and i['context_filter'] == context[userID]):

                        if show_details:
                            logger.debug('tag:', i['tag'])
                        # a random response from the intent
                        return random.choice(i['responses'])

            results.pop(0)
    else:
        return 'I did not get that. Can you tell me more?'