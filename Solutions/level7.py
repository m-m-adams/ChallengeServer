import socket
import time
import select
import decoders.Decode as Decoder
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
    def submit_answer(self,solution):
        self.transmit(solution)
        result=''
        while result=='':
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
    # 0.15 second wait each loop accounts for latency on the
    # server side - it's an AWS t2.nano instance......
    def receive(self):
        do_read = True
        receiveddata=''
        while (do_read):
            try:
                r, _, _ = select.select([self.sock], [], [],0.15)
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


# TrimToInput
# Takes the full challenge text as input and trims it down to
# the line that you need to work with to solve the problem
# this is a different line in some levels, so pay attention

def trim_to_input(fulltext):
    lines=fulltext.rsplit("\n")
    problemtext=lines[len(lines)-2] 
    return problemtext


# SolveProblem
# Solve the problem in this function
# feel free to declare more functions, but don't do it in the
# main block of code - poor programming practice

def solve_problem(problemtext):
    answer=Decoder.quickdecryptsubcipher(problemtext,15)
    return answer

#############################################################
# Main code starts here

if __name__=="__main__":
    
    serverip="localhost"
    challengeport=8001
    
    #start the challenge game
    Challenge=ChallengeInterface(serverip,challengeport)
    print(Challenge.receive())

    #choose the level to run
    challengetext=Challenge.select_level('7')
    print('\nChallenge Text is:\n',challengetext)

    #trim the text down to the problem statement
    problemtext=trim_to_input(challengetext)
    print('\nProblem Text is:\n',problemtext)


    #solve the problem
    solution=solve_problem(problemtext)
    print('\nYour solution is:\n',solution)

    #submit the answer    
    result=Challenge.submit_answer(solution)
    print('\n Result is:\n',result)


    #close the socket at the end of the program
    Challenge.exit()
