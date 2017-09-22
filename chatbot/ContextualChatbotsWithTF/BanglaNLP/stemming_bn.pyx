import csv
import os
from libc.stddef cimport wchar_t
from cpython.mem cimport PyMem_Malloc, PyMem_Free

try:
    from timethis import timethis
except ModuleNotFoundError:
    from .timethis import timethis

cdef extern from "Python.h":
    wchar_t* PyUnicode_AsWideCharString(object, Py_ssize_t *)


def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

def loadWords(csvfile):
    global banglaWordlist
    global bnWordListLength
    reader = csv.reader(csvfile , delimiter=',')

    array = list(reader)

    for i in range (0 , len(array)-1):
        for j in range( (len(array[i])-1) , 0 , -1):
            if (isEnglish(array[i][j]) == False) and (len(array[i][j]) > 0):
                banglaWordlist.append(array[i][j])
    bnWordListLength = len(banglaWordlist)

@timethis
def loadFile():
    DIR_NAME = os.path.dirname(os.path.abspath('__file__'))
    DIR_NAME_FIX = "/chatbot/ContextualChatbotsWithTF/BanglaNLP"

    try:
        with open(os.path.join(DIR_NAME, 'splittedDictionary.csv'), 'r') as csvfile:
            loadWords(csvfile)
    except FileNotFoundError:
        with open(os.path.join(DIR_NAME+DIR_NAME_FIX, 'splittedDictionary.csv'), 'r') as csvfile:
            loadWords(csvfile)


#### This is an implementation of Longest Common Subsequence algorithm in Python 3.*
# Dynamic programming implementation of LCS problem

# Returns length of LCS for X[0..m-1], Y[0..n-1]
def longest_common_substring(refWord, stemWord):
    cdef:
        int longest, x_longest
        int x, y, k
        Py_ssize_t lengthRefWord
        Py_ssize_t lengthStemWord
        wchar_t *referenceWord = PyUnicode_AsWideCharString(refWord, &lengthRefWord)
        wchar_t *stemmableWord = PyUnicode_AsWideCharString(stemWord, &lengthStemWord)
        int t1 = lengthRefWord+1
        int t2 = lengthStemWord+1
        int **m = <int **> PyMem_Malloc(t1 * sizeof(int *))
        wchar_t tempChar1;
        wchar_t tempChar2;
    longest = 0
    x_longest = 0

    for k in range(t1):
       m[k] = <int *> PyMem_Malloc(t2 * sizeof(int))
    for x in range(0, t1):
        for y in range(0, t2):
            m[x][y] = 0

    for x in range(1, t1):
        for y in range(1, t2):
           tempChar1 = referenceWord[x - 1]
           tempChar2 = stemmableWord[y - 1]

           if tempChar1 == tempChar2:
               m[x][y] = m[x - 1][y - 1] + 1
               if m[x][y] > longest:
                   longest = m[x][y]
                   x_longest = x
           else:
               m[x][y] = 0
    for k in range(t1):
       PyMem_Free(m[k])
    PyMem_Free(m)
    PyMem_Free(referenceWord)
    PyMem_Free(stemmableWord)
    return refWord[x_longest - longest: x_longest]


def stemBanglaWord(s):
    cdef:
        int max = 0
        int i = 0
    global banglaWordlist

    maxString = ""

    for i in range(bnWordListLength):
        longestCommonSubstring = longest_common_substring(banglaWordlist[i], s)
        if len(longestCommonSubstring) > max:
            maxString = longestCommonSubstring
            max = len(longestCommonSubstring)
    return maxString

cdef list banglaWordlist = list()
cdef int bnWordListLength = 0
loadFile()
