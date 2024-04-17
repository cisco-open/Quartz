# MIT License

# Copyright (c) 2024 Cisco Systems, Inc. and its affiliates

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


from __future__ import print_function

import socket
import ssl
import platform
import subprocess
import requests

from OpenSSL import SSL, _util
from itertools import count

def getHostCipherSuite():
    os = platform.system()
    if os == 'Windows':
        process = subprocess.run(["powershell.exe", "Get-TlsCipherSuite | Format-Table -Property Name"], stdout=subprocess.PIPE)
        cmd_output = process.stdout.decode('utf-8')
        cipher_suite = [x.strip() for x in cmd_output.split('\n')[3:-3]]
    elif os == 'Linux':
        process = subprocess.run(["openssl", "ciphers", "-v"], stdout=subprocess.PIPE)
        cmd_output = process.stdout.decode('utf-8')
        cipher_suite = [x.split()[0] for x in cmd_output.split('\n')[:-1]]
    else:
        process = subprocess.run(["openssl", "ciphers", "-v"], stdout=subprocess.PIPE)
        cmd_output = process.stdout.decode('utf-8')
        cipher_suite = [x.split()[0] for x in cmd_output.split('\n')[:-1]]
    return cipher_suite

def getSharedCipherSuite(server):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssl_sock = ssl.wrap_socket(sock)
    ssl_sock.connect(server)
    return [x[0] for x in ssl_sock.shared_ciphers()] # shared_ciphers returns cipher_suite sent by the client during tls handshake

#Loading config.json file
script_dir = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(script_dir,'..','config.json')
with open(config_path,'r') as config_file:
    config_data = json.load(config_file)

def checkPQSafety(server):
    host_cipher_suite = getHostCipherSuite()
    api_host = config_data['FLASK_HOST']+'/getHostSecurity'
    response = requests.post(api_host,json={"cipher_suite":host_cipher_suite})
    is_host_safe = response.json()['is_safe']
    shared_cipher_suite = getSharedCipherSuite(server)
    response = requests.post(api_host,json={"cipher_suite":shared_cipher_suite})
    is_host_safe = is_host_safe and response.json()['is_safe']
    api_host = config_data['FLASK_HOST']+'/getServerSecurity'
    response = requests.post(api_host,json={"server":server[0]})
    is_server_safe = response.json()['is_safe']
    return is_host_safe and is_server_safe

print(checkPQSafety(("google.com",443)))

