import string
import re
import os
import copy
import re
import pprint
from itertools import cycle
import decoders.fitnessfuncs as checkenglish
import decoders.ciphers as ciphers
from ciphers import SimpleSubstitution as SimpleSub

def getblankcipherlettermapping():
    return {'A': [], 'B': [], 'C': [], 'D': [], 'E': [], 'F': [], 'G': [], 'H': [], 'I': [], 'J': [], 'K': [], 'L': [], 'M': [], 'N': [], 'O': [], 'P': [], 'Q': [], 'R': [], 'S': [], 'T': [], 'U': [], 'V': [], 'W': [], 'X': [], 'Y': [], 'Z': []}

def addletterstomapping(lettermapping,cipherword,candidate):
    #deep copy to avoid side effects
    lettermapping = copy.deepcopy(lettermapping)
    for i in range(len(cipherword)):
        if candidate[i] not in lettermapping[cipherword[i]]:
            lettermapping[cipherword[i]].append(candidate[i])
    return lettermapping

def intersectmappings(mapA, mapB):

    # To intersect two maps, create a blank map, and then add only the
    # potential decryption letters if they exist in BOTH maps.
    intersectedmapping = getblankcipherlettermapping()
    
    for letter in LETTERS:
        # An empty list means "any letter is possible". In this case just
        # copy the other map entirely.
        if mapA[letter] == []:
            intersectedmapping[letter] = copy.deepcopy(mapB[letter])
        elif mapB[letter] == []:
            intersectedmapping[letter] = copy.deepcopy(mapA[letter])

        #if one mapping has only one possibility, that's it
        elif len(mapA[letter])==1:
            intersectedmapping[letter] = copy.deepcopy(mapA[letter])
        elif len(mapB[letter])==1:
            intersectedmapping[letter] = copy.deepcopy(mapB[letter])
        else:
        # If a letter in mapA[letter] exists in mapB[letter], add
        # that letter to intersectedMapping[letter].
            for mappedletter in mapA[letter]:
                if mappedletter in mapB[letter]:
                    intersectedmapping[letter].append(mappedletter)
    return intersectedmapping

def removesolvedlettersfrommapping(lettermapping):
    lettermapping=copy.deepcopy(lettermapping)
    loopAgain = True
    while loopAgain:
        # First assume that we will not loop again:
        loopAgain = False
        # solvedLetters will be a list of uppercase letters that have one
        # and only one possible mapping in letterMapping
        solvedletters = []
        for cipherletter in LETTERS:
            if len(lettermapping[cipherletter]) == 1:
                solvedletters.append(lettermapping[cipherletter][0])
        #pprint.pprint(solvedletters)
        # If a letter is solved, than it cannot possibly be a potential
        # decryption letter for a different ciphertext letter, so we
        # should remove it from those other lists.
        for cipherletter in LETTERS:
            for s in solvedletters:
                if len(lettermapping[cipherletter]) != 1 and s in lettermapping[cipherletter]:
                    lettermapping[cipherletter].remove(s)
                    if len(lettermapping[cipherletter]) == 1:
                        # A new letter is now solved, so loop again.
                        loopAgain = True
    return lettermapping

def buildlettermap(message):
    #make a blank dictionary
    intersectedmap =getblankcipherlettermapping()
    cipherwords=message.upper()
    #print(cipherwords)
    cipherwords=''.join(filter(lambda ch:ch==' ' or ch.isalpha(),cipherwords))
    candidates={}
    for cipherword in cipherwords.split():
        newmap=getblankcipherlettermapping()
        wordpattern=getwordpattern(cipherword)
        #print(cipherword,wordpattern)
        if wordpattern not in englishpatterns:
            continue
        for candidate in englishpatterns[wordpattern]:
            candidates[candidate]=None
            newmap = addletterstomapping(newmap, cipherword, candidate)
        intersectedmap = intersectmappings(intersectedmap, newmap)
    return removesolvedlettersfrommapping(intersectedmap),candidates

def buildknownpatterns(ciphertext, lettermapping):
    # Return a string of the ciphertext decrypted with the letter mapping,
    # with any ambiguous decrypted letters replaced with an _ underscore.
    # First create a simple sub key from the letterMapping mapping.
    key = ['*'] * len(LETTERS)
    
    for cipherletter in LETTERS:
        if len(lettermapping[cipherletter]) == 1:
            # If there's only one letter, add it to the key.
            keyindex = LETTERS.find(lettermapping[cipherletter][0])
            key[keyindex] = cipherletter
        else:
            ciphertext = ciphertext.replace(cipherletter.lower(), '_')
            ciphertext = ciphertext.replace(cipherletter.upper(), '_')
    
    key = ''.join(key)
    knownpatterns=SimpleSub(key).decipher(ciphertext, True)
    #knownpatterns=ciphers.subuncipher(ciphertext, key)
    knownpatterns=knownpatterns.replace('_','[a-zA-Z]')
    # With the key we've created, decrypt the ciphertext.
    return knownpatterns,key

