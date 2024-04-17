# MIT License

# Copyright (c) 2024 Cisco Systems, Inc. and its affiliates

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import socket
import ssl
import platform
import subprocess
import argparse
#import requests

#from OpenSSL import SSL, _util
#from itertools import count

def getHostCipherSuite():

    """
    Returns details of natively supported TLS cipher suites on a system.

    Input: N/A
    Output: Returns a dictionary with cipher_suite names as key and TLS protocol version as the value
    """

    os = platform.system()
    if os == 'Windows':
        process = subprocess.run(["powershell.exe", "Get-TlsCipherSuite | Format-Table -Property Name"], stdout=subprocess.PIPE)
        cmd_output = process.stdout.decode('utf-8')
        cipher_suite = [x.strip() for x in cmd_output.split('\n')[3:-3]]
    elif os == 'Linux':
        process = subprocess.run(["openssl", "ciphers", "-v"], stdout=subprocess.PIPE)
        cmd_output = process.stdout.decode('utf-8')
        cipher_suite = {x.split()[0]:x.split()[1] for x in cmd_output.split('\n')[:-1]}
    else:
        process = subprocess.run(["openssl", "ciphers", "-v"], stdout=subprocess.PIPE)
        cmd_output = process.stdout.decode('utf-8')
        cipher_suite = {x.split()[0]:x.split()[1] for x in cmd_output.split('\n')[:-1]}
    return cipher_suite

def getSharedCipherSuite(server):

    """
    Takes a remote server address as input and returns details of TLS cipher suites shared while initiating a TLS connection.

    Input: 
        - server : tuple of host address and port number
    Output: Returns a dictionary with shared cipher suites as keys and TLS protocol version as the value
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssl_sock = ssl.wrap_socket(sock)
    ssl_sock.connect(server)
    return {x[0]:x[1] for x in ssl_sock.shared_ciphers()} # shared_ciphers returns cipher_suite sent by the client during tls handshake

def checkPQSafety(server):

    """
    Takes a remote server address and returns details of all cipher suites supported on the host and shared while creating TLS connection.

    Input: 
        - server : tuple of server address and port
    Output: Returns a dictionary with two keys:
    - host: dictionary of all natively supported cipher suites
    - shared: dictionary of all TLS cipher suites shared when a connection is initiated
    """

    host_cipher_suite = getHostCipherSuite()
    try:
        shared_cipher_suite = getSharedCipherSuite(server)
    except:
        shared_cipher_suite = host_cipher_suite
    return {"host" : host_cipher_suite, "shared" : shared_cipher_suite}


def createParser():
    # Create the parser
    parser = argparse.ArgumentParser()
    # Add arguments
    parser.add_argument('--host', type=str, required=True)
    parser.add_argument('--port', type=str, default="443")
    return parser

if __name__=='__main__':
    parser = createParser()
    # Parse the argument
    args = parser.parse_args()
    scan_target = args.host
    scan_target_port = int(args.port)
    scan_results = checkPQSafety((scan_target, scan_target_port))
    print(scan_results)


