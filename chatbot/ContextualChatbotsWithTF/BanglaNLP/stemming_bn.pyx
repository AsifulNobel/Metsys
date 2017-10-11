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

class Node:
    def __init__(self, label=None, data=None):
        self.label = label
        self.data = data
        self.children = dict()

    def addChild(self, key, data=None):
        if not isinstance(key, Node):
            self.children[key] = Node(key, data)
        else:
            self.children[key.label] = key

    def __getitem__(self, key):
        return self.children[key]


class Trie:
    def __init__(self):
        self.head = Node()

    def __getitem__(self, key):
        return self.head.children[key]

    def add(self, word):
        current_node = self.head
        word_finished = True

        for i in range(len(word)):
            if word[i] in current_node.children:
                current_node = current_node.children[word[i]]
            else:
                word_finished = False
                break

        # For ever new letter, create a new child node
        if not word_finished:
            while i < len(word):
                current_node.addChild(word[i])
                current_node = current_node.children[word[i]]
                i += 1

        # Let's store the full word at the end node so we don't need to
        # travel back up the tree to reconstruct the word
        current_node.data = word

    def has_word(self, word):
        if word == '':
            return False
        if word == None:
            raise ValueError('Trie.has_word requires a not-Null string')

        # Start at the top
        current_node = self.head
        exists = True
        for letter in word:
            if letter in current_node.children:
                current_node = current_node.children[letter]
            else:
                exists = False
                break

        # Still need to check if we just reached a word like 't'
        # that isn't actually a full word in our dictionary
        if exists:
            if current_node.data == None:
                exists = False

        return exists

    def start_with_prefix(self, prefix):
        """ Returns a list of all words in tree that start with prefix """
        words = list()
        if prefix == None:
            raise ValueError('Requires not-Null prefix')

        # Determine end-of-prefix node
        top_node = self.head
        for letter in prefix:
            if letter in top_node.children:
                top_node = top_node.children[letter]
            else:
                # Prefix not in tree, go no further
                return words

        # Get words under prefix
        if top_node == self.head:
            queue = [node for key, node in top_node.children.items()]
        else:
            queue = [top_node]

        # Perform a breadth first search under the prefix
        # A cool effect of using BFS as opposed to DFS is that BFS will return
        # a list of words ordered by increasing length
        while queue:
            current_node = queue.pop()
            if current_node.data != None:
                # Isn't it nice to not have to go back up the tree?
                words.append(current_node.data)

            queue = [node for key, node in current_node.children.items()] + queue

        return words

    def getData(self, word):
        """ This returns the 'data' of the node identified by the given word """
        if not self.has_word(word):
            raise ValueError('{} not found in trie'.format(word))

        # Race to the bottom, get data
        current_node = self.head
        for letter in word:
            current_node = current_node[letter]

        return current_node.data


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
    DIR_NAME_FIX = "/BanglaNLP"

    try:
        with open(os.path.join(DIR_NAME, 'splittedDictionary.csv'), 'r') as csvfile:
            loadWords(csvfile)
    except FileNotFoundError:
        with open(os.path.join(DIR_NAME+DIR_NAME_FIX, 'splittedDictionary.csv'), 'r') as csvfile:
            loadWords(csvfile)

@timethis
def buildTree():
    global banglaWordlist
    global trie

    cdef:
        int j = 0
        int k = 0
        int length = 0

    trie = Trie()
    for i in banglaWordlist:
        length = len(i)

        for j in range(1, length+1):
            for k in range(0, j):
                trie.add(i[k:j])


def stemBanglaWord(s):
    length = len(s)
    max = 0
    maxString = ""
    flag = False
    for j in range(1, length+1):
        for k in range(0, j):
            substring = s[k:j]
            if (trie.has_word(substring) == True):
                flag = True
                if ((j-k) > max):
                    max = j-k
                    maxString = substring
    if(flag == False):
        return s
    return maxString

cdef list banglaWordlist = list()
cdef int bnWordListLength = 0
trie = None