def decryptwithknownpatterns(knownpatterns,possiblewords):
    decryptedstring=[]
    otherpossibilities={}
    for pattern in knownpatterns.split():
        pattern=''.join(filter(lambda ch:ch in['[',']','-',' '] or ch.isalpha(),pattern))
        pattern=r'\b'+pattern+r'\b'
        #print(pattern)
        p=re.compile(pattern,re.IGNORECASE)
        possibledecryptions=list(filter(p.match,possiblewords))
        
        if len(possibledecryptions)==1:
            decryptedstring.append(possibledecryptions[0])
        else:
            decryptedstring.append('???')
            otherpossibilities[pattern]=(possibledecryptions[0:len(possibledecryptions)])
            
    return ' '.join(decryptedstring),otherpossibilities

def buildknownlettermap(ciphertext,plaintext):
    lettermap=getblankcipherlettermapping()
    cipherarray=ciphertext.split()
    plainarray=plaintext.split()
    for wordnum in range(len(plainarray)):
        if plainarray[wordnum]!='???':
            for letternum in range(len(plainarray[wordnum])):
                lettermap[cipherarray[wordnum][letternum].upper()]=plainarray[wordnum][letternum].upper()
    return lettermap

def decryptsubcipher(ciphertext):
    fullciphertext=ciphertext
    ciphertext=''.join(filter(lambda ch:ch==' ' or ch.isalpha(),ciphertext))
    initiallettermap,possiblewords=buildlettermap(ciphertext)
    knownpatterns,key=buildknownpatterns(ciphertext,initiallettermap)
    plaintext,others=decryptwithknownpatterns(knownpatterns,possiblewords)
    #print(plaintext)
    progress=True
    lastlettermap=initiallettermap
    round=1
    while progress:

        round+=1
        lettermapfromdecryption=buildknownlettermap(ciphertext,plaintext)
        
        #build possible letter map from remaining ciphertext

        remainingcipherwords=[]
        remainingplainwords=[]
        plaintextarray=plaintext.split()
        ciphertextarray=ciphertext.split()
        for i in range(len(plaintextarray)):
            if plaintextarray[i]=='???':
                remainingcipherwords.append(ciphertextarray[i])
        remainingciphertext=' '.join(remainingcipherwords)

        lettermapfromcipher,_=buildlettermap(remainingciphertext)

        
        intersectedlettermap=intersectmappings(lettermapfromdecryption,lettermapfromcipher)
        intersectedlettermap=removesolvedlettersfrommapping(intersectedlettermap)

        #determine whether to continue loop
        progress=intersectedlettermap!=lastlettermap
        lastlettermap=intersectedlettermap
        
        knownpatterns2,key=buildknownpatterns(ciphertext,intersectedlettermap)
        plaintext,others=decryptwithknownpatterns(knownpatterns2,possiblewords)
        print(round)

    
    return(ciphers.subuncipher(fullciphertext, key), intersectedlettermap, key)

def getwordpattern(word):
    # Returns a string of the pattern form of the given word.
    # e.g. '0.1.2.3.4.1.2.3.5.6' for 'DUSTBUSTER'
    word = word.upper()
    nextNum = 1
    letterNums = {}
    wordPattern = []

    for letter in word:
        if letter not in letterNums:
            letterNums[letter] = str(nextNum)
            nextNum += 1
        wordPattern.append(letterNums[letter])

    return int(''.join(wordPattern))

def makewordpatterns(pathtodictionary):

    allPatterns = {}
    fo = open(pathtodictionary)
    wordList = fo.read().split('\n')
    fo.close()
    for word in wordList:
        # Get the pattern for each string in wordList.
        pattern = getwordpattern(word)
        if pattern not in allPatterns:
            allPatterns[pattern] = [word]
        else:
            allPatterns[pattern].append(word)

    return allPatterns

def quickdecryptsubcipher(ciphertext,nwords):
    splittext=ciphertext.split()
    splittext.sort(key=len)
    splittext.reverse()
    partialcipher=' '.join(splittext[0:nwords])
    plain,lettermap,key=decryptsubcipher(partialcipher)
    return(ciphers.subuncipher(ciphertext, key))

if __name__=='__main__':

    wordpatternpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dictionaries', "wordpatterns.py")
    if not os.path.exists(wordpatternpath):
        fo = open(wordpatternpath, 'w')
        fo.write('allpatterns= ')
        wordpatterns = makewordpatterns(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dictionaries', "dictionary.txt"))
        fo.write(pprint.pformat(wordpatterns))
        fo.close()

    import decoders.dictionaries.wordpatterns as wordpatterns
    englishpatterns=wordpatterns.allpatterns
    LETTERS='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    print(LETTERS)
    
    mymessage = 'If a man is offered a fact which goes against his instincts, he will scrutinize it closely, and unless the evidence is overwhelming, he will refuse to believe it. If, on the other hand, he is offered something which affords a reason for acting in accordance to his instincts, he will accept it even on the slightest evidence. The origin of myths is explained in this way. -Bertrand Russell'
    #ciphertext='KWJRCAKM TCCTCCHXTBAJC YWERHMCB JMPWUMXMCEM IZAGHTC JMVWMCB OHCKTXXMO GJAAKGTLLMJC HOHABEHMC WXCWIIAJBMO TOUHCMC SAJTKHXHSMJ AUMJJTXR OJWYYMBC FALSMO'
    key='LFWOAYUISVKMNXPBDCRJTQEGHZ'

    ciphertext=SimpleSub(key).encipher(mymessage, True)
    print(ciphertext)
    print(SimpleSub(key).decipher(ciphertext, True))
    plain=quickdecryptsubcipher(ciphertext,20)


