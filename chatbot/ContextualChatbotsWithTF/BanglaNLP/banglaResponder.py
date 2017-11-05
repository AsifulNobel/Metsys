import numpy as np
import tflearn
import tensorflow as tf
import random
import pickle
import json
import os
import logging
import nltk
from .stemming_bn import isEnglish, stemBanglaWord, loadFile, buildTree
from .timethis import timethis

DIR_NAME = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger(__name__)

context = None
ERROR_THRESHOLD = 0
model = None
words = None
classes = None
train_x = None
train_y = None
intents = None


def initialize():
    loadFile()
    buildTree()
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
    global context
    global ERROR_THRESHOLD
    global words
    global classes
    global train_x
    global train_y
    global intents

    context = {}
    ERROR_THRESHOLD = 0.10

    data = pickle.load(open(os.path.join(DIR_NAME, "training_data"), "rb"))
    words = data['words']
    classes = data['classes']
    train_x = data['train_x']
    train_y = data['train_y']

    with open(os.path.join(DIR_NAME, 'banglaintents.json')) as json_data:
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

    with open(os.path.join(DIR_NAME, 'banglaintents.json')) as json_data:
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
    loadFile()
    buildTree()
    words = [stemBanglaWord(w) for w in words if w not in ignore_words]

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
        # Used custom function stemBanglaWord() here
        pattern_words = [stemBanglaWord(word) for word in pattern_words]
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

    sentence_words = nltk.word_tokenize(sentence)
    logger.debug("Tokenized words: {}".format(sentence_words))

    # stem each word
    sentence_words = [stemBanglaWord(word) for word in sentence_words]
    logger.debug("Stemmed words: {}".format(sentence_words))
    return sentence_words

@timethis
def bow(sentence, words, show_details=False):
    # logger.debug("Training words: {}".format(words))
    # logger.debug("Classes: {}".format(classes))
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
    # logger.debug("BOW output: {}".format(np.array(bag)))
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

def addUserContext(userID):
    """Adds user id to context dictionary"""
    if userID not in context.keys():
        context[userID] = ""
    return


def removeUserContext(userID):
    """Removes user id to context dictionary"""
    if userID in context.keys():
        context.pop(userID)
    return

def response_message(sentence, userID='123', show_details=True):
    global intents
    global model

    failedResponse = "দুঃখিত! আমার কাছে আপনার প্রশ্নের উত্তর নেই। আপনার প্রশ্নের উত্তর জানতে, আপনি আমাদের হেল্পলাইন ০১৭৫২-৫০৯৮৯০ নাম্বারে যোগাযোগ করুন।"
    cannotEvenResponse = "দুঃখিত! আমি আপনার প্রশ্ন বুঝতে পারিনি। আপনি কী আরেকটু বিস্তারিত বলবেন?"

    previousContext = context.get(userID, None)

    if not previousContext:
        addUserContext(userID)

    results = classify(sentence)

    contextual_result = ""
    contextual_result_context = ""
    contextual_result_probablility = 0.0
    non_contextual_result = ""
    non_contextual_result_context = ""
    non_contextual_result_probability = 0.0

    responseTag = ""

    # if we have a classification then find the matching intent tag
    if results:
        # loop as long as there are matches to process
        while results:
            for i in intents['intents']:
                # find a tag matching the first result
                if i['tag'] == results[0][0]:
                    if non_contextual_result == "":
                        if not 'context_filter' in i:
                            non_contextual_result = random.choice(i['responses'])
                            responseTag = 'bangla_'+i['tag']
                            non_contextual_result_probability = results[0][1]
                            #if the new context set in intent i
                            if 'context_set' in i:
                                if show_details:
                                    print ('context:', i['context_set'])
                                non_contextual_result_context = i['context_set']
                    if contextual_result == "":
                        if (userID in context and 'context_filter' in i and (context[userID] in i['context_filter'])):
                            if show_details:
                                print ('tag:', i['tag'])
                            # a random response from the intent
                            contextual_result = random.choice(i['responses'])
                            responseTag = 'bangla_'+i['tag']
                            contextual_result_probablility = results[0][1]
                            if 'context_set' in i:
                                if show_details:
                                    print ('context:', i['context_set'])
                                contextual_result_context = i['context_set']

            results.pop(0)

        if(contextual_result != ""):
            logger.debug(contextual_result)

            if(contextual_result_context != ""):
                context[userID] = contextual_result_context
            return (contextual_result, responseTag)
        elif(non_contextual_result != ""):
            logger.debug(non_contextual_result)

            if (non_contextual_result_context != ""):
                context[userID] = non_contextual_result_context
            return (non_contextual_result, responseTag)
        else:
            logger.debug(cannotEvenResponse)
            return (cannotEvenResponse, responseTag)
    else:
        logger.debug(failedResponse)
        return (failedResponse, responseTag)
