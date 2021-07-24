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


print(banglaWordlist)
print(len(banglaWordlist))

