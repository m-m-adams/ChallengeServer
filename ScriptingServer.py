from BasicChallenges import BasicChallengeManager
from Communications import *
import threading
import sys

""" SET SERVER SETTINGS HERE """
try:
    SERVER_BIND_ADDR = sys.argv[1]
    SERVER_PORT = int(sys.argv[2])

except Exception as error_message:
    print("[!] Either no arguments supplied or incorrect formatting! Using server defaults...")
    SERVER_BIND_ADDR = "0.0.0.0"
    SERVER_PORT = 8001

""" END OF SETTINGS SECTION"""


class ScriptingVault:
    def __init__(self, bind_address, bind_port):
        print("### Scripting Vault ###")
        print("Bind Address: <{}> Port:<{}>".format(bind_address, bind_port))

        # Create the server
        self.server = Server(bind_address, bind_port)

        # Create challenges manager
        self.challenges_manager = BasicChallengeManager()

    def run(self):
        # Display running state
        print("Notice: Server is now <Running>")
        try:
            # Keep running server until the server is stopped
            while True:
                # Wait for connection
                FoundClient=False
                self.server.s.settimeout(2)
                while not FoundClient:
                    try:
                        client = self.server.accept_connection()
                        FoundClient = True
                    except socket.timeout:
                        # don't do anything but also don't print the error
                        pass
                    except KeyboardInterrupt:
                        print('user interrupt, server closing')
                        self.server.s.close()
                        sys.exit()


                # Retrieve connection information
                ip_addr, port_num = client.get_addr()

                # Display new connection
                print("Notice: Connection received from <{}:{}>".format(ip_addr, port_num))

                # Create thread for new client
                thread = threading.Thread(target=self.client_thread, args=(client,))

                #make the thread a daemon so it exits when the main program does
                thread.isDaemon()
                # Run thread
                thread.start()
        except KeyboardInterrupt:
            print('user interrupt, server closing')
            self.server.s.close()
            sys.exit()


    def client_thread(self, client):
        try:
            # Keep running until connection ends
            while True:
                # Get the number of challenges
                num_challenges = self.challenges_manager.get_num_challenges()

                # Create the introduction message
                message = ""
                message += "Welcome to the scripting vault! Please select a level (1-{}):\n".format(num_challenges)

                # Send introduction
                client.send(message.encode())

                # Receive level selection from client
                client_response = client.recv().decode()

                # Poll challenges manager for level
                challenge_class = self.challenges_manager.retrieve_challenge(client_response)

                # Send appropriate response to client selection
                if challenge_class is not None:
                    # Create success message for client
                    #server_response = "Here is your level <{}> challenge!\n".format(client_response)
                    pass
                    # Send success message to client
                    #client.send(server_response.encode())
                else:
                    # Create error message for client
                    server_response = "Sorry, but <{}> is not a valid selection! Please try again!\n".format(
                        client_response)

                    # Send the error message to client
                    client.send(server_response.encode())

                    # Return back to introduction
                    continue

                # Initialise challenge
                challenge = challenge_class(client)

                # Run the challenge
                challenge.run()

        except socket.error:
            # Retrieve client information
            ip_addr, port_num = client.get_addr()

            # Display disconnect information
            print("Notice: Client <{}:{}>  has disconnected.".format(ip_addr, port_num))


if __name__ == '__main__':
    # Setup server
    script_vault = ScriptingVault(SERVER_BIND_ADDR, SERVER_PORT)

    # Run server

    script_vault.run()


