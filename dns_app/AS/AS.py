import socket
import os

class DNSServer:
    def __init__(self, ip, port, dns_file):
        self.ip = ip
        self.port = port  
        self.dns_file = dns_file  
        self.dns_records = {}  
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Creating a UDP socket
        self.sock.bind((self.ip, self.port))

        # Check if the DNS records file exists, if not, create it. If it exists, load the records.
        if not os.path.exists(self.dns_file):
            with open(self.dns_file, 'w') as file:
                pass  # Create an empty file if it doesn't exist
        else:
            self.load_dns_records()

    # Function to load DNS records from the file into memory
    def load_dns_records(self):
        with open(self.dns_file, 'r') as file:
            for line in file:
                record_type, hostname, ip_address, ttl = line.strip().split(',')
                self.dns_records[hostname] = (record_type, ip_address, ttl)

    # Function to update the DNS records file with the current records from memory
    def update_dns_records(self):
        with open(self.dns_file, 'w') as file:
            for hostname, (record_type, ip_address, ttl) in self.dns_records.items():
                file.write(f"{record_type},{hostname},{ip_address},{ttl}\n")  # Write the updated records to the file

    # Function to handle incoming DNS queries
    def handle_dns_query(self, data, addr):
        fields = data.split("\n")
        record_type = fields[0].split('=')[1]
        hostname = fields[1].split('=')[1]

        # Check if the requested hostname exists in the records
        if hostname in self.dns_records:
            ip_address, ttl = self.dns_records[hostname][1:]
            response = f"TYPE={record_type}\nNAME={hostname}\nVALUE={ip_address}\nTTL={ttl}"
            self.sock.sendto(response.encode(), addr)  # Sending the response back to the client

    # Function to register a new DNS record received from a client
    def register_dns_record(self, data):
        fields = data.split("\n")
        record_type = fields[0].split('=')[1]
        hostname = fields[1].split('=')[1]
        ip_address = fields[2].split('=')[1]
        ttl = fields[3].split('=')[1]

        # Adding the new record to the dictionary
        self.dns_records[hostname] = (record_type, ip_address, ttl)
        self.update_dns_records()
        print(f"Registered DNS record:{hostname} -> {ip_address}")

    def run(self):
        try:
            print("DNS server is running...")
            while True:
                data, addr = self.sock.recvfrom(2048)  # Receiving data from the client
                decoded_data = data.decode()

                # Check the type of request and process it
                if decoded_data.startswith('TYPE=A'):
                    self.handle_dns_query(decoded_data, addr)
                else:
                    self.register_dns_record(decoded_data)

        except KeyboardInterrupt:
            print("DNS server has stopped")
            self.sock.close()

if __name__ == "__main__":
    server = DNSServer('0.0.0.0', 53533, 'dns_records.txt')
    server.run()


