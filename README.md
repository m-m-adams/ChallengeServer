# ScriptingServer
python scripting server

In the solutions folder you'll find challengeinterface.py and startersolution.py. 
The challenge interface opens the socket to the challenge server and handles latency issues. 
If you write your own interface and your code doesn't work the first step will be using the provided one

Challengeinterface:

Initiate the challenge by calling challenge=ChallengeClient.challengeinterface(destination,destinationport)

select your level with challengetext=challenge.select_level(level). The return value is the text for the selected level

Submit an answer with challenge.submit_answer(answer). The return value is the response from the server
Note that in many challenges the return value is a new problem that must be solved to get the flag

When you have a flag, the return will include the string 'Here is your flag:' 

There are other methods in the challenge interface class but they are not necessary to solve any problems


Hints:

Problem 1:
You can solve this most easily using regex or a filter
It's also possible to loop through the string and reconstruct a new 'cleaned' string

Problem 2:
Try sorting all the words in the answer into an upper list and a lower list

Problem 3:
This problem is testing your ability to repeatedly parse a word out of the challenge response and resubmit it

Problem 4:
