# ScriptingServer
python scripting server

In the solutions folder you'll find challengeinterface.py and startersolution.py. 
The challenge interface opens the socket to the challenge server and handles latency issues. 
If you write your own interface and your code doesn't work the first step will be using the provided one

Challengeinterface:

Initiate the challenge by calling challenge=ChallengeClient.challengeinterface(destination,destinationport)

select your level with challengetext=challenge.select_level(level). The return value is the text for the selected level

Submit an answer with challenge.submit_answer(answer). The return value is the response from the server

Note that in many challenges the return value is a new problem that must be solved to get the flag. When you have a flag, the return will include the string 'Here is your flag:' 

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
Some words will have multiple possible candidates - you might need to decipher 55-60 phrases in order to get 50 correct answers.  

Problem 5:   
At the beginning you know none of the word associations. Each time you submit an incorrect answer, you'll be given the correct assocation. Use this to build out a dictionary of word associations that you know and if you are given a word that's in your dictionary, return it  

Problem 6:  
If you try to bruteforce the case of the entire base64 encoded phrase at once, it's going to need a supercomputer. Use the fact that 4 base64 digits always decode to the same 3 input bytes, and brute force it piecewise

Problem 7:  
It's not a rot cipher, it's making a random reorder of the alphabet and using that as the substiution table.  
Don't try to brute force this - a 26 letter key is about 100 bits, and 2^100 operations is well beyond what you can run on a home computer. It is possible to deterministically decrypt a random sub cipher if the input is long enough, and it is in this challenge.

