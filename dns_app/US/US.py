from flask import Flask, request, jsonify
import requests
import socket

app = Flask(__name__)  # Create a new Flask web application instance

@app.route('/')
def hello_world():
    return 'Hello World!'

# Function to resolve a given hostname to an IP address using a custom DNS query
def resolve_hostname_to_ip(hostname, as_ip, as_port):
    try:
        dns_query = f"TYPE=A\nNAME={hostname}"
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create a new UDP socket
        sock.sendto(dns_query.encode(), (as_ip, int(as_port)))  # Send the DNS query

        response, _ = sock.recvfrom(2048)
        sock.close()

        # Parse the DNS response
        dns_response_lines = response.decode().split("\n")

        if dns_response_lines and dns_response_lines[0] == "TYPE=A":
            ip_address = dns_response_lines[2].split("=")[1]  # Extract the IP address from the response
            return ip_address
        else:
            return None
    except Exception as e:
        print(f"An error occurred during DNS resolution: {e}")
        return None

# Function to request a Fibonacci number from another server
def get_fibonacci_number(fs_ip, fs_port, number):
    try:
        # Send a request to the Fibonacci server
        response = requests.get(f"http://{fs_ip}:{fs_port}/fibonacci?number={number}")

        if response.status_code == 200:
            return response.text
        else:
            return None
    except Exception as e:
        print(f"An error occurred during the Fibonacci request: {e}")
        return None

@app.route('/fibonacci')  # Define the route for the Fibonacci endpoint
def fibonacci():
    # Retrieve query parameters from the URL
    hostname = request.args.get('hostname')
    fs_port = request.args.get('fs_port')
    number = request.args.get('number')
    as_ip = request.args.get('as_ip')
    as_port = request.args.get('as_port')

    # Validate that all required parameters are present
    if not hostname or not fs_port or not number or not as_ip or not as_port:
        return jsonify(error="Bad Request", message="Missing parameters"), 400

    fs_ip = resolve_hostname_to_ip(hostname, as_ip, as_port)
    if not fs_ip:
        return jsonify(error="Internal Server Error", message="DNS query failed"), 500

    # Request the Fibonacci number from the other server
    fib_number = get_fibonacci_number(fs_ip, fs_port, number)
    if fib_number is None:
        return jsonify(error="Internal Server Error", message="Fibonacci request failed"), 500

    return fib_number, 200  # If everything was successful, return the Fibonacci number

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
