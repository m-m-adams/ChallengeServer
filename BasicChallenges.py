"""



"""
""" Imports """
import random
import time
import os
from flags import *
""" Module methods """


def load_word_list(path):
    # Open the file
    with open(path) as file:
        # Extract all the words
        words = [word.strip('\n') for word in file.readlines()]

    # Return the word list in python list format
    return words


""" Module constants """
CurrentPath=os.path.dirname(os.path.abspath(__file__))
WORD_LIST = load_word_list(os.path.join(CurrentPath,"wordlist.txt"))

""" Class definitions """


class BasicChallengeManager:
    def __init__(self):
        # Load the challenges
        self.challenges_bank = {
            1: GarbageChars,
            2: UpperAndLower,
            3: Copycat,
            4: RotN,
            5: WordAssociation,
            6: RotTheBass,
            7: Substitution
        }

    def retrieve_challenge(self, challenge_number):
        # Check if the input is in the right format (integer)
        if not isinstance(challenge_number, int):
            # Case where input is not correctly formatted as integer
            try:
                # Try to cast to int
                challenge_number = int(challenge_number)

            except Exception as error_message:
                # If cast not successful, just return None
                return None

        # Check if challenge is actually listed
        if challenge_number in self.challenges_bank:
            # If challenge found, send it to the vault
            return self.challenges_bank[challenge_number]
        else:
            # If challenge is not found
            return None

    def get_num_challenges(self):
        # Get the number of challenges
        num_challenges = len(self.challenges_bank)

        # Return the value
        return num_challenges


class ChallengeAbstract:
    def __init__(self, client_communications):
        # Establish communication line from challenge to client
        self.client = client_communications

    def recv(self):
        # Retrieve message from client
        return self.client.recv()

    def send(self, byte_message):
        # Send message to client
        self.client.send(byte_message)

    def run(self):
        """
        When a challenge is selected, this method will be called
        to start the challenge.

        Parameters:
        None

        Returns:
        None

        """
        # Will be implemented by subclass
        print("TOO BE IMPLEMENTED BY SUBCLASS")


class GarbageChars(ChallengeAbstract):
    def __init__(self, client_communication):
        # Call superclasses' __init__ method
        super().__init__(client_communication)

        # Create reference to module's private word list
        self.word_list = WORD_LIST

    def run(self):
        # Define the flag
        flag = "Garbage-Removal-Via-Script"

        # Define the number of words for the challenge
        number_of_words = 6

        # Define the garbage characters
        garbage_chars = '!"@^#$%&()*+,-.?0123456789'

        # Define the reaction threshold time (seconds)
        reaction_threshold = 2

        # Keep running until the challenge is complete
        while True:
            # Randomly choose word list indices to get words from
            indices_list = [random.randint(0, len(self.word_list) - 1) for _ in range(0, number_of_words)]

            # Extract the words from the word list
            selected_words = [self.word_list[index] for index in indices_list]

            # Save the answer
            answer = " ".join(selected_words)

            # Create a container for the garbage added words
            garbage_words = []

            # Parse through the selected words
            for word in selected_words:
                # Add garbage to each word
                word = "".join([letter + garbage_chars[random.randint(0, len(garbage_chars) - 1)] for letter in word])

                # Append to the list
                garbage_words.append(word)

            # Create the challenge
            challenge = " ".join(garbage_words) + '\n'

            # Create the instructions
            message = ""
            message += "Remove the numbers and special characters (except for spaces) from the string "
            message += "and send it back to recieve a flag. You have 2 seconds to respond.\n"

            # Send the instructions
            self.send(message.encode())

            # Send the challenge itself
            self.send(challenge.encode())

            # Start the timer
            start_time = time.time()

            # Receive the response
            client_response = self.recv().decode()

            # Stop the timer
            stop_time = time.time() - start_time

            # Validate the client's response
            if client_response == answer and stop_time <= reaction_threshold:
                # Create the server's response
                server_response = "Here is your flag -> {}\n".format(flag)

                # Send the response
                self.send(server_response.encode())

                # Exit the challenge
                return
            elif client_response == answer and stop_time > reaction_threshold:
                # Create the server's response
                server_response = ""
                server_response += "Your answer was correct, "
                server_response += "but your response was too slow at {} seconds. ".format(stop_time)
                server_response += "Please try again.\n"

            else:
                # Create the server's response
                server_response = ""
                server_response += "Sorry <{}> was incorrect, ".format(client_response)
                server_response += "the correct answer was <{}>\n".format(answer)

            # Send the response
            self.send(server_response.encode())

            # Restart the challenge
            continue


