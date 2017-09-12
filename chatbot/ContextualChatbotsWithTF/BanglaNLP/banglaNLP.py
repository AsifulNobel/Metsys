#In this I have used a clever trick to filter out all the garbage in CSV
#I checked if the cell string contains only ASCII or NOT
#If not it is definitely a Bangla Word ;-)

import csv

# -*- coding: utf-8 -*-
def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

with open('splittedDictionary.csv', 'r') as csvfile:
    reader = csv.reader(csvfile , delimiter=',')

    banglaWordlist = list()
    array = list(reader)

    for i in range (0 , len(array)-1):
        for j in range( (len(array[i])-1) , 0 , -1):
            if(isEnglish(array[i][j]) == False):
                banglaWordlist.append(array[i][j])


#print(banglaWordlist)
#print(len(banglaWordlist))

#### This is an implementation of Longest Common Subsequence algorithm in Python 3.*

# Dynamic programming implementation of LCS problem

# Returns length of LCS for X[0..m-1], Y[0..n-1]
def longest_common_substring(s1, s2):
   m = [[0] * (1 + len(s2)) for i in range(1 + len(s1))]
   longest, x_longest = 0, 0
   for x in range(1, 1 + len(s1)):
       for y in range(1, 1 + len(s2)):
           if s1[x - 1] == s2[y - 1]:
               m[x][y] = m[x - 1][y - 1] + 1
               if m[x][y] > longest:
                   longest = m[x][y]
                   x_longest = x
           else:
               m[x][y] = 0
   return s1[x_longest - longest: x_longest]

def stemBanglaWord(s):
    max = 0
    maxString = ""
    for i in banglaWordlist:
        longestCommonSubstring = longest_common_substring(i , s)
        if len(longestCommonSubstring) > max:
            maxString = longestCommonSubstring
            max = len(longestCommonSubstring)
    return maxString



######PREVIOUS CODE SECTIONS STARTS HERE###################

import json
import trie
import nltk

with open('./banglaintents.json') as json_data:
    intents = json.load(json_data)




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
#Used custom function stemBanglaWord() here
words = [stemBanglaWord(w) for w in words if w not in ignore_words]
#words = sorted(list(set(words)))

# remove duplicates
classes = sorted(list(set(classes)))

print (len(documents), "documents",documents)
print (len(classes), "classes", classes)
print (len(words), "unique stemmed words", words)

