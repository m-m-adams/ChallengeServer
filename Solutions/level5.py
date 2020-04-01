import socket
import time
import select
import sys
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
    decodedarray=[]
    for word in problemtext.split(' '):
        decoded=''
        for n in range(26):
            candidate=Decode.rot(word,n)
            if Decode.CountEnglish(candidate)>0:
                decoded=candidate
        decodedarray.append(decoded)
    return ' '.join(decodedarray)

#############################################################
# Main code starts here

if __name__=="__main__":
    
    serverip="15.223.13.29"
    challengeport=8001
    level=5
    
    #start the challenge game
    Challenge=ChallengeInterface(serverip,challengeport)
    print(Challenge.receive())

    #choose the level to run
    challengetext=Challenge.select_level(level)
    print('\nChallenge Text is:\n',challengetext)
    status=''

    #get current status
    status=select_rline(challengetext,3)
    print('\nStatus is:\n',status)
    
    #trim the text down to the problem statement
    problemtext=select_rline(challengetext,2)
    print('\nProblem Text is:\n',problemtext)

    wordmem={}
    while 'Here is your flag' not in challengetext:
        #solve the problem
        if problemtext in wordmem:
            solution=wordmem[problemtext]
        else: solution=' '
        #print('\nYour solution is:\n',solution)

        #submit the answer    
        challengetext=Challenge.submit_answer(solution,3)

        #parse out the matching pair
        resultwords=select_rline(challengetext,4).rsplit(' ')
        result=resultwords[len(resultwords)-1]
        #print('\nCorrect answer was:\n',result)
        if solution==' ':
            wordmem[problemtext]=result

        status=select_rline(challengetext,3)
        progress=' '.join(['\nStatus is:\n',status,'\n\nI know this many words so far:\n',str(len(wordmem))])
        sys.stdout.write(progress)
        sys.stdout.flush()

        problemtext=select_rline(challengetext,2)
        #print('\nProblem Text is:\n',problemtext)
        
    print('\ncomplete!:\n',challengetext)
    #close the socket at the end of the program
    Challenge.exit()