class UpperAndLower(ChallengeAbstract):
    def __init__(self, client_communication):
        # Call superclasses' __init__ method
        super().__init__(client_communication)

        # Create reference to module's private word list
        self.word_list = WORD_LIST

    def run(self):
        # Define the challenge's flag
        flag = flags['uplow']

        # Define the number of words used for this challenge
        num_words = 20

        # Create the instructions message
        message = ""
        message += "Let's play a game of upper and lower! "
        message += "I will send you a list of words. "
        message += "Within the list, one of the words will either be the unique lowercase or lowercase word.\n"
        message += "Send back the unique word in the list for the flag!\n"

        # Send the instructions
        self.send(message.encode())

        # Keep running until the challenge is done
        while True:
            # Randomly select words from the wordlist
            selected_words = [WORD_LIST[random.randint(0, len(WORD_LIST) - 1)] for _ in range(0, num_words)]

            # Randomly select upper or lower
            coin_flip = random.randint(0, 1)

            # Unique word is upper with 0, and unique word is lower is 1
            if coin_flip == 0:
                # Lowercase all the words in the list
                selected_words = [_.lower() for _ in selected_words]

                # Randomly select a word to uppercase
                random_index = random.randint(0, len(selected_words) - 1)

                # Uppercase the word
                selected_words[random_index] = selected_words[random_index].upper()

                # Save the answer
                answer = selected_words[random_index]
            else:
                # Uppercase all the words in the list
                selected_words = [_.upper() for _ in selected_words]

                # Randomly select a word to lowercase
                random_index = random.randint(0, len(selected_words) - 1)

                # Lowercase the word
                selected_words[random_index] = selected_words[random_index].lower()

                # Save the answer
                answer = selected_words[random_index]

            # Create the challenge
            challenge = " ".join(selected_words) + '\n'

            # Send the message
            self.send(challenge.encode())

            # Receive the client's response
            client_response = self.recv().decode()

            if client_response == answer:
                # Challenge is completed
                break
            else:
                # Create the server response
                message = "Try again! The answer was <{}>\n".format(answer)

                # Send the server response
                self.send(message.encode())

        # Create flag message with completion of message
        server_response = "Here is your flag -> {}\n".format(flag)

        # Send the flag message
        self.send(server_response.encode())

# NOT FINISHED
class UpperAndLower2(ChallengeAbstract):
    """ TO BE UPDATED """
    def __init__(self, client_communication):
        # Call superclasses' __init__ method
        super().__init__(client_communication)

        # Create reference to module's private word list
        self.word_list = WORD_LIST

    def run(self):
        # Define the challenge's flag
        flag = flags[flag2]

        # Define the number of words used for this challenge
        num_words = 20

        # Define the number of consecutive correct answers for a flag
        answer_threshold = 10

        # Define a container for the number of successful consecutive answers
        answer_counter = 0

        # Create the instructions message
        message = ""
        message += "Let's play a game of upper and lower! "
        message += "I will send you a list of words. "
        message += "Within the list, one of the words will either be the unique lowercase or lowercase word.\n"
        message += "You need to send !\n"

        # Send the instructions
        self.send(message.encode())

        # Keep running until the challenge is done
        while answer_counter < answer_threshold:
            # Randomly select words from the wordlist
            selected_words = [WORD_LIST[random.randint(0, len(WORD_LIST) - 1)] for _ in range(0, num_words)]

            # Randomly select upper or lower
            coin_flip = random.randint(0, 1)

            # Unique word is upper with 0, and unique word is lower is 1
            if coin_flip == 0:
                # Lowercase all the words in the list
                selected_words = [_.lower() for _ in selected_words]

                # Randomly select a word to uppercase
                random_index = random.randint(0, len(selected_words) - 1)

                # Uppercase the word
                selected_words[random_index] = selected_words[random_index].upper()

                # Save the answer
                answer = selected_words[random_index]
            else:
                # Uppercase all the words in the list
                selected_words = [_.upper() for _ in selected_words]

                # Randomly select a word to lowercase
                random_index = random.randint(0, len(selected_words) - 1)

                # Lowercase the word
                selected_words[random_index] = selected_words[random_index].lower()

                # Save the answer
                answer = selected_words[random_index]

            # Create the challenge
            challenge = " ".join(selected_words) + '\n'

            # Send the message
            self.send(challenge.encode())

            # Receive the client's response
            client_response = self.recv().decode()

            if client_response == answer:
                # Challenge is completed
                break
            else:
                # Create the server response
                message = "Try again! The answer was <{}>\n".format(answer)

                # Send the server response
                self.send(message.encode())

        # Create flag message with completion of message
        server_response = "Here is your flag -> {}\n".format(flag)

        # Send the flag message
        self.send(server_response.encode())


class Copycat(ChallengeAbstract):
    def __init__(self, client_communication):
        # Call superclasses' __init__ method
        super().__init__(client_communication)

        # Create reference to module's private word list
        self.word_list = WORD_LIST

    def run(self):
        # Define the challenge's flag
        flag = flags['copycat']

        # Define the number of words for the challenge
        word_num = 21

        # Define the number of correct consecutive answers for the flag
        answer_threshold = 100

        # Define a contaienr to keep track the number of consecutive correct answers
        correct_answer_counter = 0

        # Create the instructions message
        message = ""
        message += "Let's play a game of copycat! "
        message += "Your job is to just simply repeat back to me the list of words I send you.\n"
        message += "You must do this consecutively and correctly for a total of <{}> times.\n".format(answer_threshold)

        # Send the instructions message
        self.send(message.encode())

        # Keep running until he challenge is done
        while True:
            # Create the status update message
            message = ""
            message += "You have sent me <{}> responses in a row correctly.\n".format(correct_answer_counter)

            # Send the status update message
            self.send(message.encode())

            # Randomly select the words
            selected_words = [WORD_LIST[random.randint(0, len(WORD_LIST) - 1)] for _ in range(0, word_num)]

            # Create the answer and challenge
            answer = " ".join(selected_words)
            challenge = answer + '\n'

            # Send the challenge
            self.send(challenge.encode())

            # Receive the client's response
            client_response = self.recv().decode()

            if client_response.strip() == answer:
                # Create the server's response
                message = ""
                message += "Correct!\n"

                # Increment the tracker
                correct_answer_counter += 1
            else:
                # Create the server's response
                message = ""
                message += "Sorry the answer was: {}\n".format(answer)

                # Set the tracker to 0
                correct_answer_counter = 0

            # Send the server's response
            self.send(message.encode())

            # Once the threshold is met, exit the challenge
            if correct_answer_counter == answer_threshold:
                break

        # Create flag message with completion of message
        server_response = "Here is your flag -> {}\n".format(flag)

        # Send the flag message
        self.send(server_response.encode())


class RotN(ChallengeAbstract):
    def __init__(self, client_communication):
        # Call superclasses' __init__ method
        super().__init__(client_communication)

        # Create reference to module's private word list
        self.word_list = WORD_LIST

    @staticmethod
    def shift_word(word, shift):
        n = shift % 26
        UC = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.encode()
        LC = 'abcdefghijklmnopqrstuvwxyz'.encode()
        trans = bytes.maketrans(UC + LC, UC[n:] + UC[0:n] + LC[n:] + LC[0:n])
        # print((UC+LC))
        # print(UC[n:]+UC[0:n]+LC[n:]+LC[0:n])
        return word.translate(trans)

    def run(self):
        # Define the flag
        flag = flags['rotten']

        # Define the number of words for each rot-n cypher
        word_num = 14

        # Define the number of correct answers to complete the challenge
        correct_answer_threshold = 50

        # Create a container to count the number of correct answers
        correct_answer_count = 0

        # Create the instructions
        message = ""
        message += "I have ROT-N ciphered some random words. Each word has a different shift. "
        message += "Decipher them and send them back\n"

        # Send the instructions
        self.send(message.encode())

        # Keep running until the challenge is complete
        while correct_answer_count < correct_answer_threshold:
            # Create the status update message
            message = ""
            message += "You have answered {}/50 correctly\n".format(correct_answer_count)
            message += "Decrypt this and send it back: \n"

            # Send the status update
            self.send(message.encode())

            # Randomly choose word list indices to get words from
            indices_list = [random.randint(0, len(self.word_list) - 1) for _ in range(0, word_num)]

            # Extract the words from the word list
            selected_words = [self.word_list[index] for index in indices_list]

            # Save the answer
            answer = " ".join(selected_words)

            # Apply a rot-n cipher on the selected words
            selected_words = [self.shift_word(word, random.randint(1, 25)) for word in selected_words]

            # Convert the ciphered word list into a string
            challenge = " ".join(selected_words) + '\n'

            # Send the challenge
            self.send(challenge.encode())

            # Receive the response
            client_response = self.recv().decode()

            # Validate the client's response
            if client_response == answer:
                # Create the server's response
                server_response = "Correct!\n".format(flag)

                # Increment the correct answer counter
                correct_answer_count += 1
            else:
                # Create the server's response
                server_response = ""
                server_response += "Sorry <{}> was incorrect, ".format(client_response)
                server_response += "the correct answer was <{}>\n".format(answer)

            # Send the response
            self.send(server_response.encode())

        # Create flag message with completion of message
        server_response = "Here is your flag -> {}\n".format(flag)

        # Send the flag message
        self.send(server_response.encode())


