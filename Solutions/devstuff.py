import socket
import time
import select
import sys
import base64
import itertools
import decoders.Decode as Decode
###########################################################
# Class declarations                                      
###########################################################

###########################################################
# Challenge Interface
# This class is a wrapper for socket functions to make
# them more friendly to use in this context. Has specific
# functions select_level and submit_answer for this
# challenge, as well as implementing friendlier send and
# receives, reset, and exit for internal use in the class.


class ChallengeInterface(object):
    #setup the socket to connect to the challenge
    #This function has default arguments
    def __init__(self,address,port):
        sock=socket.socket()
        sock.connect((address,port))
        self.address=address
        self.port=port
        self.sock=sock

    #accept a level and a challenge socket as
    #input, select the level and return its text
    def select_level(self,level):
        self.transmit(level)
        ChallengeText=self.receive()
        return ChallengeText

    #If it's correct you get a flag
    #if it's incorrect you get a new challenge
    #in some challenges, on submitting a correct
    #answer you immediately get a new challenge,
    #which will be stored in result
    #accepts a number of lines to receive - continues
    #to receive more data until this number is hit
    
    def submit_answer(self,solution,nlines=1):
        self.transmit(solution)
        result=''
        
        while len(result.split('\n'))<nlines:
            time.sleep(0.1)
            result=self.receive()
        return result
    
    #resets the socket and restarts the connection
    #shouldn't be needed but implemented for robustness
    def reset(self):
        self.exit()
        sock=socket.socket()
        sock.connect((self.address,self.port))
        self.sock=sock

    #generic socket encode and send
    def transmit(self,submission):
        return self.sock.send(str(submission).encode())
    
    # socket receive and decode
    # checks that the socket has data on it, and if so reads
    # repeats until the socket has no more data
    # 0.2 second wait each loop accounts for latency on the
    # server side - it's an AWS t2.nano instance......
    def receive(self):
        do_read = True
        receiveddata=''
        while (do_read):
            try:
                r, _, _ = select.select([self.sock], [], [],0.2)
                do_read = bool(r)
            except socket.error:
                pass
            if do_read:
                data = self.sock.recv(1024).decode()
                receiveddata+=data
        return receiveddata
    
    #generic socket close
    def exit(self):
        self.sock.close()

#end of challenge interface class
#############################################################

#############################################################
# Function declarations                                      
#############################################################


# select_rline
# Takes the full challenge text as input and selects a line
# from the end. Challenge text is normally the second last
# line, so use rline=2 by default

def select_rline(fulltext,rline=2):
    lines=fulltext.rsplit("\n")
    problemtext=lines[len(lines)-rline] 
    return problemtext


# SolveProblem
# Solve the problem in this function
# feel free to declare more functions, but don't do it in the
# main block of code - poor programming practice

def solve_problem(problemtext):
    rotresults=[]
    for n in range(26):
        candidate=Decode.rot(problemtext,n)
        candidate=list(candidate)
        reassembled=''
        for i in range(0, len(candidate),4):
            answer=[]
            chunk=''.join(candidate[i:i+4])
            UppLowPerms=[''.join(x)for x in  itertools.permutations(list(chunk)+list(chunk.lower()),len(chunk)) if ''.join(x).lower()==chunk.lower()]
            UppLowPerms=list(set(UppLowPerms))
            for possibility in UppLowPerms:
                try:
                    maybe=base64.b64decode(possibility).decode()
                    a=maybe.replace(' ','')
                    if a.isalnum() and a.isupper():
                        answer.append(maybe)
                except: pass
            if len(answer)==1:
                reassembled+=answer[0]
            elif len(answer)==2:
                reassembled1=reassembled+answer[0]
                reassembled2=reassembled+answer[1]
                if Decode.CountEnglish(reassembled1)>Decode.CountEnglish(reassembled2):
                    rotresults.append(reassembled1)
                else:
                    rotresults.append(reassembled2)
    wordcount=0
    for possibility in rotresults:
        CurCount=Decode.CountEnglish(possibility)
        if CurCount>wordcount:
            solution=possibility
            wordcount=CurCount

    if solution:
        return solution
    else:
        return 0

Input='keyboard slaughtered'
uppered=Input.upper()
base64ed=base64.b64encode(uppered.encode())
roted=Decode.rot(base64ed,4)
upperedagain=roted.upper().decode()

answer=solve_problem(upperedagain)
print(answer)
