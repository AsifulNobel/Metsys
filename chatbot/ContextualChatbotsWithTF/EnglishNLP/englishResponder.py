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

stemmer = None
context = None
ERROR_THRESHOLD = 0
model = None
words = None
classes = None
train_x = None
train_y = None
intents = None


def initialize():
    loadData()
    buildNN()
    loadModel()


def buildNN():
    """Builds neural network graph and sets it to global model handler"""
    global model
    # Clears the default graph stack and resets the global default graph
    tf.reset_default_graph()

    net = tflearn.input_data(shape=[None, len(train_x[0])])
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, len(train_y[0]), activation='softmax')
    net = tflearn.regression(net)
    model = tflearn.DNN(net, tensorboard_dir='tflearn_logs')

def loadData():
    global stemmer
    global context
    global ERROR_THRESHOLD
    global words
    global classes
    global train_x
    global train_y
    global intents

    stemmer = LancasterStemmer()
    context = {}
    ERROR_THRESHOLD = 0.25

    data = pickle.load(open(os.path.join(DIR_NAME, "training_data"), "rb"))
    words = data['words']
    classes = data['classes']
    train_x = data['train_x']
    train_y = data['train_y']

    with open(os.path.join(DIR_NAME, 'intents.json')) as json_data:
        logger.info("Loading Intents...")
        intents = json.load(json_data)


def loadModel():
    """Loads training data for Neural Network"""
    global model

    logger.info("Loading Model...")
    model.load(DIR_NAME + '/model.tflearn')


def train():
    """Train a neural network on the fly"""
    words = []
    classes = []
    documents = []
    ignore_words = ['?']
    intents = None

    with open(os.path.join(DIR_NAME, 'intents.json')) as json_data:
        logger.info("Loading Intents...")
        intents = json.load(json_data)

    # loop through each sentence in our intents patterns
    for intent in intents['intents']:
        for pattern in intent['patterns']:
            # tokenize each word in the sentence
            w = nltk.word_tokenize(pattern)
            # add to our words list
            words.extend(w)
            # add to documents in our corpus
            documents.append((w, intent['tag']))
            # add to our classes list
            if intent['tag'] not in classes:
                classes.append(intent['tag'])

    # stem and lower each word and remove duplicates
    words = [stemmer.stem(w.lower()) for w in words if w not in ignore_words]
    words = sorted(list(set(words)))

    # remove duplicates
    classes = sorted(list(set(classes)))

    training = []
    output_empty = [0] * len(classes)

    # training set, bag of words for each sentence
    for doc in documents:
        # initialize our bag of words
        bag = []
        # list of tokenized words for the pattern
        pattern_words = doc[0]
        # stem each word
        pattern_words = [stemmer.stem(word.lower()) for word in pattern_words]
        # create our bag of words array
        for w in words:
            bag.append(1) if w in pattern_words else bag.append(0)

        # output is a '0' for each tag and '1' for current tag
        output_row = list(output_empty)
        output_row[classes.index(doc[1])] = 1

        training.append([bag, output_row])

    # shuffle our features and turn into np.array
    random.shuffle(training)
    training = np.array(training)

    # create train and test lists
    train_x = list(training[:, 0])
    train_y = list(training[:, 1])
    # notice that our data is shuffled. Tensorflow will take some of this and use it as test data to gauge accuracy for a newly fitted model.

    tf.reset_default_graph()
    # Build neural network

    net = tflearn.input_data(shape=[None, len(train_x[0])])
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, len(train_y[0]), activation='softmax')
    net = tflearn.regression(net)

    # Define model and setup tensorboard
    model = tflearn.DNN(net, tensorboard_dir=os.path.join(DIR_NAME, 'tflearn_logs'))
    # Start training (apply gradient descent algorithm)
    model.fit(train_x, train_y, n_epoch=1000, batch_size=8, show_metric=True)
    model.save(os.path.join(DIR_NAME, 'model.tflearn'))  ##save the tensorflow model
    logger.info('Saving model...')

    import pickle
    pickle.dump({'words': words, 'classes': classes, 'train_x': train_x, 'train_y': train_y},
                open(os.path.join(DIR_NAME, "training_data"), "wb"))


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
                    # a random response from the intent
                    return random.choice(i['responses'])

            results.pop(0)
    else:
        return 'I did not get that. Can you tell me more?'