class WordAssociation(ChallengeAbstract):
    def __init__(self, client_communication):
        # Call superclasses' __init__ method
        super().__init__(client_communication)

        # Create reference to module's private word list
        self.word_list = WORD_LIST

    def run(self):
        # Define the flag
        flag = flags['wordassociation']

        # Define the total number of association questions for the game
        num_associations = 50

        # Define the threshold for the number of concurrent right answers for the flag
        flag_threshold = 50

        # Define the threshold for the number of concurrent wrong answers for reset
        reset_threshold = 50

        # Create container for the current number of answers in a row
        num_correct_answers = 0

        # Create container for the correct number of wrong answers in a row
        num_wrong_answers = 0

        # Select the words for word association
        random_indices = random.sample(range(len(WORD_LIST) - 1), num_associations * 2)
        word_set = [WORD_LIST[_] for _ in random_indices]

        # Create the instructions
        message = ""
        message += "Lets play a game of Word Association to test your (virtual) memory! "
        message += "To get the flag, you need to get {} correct associations in a row. \n".format(flag_threshold)
        message += "If you get more than {} associations wrong in a row, the game will reset. ".format(reset_threshold)
        message += "For every wrong answer, you will receive what the correct response was. "
        message += "Now lets begin!\n"

        # Send the instructions
        self.send(message.encode())

        # Keep running until flag conditions met
        while num_correct_answers < flag_threshold:
            # Create update message
            message = ""
            message += "You have {}/{} consecutive correct answers ".format(num_correct_answers, flag_threshold)
            message += "and {}/{} consecutive incorrect ones!\n".format(num_wrong_answers, reset_threshold)

            # Send the update message
            self.send(message.encode())

            # Grab a word pair
            random_index = random.randint(0, num_associations - 1) * 2
            word_association = (word_set[random_index], word_set[random_index + 1])

            # Create the challenge question
            message = ""
            message += "{}?\n".format(word_association[0])

            # Send the challenge
            self.send(message.encode())

            # Get the response
            client_response = self.recv().decode()

            # Validate the client's response
            if client_response == word_association[1]:
                # Create the server response message
                message = "Correct!\n"

                # Send the message
                self.send(message.encode())

                # Adjust the counters
                num_wrong_answers = 0
                num_correct_answers += 1
            else:
                # Create the server response message
                message = "Incorrect! The answer was {}\n".format(word_association[1])

                # Send the message
                self.send(message.encode())

                # Adjust the counters
                num_wrong_answers += 1
                num_correct_answers = 0

            # If reset threshold is met
            if num_wrong_answers == reset_threshold:
                # Create the response message
                message = "You have answered too many questions in a row wrong. Challenge is resetting...\n"

                # Send the message
                self.send(message.encode())

                # Exit the challenge
                return

            # Delay for a small time
            time.sleep(0.05)

        # Once challenge is complete, send the flag!
        server_response = "Here is your flag -> {}\n".format(flag)

        # Send the flag message
        self.send(server_response.encode())


