PORT_NUM_PRIME = 64499

#  djb2 by Dan Bernstein (www.cse.yorku.ca/~oz/hash.html)
def hash(string):
    hash = 5381
    for ch in string:
        hash = ((hash << 5) + hash) + ord(ch)

    print(hash % PORT_NUM_PRIME)
    return hash % PORT_NUM_PRIME



hash("asdfasdf")