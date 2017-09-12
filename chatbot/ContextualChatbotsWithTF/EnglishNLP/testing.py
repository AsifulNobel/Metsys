##############################    STEP 1    ################################
#things we need for NLP
import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()


##############################    STEP 2    ################################
#things we need for Tensorflow
import numpy as np
import tflearn
import tensorflow as tf
import random


##############################    STEP 3    ################################
# import our chat-bot intents file
import json

with open('intents.json') as json_data:
    intents = json.load(json_data)


##############################    STEP 4    ################################
#we can now begin to organize our documents, words and classification classes
words = []
classes = []
documents = []
ignore_words = ['?']
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

print (len(documents), "documents")
print (len(classes), "classes", classes)
print (len(words), "unique stemmed words", words)


##############################    STEP 5    ################################
#unfortunately this data structure won’t work with Tensorflow, we need to transform it further: from documents of words into tensors of numbers.
# create our training data
training = []
output = []
# create an empty array for our output
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
train_x = list(training[:,0])
train_y = list(training[:,1])
#notice that our data is shuffled. Tensorflow will take some of this and use it as test data to gauge accuracy for a newly fitted model.



##############################    STEP 6    ################################
#We’re ready to build our model.
#This is the same structure used here - https://chatbotslife.com/deep-learning-in-7-lines-of-code-7879a8ef8cfb

# reset underlying graph data
tf.reset_default_graph()
# Build neural network

net = tflearn.input_data(shape=[None, len(train_x[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(train_y[0]), activation='softmax')
net = tflearn.regression(net)

# Define model and setup tensorboard
model = tflearn.DNN(net, tensorboard_dir='tflearn_logs')
# Start training (apply gradient descent algorithm)
model.fit(train_x, train_y, n_epoch=1000, batch_size=8, show_metric=True)
model.save('model.tflearn')  ##save the tensorflow model


##############################    STEP 7    ################################
# save all of our data structures
import pickle
pickle.dump( {'words':words, 'classes':classes, 'train_x':train_x, 'train_y':train_y}, open( "training_data", "wb" ) )




# #this stupid code make no sense . Cause I tried to use this code from separate file and failed . In same file we don't need to reload everything again
# ##############################    STEP 8    ################################
# #loading our previous works . So if Step 1-7 is done we don't need to further run them again and again
#
# # restore all of our data structures
# import pickle
# data = pickle.load( open( "training_data", "rb" ) )
# words = data['words']
# classes = data['classes']
# train_x = data['train_x']
# train_y = data['train_y']
#
# # import our chat-bot intents file
# import json
# with open('intents.json') as json_data:
#     intents = json.load(json_data)
#
# # load our saved model
#model.load('./model.tflearn')


##############################    STEP 9    ################################
# Before we can begin processing intents, we need a way to produce a bag-of-words from user input.
# This is the same technique as we used earlier to create our training document

def clean_up_sentence(sentence):
    # tokenize the pattern
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word
    sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
    return sentence_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence
def bow(sentence, words, show_details=False):
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

    return(np.array(bag))

print (bow("is your shop open today?", words))


#commenting out STEP 10 and 11 because this is the test of context free response
#as contextual response is added in STEP 12 commenting out the 10 and 11
#but keeping the code for future reference and comparison

# ##############################    STEP 10    ################################
# #building th response processor
# ERROR_THRESHOLD = 0.25
# def classify(sentence):
#     # generate probabilities from the model
#     results = model.predict([bow(sentence, words)])[0]
#     # filter out predictions below a threshold
#     results = [[i,r] for i,r in enumerate(results) if r>ERROR_THRESHOLD]
#     # sort by strength of probability
#     results.sort(key=lambda x: x[1], reverse=True)
#     return_list = []
#     for r in results:
#         return_list.append((classes[r[0]], r[1]))
#     # return tuple of intent and probability
#     return return_list
#
# def response(sentence, userID='123', show_details=False):
#     results = classify(sentence)
#     # if we have a classification then find the matching intent tag
#     if results:
#         # loop as long as there are matches to process
#         while results:
#             for i in intents['intents']:
#                 # find a tag matching the first result
#                 if i['tag'] == results[0][0]:
#                     # a random response from the intent
#                     return print(random.choice(i['responses']))
#
#             results.pop(0)
#
#
#
# #Each sentence passed to response() is classified.
# # Our classifier uses model.predict() and is lighting fast.
# # The probabilities returned by the model are lined-up with our intents definitions to produce a list of potential responses.
# #If one or more classifications are above a threshold, we see if a tag matches an intent and then process that.
# # We’ll treat our classification list as a stack and pop off the stack looking for a suitable match until we find one, or it’s empty.
#
#
# ##############################    STEP 11    ################################
# #testing our classify and response function
# #remember this a context free response
# #Contextualization has not been included yet
#
# print(classify('is your shop open today?'))
# response('is your shop open today?')
# print(classify('do you take cash?'))
# response('do you take cash?')
# print(classify('what kind of mopeds do you rent?'))
# response('what kind of mopeds do you rent?')
# print(classify('Goodbye, see you later'))
# response('Goodbye, see you later')



##############################    STEP 12    ################################
#we are now moving towards the final step of our program
# which is the bot can answer the question based on the context of whole conversation

#We want to handle a question about renting a moped and ask if the rental is for today.
# That clarification question is a simple contextual response.
# If the user responds ‘today’ and the context is the rental timeframe then it’s best they call the rental company’s 1–800 #.
# No time to waste.
#To achieve this we will add the notion of ‘state’ to our framework. T
# his is comprised of a data-structure to maintain state and specific code to manipulate it while processing intents.
#Because the state of our state-machine needs to be easily persisted, restored, copied, etc.
# it’s important to keep it all in a data structure such as a dictionary.


# create a data structure to hold user context
context = {}

ERROR_THRESHOLD = 0.25
def classify(sentence):
    # generate probabilities from the model
    results = model.predict([bow(sentence, words)])[0]
    # filter out predictions below a threshold
    results = [[i,r] for i,r in enumerate(results) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append((classes[r[0]], r[1]))
    # return tuple of intent and probability
    return return_list

def response(sentence, userID='123', show_details=False):
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
                        if show_details: print ('context:', i['context_set'])
                        context[userID] = i['context_set']

                    # check if this intent is contextual and applies to this user's conversation
                    if not 'context_filter' in i or \
                        (userID in context and 'context_filter' in i and i['context_filter'] == context[userID]):
                        if show_details: print ('tag:', i['tag'])
                        # a random response from the intent
                        return print(random.choice(i['responses']))

            results.pop(0)


# Our context state is a dictionary, it will contain state for each user.
# We’ll use some unique identified for each user (eg. cell #).
# This allows our framework and state-machine to maintain state for multiple users simultaneously.
# create a data structure to hold user context
# context = {}
#In this way, if a user just typed ‘today’ out of the blue (no context), our ‘today’ intent won’t be processed.
# If they enter ‘today’ as a response to our clarification question (intent tag:‘rental’) then the intent is processed.

response('we want to rent a moped')
response('today')
