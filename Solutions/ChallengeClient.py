import socket
import time
import select

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


class challengeinterface(object):
    #setup the socket to connect to the challenge
    #This function has default arguments
    def __init__(self,address,port):
        sock=socket.socket()
        self.address=address
        self.port=port
        self.sock=sock

    def start(self):
        self.sock.connect((self.address, self.port))
        return self.receive()
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
    # default to receiving until it receives 'END MESSAGE\n', as sent by the server's communications.py
    def receive(self, terminator='END MESSAGE\n'):
        do_read = False
        receiveddata=''
        while not receiveddata.endswith(terminator):
            try:
                # select.select will return true if there is data on the socket
                # this prevents the recv function from blocking
                r, _, _ = select.select([self.sock], [], [],0.15)

                do_read = bool(r)
            except socket.error:
                pass
            if do_read:
                data = self.sock.recv(1024).decode()
                receiveddata+=data
        return receiveddata.replace('END MESSAGE\n','')
    
    #generic socket close
    def exit(self):
        self.sock.close()

#end of challenge interface class
#############################################################
