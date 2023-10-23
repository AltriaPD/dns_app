from flask import Flask, request
from flask.views import MethodView
import socket
import json

app = Flask(__name__)

class FibonacciServer(MethodView):
    def __init__(self):
        # Initializing the server's properties.
        self.hostname = None
        self.ip = None
        self.as_ip = None
        self.as_port = None

    def get(self):
        # Handling GET requests to the root URL.
        return 'Hello World!'

    def put(self):
        # Handling PUT requests for server registration.
        data = json.loads(request.data.decode())
        self.hostname = data.get('hostname')
        self.ip = data.get('ip')
        self.as_ip = data.get('as_ip')
        self.as_port = data.get('as_port')

        # Preparing the message for the Authoritative Server.
        udp_msg = f"TYPE=A\nNAME={self.hostname}\nVALUE={self.ip}\nTTL=10\n"

        try:
            # Using a context manager for the socket operations.
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                # Sending the registration data to the Authoritative Server.
                sock.sendto(udp_msg.encode(), (self.as_ip, int(self.as_port)))

                # Receiving and logging the response from the Authoritative Server.
                response, _ = sock.recvfrom(2048)
                response_data = response.decode()
                print(f"Response from AS: {response_data}")

            return 'Fibonacci server registered on the Authoritative Server!', 201

        except Exception as e:
            print(f"An error occurred: {e}")
            return 'Internal Server Error', 500

    def calculate_fibonacci(self, number):
        # A method to calculate Fibonacci numbers.
        if number <= 1:
            return number
        else:
            return self.calculate_fibonacci(number-1) + self.calculate_fibonacci(number-2)

@app.route('/fibonacci')
def get_fibonacci():
    try:
        number = int(request.args.get('number'))
        if number <= 0:
            raise ValueError("Number must be positive")

        server = FibonacciServer() 
        result = server.calculate_fibonacci(number)
        return str(result), 200

    except ValueError as e:
        return f'Bad Request - {str(e)}', 400

server_view = FibonacciServer.as_view('fibonacci_server')
app.add_url_rule('/', view_func=server_view, methods=['GET', 'PUT'])

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9090, debug=True)
