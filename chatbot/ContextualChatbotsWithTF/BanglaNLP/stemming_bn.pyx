import csv
import os

#In this I have used a clever trick to filter out all the garbage in CSV
#I checked if the cell string contains only ASCII or NOT
#If not it is definitely a Bangla Word ;-)
def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True


DIR_NAME = os.path.dirname(os.path.abspath('__file__'))
DIR_NAME_FIX = "/chatbot/ContextualChatbotsWithTF/BanglaNLP"

try:
    with open(os.path.join(DIR_NAME, 'splittedDictionary.csv'), 'r') as csvfile:
        reader = csv.reader(csvfile , delimiter=',')

        banglaWordlist = list()
        array = list(reader)

        for i in range (0 , len(array)-1):
            for j in range( (len(array[i])-1) , 0 , -1):
                if(isEnglish(array[i][j]) == False):
                    banglaWordlist.append(array[i][j])
except FileNotFoundError:
    with open(os.path.join(DIR_NAME+DIR_NAME_FIX, 'splittedDictionary.csv'), 'r') as csvfile:
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
   cdef int longest, x_longest
   longest = 0
   x_longest = 0

   cdef int x, y

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
    cdef int max = 0

    maxString = ""
    for i in banglaWordlist:
        longestCommonSubstring = longest_common_substring(i , s)
        if len(longestCommonSubstring) > max:
            maxString = longestCommonSubstring
            max = len(longestCommonSubstring)
    return maxString
