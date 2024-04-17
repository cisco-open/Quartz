# MIT License

# Copyright (c) 2024 Cisco Systems, Inc. and its affiliates

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Inbuilt modules
from threading import Thread
from datetime import datetime
from git import RemoteProgress
import json
import os
import logging
import git

#Loading config.json file
script_dir = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(script_dir,'..','..','config.json')
with open(config_path,'r') as config_file:
    config_data = json.load(config_file)
# TLS Scanner Repo Link
scanner_repo = config_data['SCANNER_REPO']
cloned_path = '/tmp/testssl.sh'

logging.basicConfig(level=logging.DEBUG)

class CloneProgress(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        if message:
            print(message)

def clone(repo):
    print('Cloning into %s' % repo)
    local_path = "/tmp"
    try:
        git.Repo.clone_from(repo, local_path, branch='main', progress=CloneProgress())
    except ConnectionError:
        print("Connection failed!!")
        raise ConnectionError

def checkPQSafety(file_name):
    scan_out_file = open(file_name, 'r')
    scan_output = json.loads(scan_out_file.read())
    scan_out_file.close()
    #print(output['ciphers'][0]['cipher_suites'])
    cipher_suite = []
    for entry in scan_output['scanResult']:
        for server_preference in entry['serverPreferences']:
            if server_preference['id'].startswith('supportedciphers') or server_preference['id'].startswith('cipherorder'):
                for algo in server_preference['finding'].split():
                    cipher_suite.append(algo)
    return cipher_suite

def getScanAnalysis(api_host, port, protocol, file_name, type):
    json_out = file_name
    protocol_option = ''
    port_option = ''
    server_preference_option = ' '
    if type != 'full':
        server_preference_option = " -P "
    if protocol != "" and protocol is not None:
        protocol_option = " -t " + protocol
    if port != "":
        port_option = ":" + str(port) 
    cmd = "/tmp/testssl.sh/testssl.sh --quiet" + server_preference_option + "-oJ " + json_out + protocol_option + " " + api_host + port_option + " 1>/dev/null"
    os.system(cmd)
    return

def apiScanInitiate(host, port, protocol, type):
    # Check if the bash script is present, download the repo if not present
    if not os.path.exists('/tmp/testssl.sh'):
        try:
            clone(scanner_repo)
        except:
            logging.error("Failed to clone repository")
            return "Failed"
    # Generate file name to store scan output
    now = datetime.now()
    json_out = host + '_' + now.strftime("%Y%m%d-%H%M") + '.json'

    # Call script to run scan
    getScanAnalysis(host, port, protocol, json_out, type)
        #proc = subprocess.Popen(["python3 ./microservices/api_cipher_suite.py " + options], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
    return json_out

# if __name__=='__main':
#     parser = createParser()
#     # Parse the argument
#     args = parser.parse_args()
#     apiScanInitiate(args)


