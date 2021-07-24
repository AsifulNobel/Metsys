import stemming_bn
import nltk

inputs = ["আপনাদের দোকান কবে খোলা থাকবে?", "হ্যালো",
    "একটা টিভি দেখান"]

for sentence in inputs:
    wordList = nltk.word_tokenize(sentence)

    print(wordList)
    if wordList is not None:
        stemming_bn.stemBanglaWord(wordList)