class RotTheBass(ChallengeAbstract):
    def __init__(self, client_communication):
        # Call superclasses' __init__ method
        super().__init__(client_communication)

        # Create reference to module's private word list
        self.word_list = WORD_LIST

    @staticmethod
    def rotn(word, shift):
        n = shift % 26
        UC = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.encode()
        LC = 'abcdefghijklmnopqrstuvwxyz'.encode()
        trans = bytes.maketrans(UC + LC, UC[n:] + UC[0:n] + LC[n:] + LC[0:n])
        # print((UC+LC))
        # print(UC[n:]+UC[0:n]+LC[n:]+LC[0:n])
        return word.translate(trans)

    def run(self):
        # Define the flag for the challenge
        flag = flags['rotbass']

        # Define the number of the words for the challenge
        num_words = 2

        # Define the time threshold to complete the threshold
        time_threshold = 2

        # Create instruction message
        message = ""
        message += "I have encoded <{}> words seperated by a space in the following method: ".format(num_words)
        message += "uppercase word -> base64 -> rot-N -> uppercase\n"
        message += "Send back the decoded message in <{}> seconds for a flag\n".format(time_threshold)

        # Send the instruction message
        self.send(message.encode())

        # Keep running until challenge completed
        while True:
            # Grab two random words from the word list
            random_indices = random.sample(range(len(WORD_LIST) - 1), num_words)
            selected_words = [WORD_LIST[_] for _ in random_indices]

            # Save the answer
            answer = " ".join(selected_words)

            # Create the challenge
            challenge = " ".join(selected_words)
            challenge = challenge.upper()
            challenge = __import__("base64").b64encode(challenge.encode())
            challenge = self.rotn(challenge.decode(), random.randint(1, 25))
            challenge = challenge.upper() + "\n"


            # Send the challenge
            self.send(challenge.encode())

            # Get the start time
            start_time = time.time()

            # Receive the answer
            client_response = self.recv().decode()

            # Get the stop time
            stop_time = time.time() - start_time

            # Validate answer
            if client_response == answer and stop_time <= time_threshold:
                # Challenge complete!
                break

            elif client_response == answer and stop_time <= time_threshold:
                # Create the response message
                message = "Your answer was correct, but you were too slow\n"

            else:
                # Create the response message
                message = "Sorry, the correct answer was {}\n".format(answer)

            # Send the response
            self.send(message.encode())

        # Create flag message with completion of message
        server_response = "Here is your flag -> {}\n".format(flag)

        # Send the flag message
        self.send(server_response.encode())


class Substitution(ChallengeAbstract):
    def __init__(self, client_communication):
        # Call superclasses' __init__ method
        super().__init__(client_communication)

        # Create reference to module's private word list
        self.word_list = WORD_LIST

    def run(self):
        # Define the challenge's flag
        flag = flags['subcipher']

        # Define standard charset
        char_set = "ABCDEFGHIJKMNOPQRSTUVWXYZ"

        # Define the time limit for completing the challenge
        time_threshold = 3

        # Define the number of words for the challenge
        num_words = 15

        # Keep running until the challenge is done
        while True:
            # Create the instructions message
            message = ""
            message += "I have applied a substitution cipher to a string of random words, "
            message += "decipher it correctly for a flag, you have <{}> seconds\n".format(time_threshold)

            # Send the instructions
            self.send(message.encode())

            # Grab a randomised list of words from the word list
            random_words = " ".join([WORD_LIST[random.randint(0, len(WORD_LIST) - 1)] for _ in range(num_words)])

            # Save the answer
            answer = random_words

            # Create a randomised version of the charset
            random_char_set = [_ for _ in char_set]
            random.shuffle(random_char_set)

            # Create a translator
            translator = {orig_char: new_char for orig_char, new_char in zip(char_set, random_char_set)}

            # Translate the string
            challenge = "".join([translator[char] if char in translator else char for char in random_words]) + '\n'

            # Send the challenge
            self.send(challenge.encode())

            # Start the timer
            start_time = time.time()

            # Receive the client's response
            client_response = self.recv().decode()

            # Get the response time
            response_time = time.time() - start_time

            # Validate the response
            if client_response == answer and response_time <= time_threshold:
                # Challenge complete!
                break
            elif client_response == answer and response_time > time_threshold:
                # Create the server response message
                server_response = ""
                server_response += "You were correct... "
                server_response += "but too slow with a response time of <{}>!\n".format(response_time)
                server_response += "The correct response was <{}>\n".format(answer)

                # Send the server response message
                self.send(server_response.encode())

            else:
                # Create the server response message
                server_response = ""
                server_response += "Your answer was incorrect, the correct response was {}\n".format(answer)

                # Send the server response message
                self.send(server_response.encode())

        # Create flag message with completion of message
        server_response = "Here is your flag -> {}\n".format(flag)
        server_response += "you solved in <{}>!\n".format(response_time)

        # Send the flag message
        self.send(server_response.encode())
