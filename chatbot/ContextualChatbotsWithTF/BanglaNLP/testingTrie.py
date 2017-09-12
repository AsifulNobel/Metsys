texts = [ "The lion (Panthera leo) ...", "Panthera ...", "..." ]
keywords  = ['cat', 'lion', 'panthera', 'family']

# gives the count of `word in text`
def matches(text):
    return sum(word in text.lower() for word in keywords)

# or inline that helper function as a lambda:
# matches = lambda text:sum(word in text.lower() for word in keywords)

# print the one with the highest count of matches
print (max(texts, key=matches))