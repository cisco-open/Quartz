# MIT License

# Copyright (c) 2024 Cisco Systems, Inc. and its affiliates

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Inbuilt modules
from git import RemoteProgress
from datetime import datetime
from urllib.parse import urlparse
import json
import os
import argparse
import git
import logging
import requests

# Flask imports
import mysql.connector as connector
from mysql.connector import Error


logging.basicConfig(level=logging.DEBUG)

scanner_path = "/tmp/testssl.sh"

class CloneProgress(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        if message:
            print(message)

def clone(repo, local_path):
    """
    Takes a repository name and local directory as input and clones it.

    Input: 
        - repo : string
        - local_path: string
    Output: Prints the cloning progress status to STD OUT
    """

    logging.info('Cloning into %s' % repo)
    try:
        git.Repo.clone_from(repo, local_path, branch='3.0', progress=CloneProgress())
    except ConnectionError:
        print("Connection failed!!")
        raise ConnectionError

def getScanner():
    """
    Download the testtls.sh script if not already downloaded.

    Input: N/A
    Output: N/A
    """

    if not os.path.exists(scanner_path):
        logging.info(f"TLS Scanner not found in {scanner_path}")
        logging.info("Cloning: https://github.com/drwetter/testssl.sh.git")
        clone("https://github.com/drwetter/testssl.sh.git", scanner_path)
    else:
        logging.info(f"TLS Scanner found in {scanner_path}")
    logging.info("Proceeding to scan")
    return

def checkPQCSafety(cipher_list):
    """
    Takes a TLS cipher suite list as input and checks the cipher suite against stored information to determine PQC status.

    Input: 
        - cipher_list : list of cipher suites
    Output: 
        - is_safe : Boolean value, True if all cipher_suites are PQC safe
        - tls_algo_record : List of TLS cipher suite records with all associated details
    """
    # Update cipher suite details
    # Read cipher suite details from static JSON file
    cipher_suite_details_file = open('pqc_cipher_info.json', 'r')
    cipher_suite_details = json.loads(cipher_suite_details_file.read())
    cipher_suite_details_file.close()

    # Parse the cipher suite list against the existing information and store the results
    output = []
    pqc_safe = True
    for cipher in cipher_list:
        cipher_suite_record = cipher_suite_details[cipher]
        if cipher_suite_record['pqc_safe'] == False:
            pqc_safe = False
        output.append({"name":cipher, "pqc_safe":cipher_suite_record['pqc_safe'], "risk_factor":cipher_suite_record['risk_factor'], "remediation":cipher_suite_record['remediation']})
    return {'is_safe': pqc_safe, "tls_algo_record": output}

def getScanAnalysis(scan_target, scan_target_port, scan_target_protocol):
    """
    Scans remote API as per the target, port and protocol details provided as input.

    Input: 
        - scan_target : string
        - scan_target_port : string
        - scan_targert_protocol : string
    Output: Returns a dictionary with two keys:
    - scan_result : List of three dictionaries containing details of identified cipher suites, safe/unsafe components, and pie chart details
    - graph : Details of nodes and edges for generating dependency graph
    - scan_details : List of dictionary with scan status information
    """
    # Parse input host name to extract domain name
    domain = ''
    if scan_target.find('/') != -1:
        domain = urlparse(scan_target).netloc
    else:
        domain = scan_target

    # Create JSON filename to store scan results
    file_now = datetime.now()
    json_out = domain + '_' + file_now.strftime("%Y%m%d-%H%M") + '.json'

    # Determine protocol and port command options if input is specified
    protocol_option = ''
    port_option = ''
    if scan_target_protocol != "":
        protocol_option = " -t " + scan_target_protocol
    if scan_target_port != "":
        port_option = ":" + scan_target_port 
    
    # Command to be executed for calling the script
    cmd = "/tmp/testssl.sh/testssl.sh -P --openssl-timeout 2 -oJ " + json_out + protocol_option + " " + domain + port_option

    # Execute the command and wait for the results
    try:
        os.system(cmd)
        #pass
    except:
        return "Failed to execute scan!"
    
    # Read the JSON output file 
    scan_out = open(json_out, 'r')
    scan_output = json.loads(scan_out.read())
    scan_out.close()

    # Delete the file since we don't need it anymore
    os.system("rm " + json_out)

    # Parse the JSON file output to extract cipher suite details
    cipher_suite = {}
    try:
        if scan_output['scanTime'] == "Scan interrupted":
            print("2")
            return scan_output['scanResult'][0]['finding']
        for entry in scan_output['scanResult']:
            for server_preference in entry['serverPreferences']:
                if server_preference['id'].startswith('supportedciphers') or server_preference['id'].startswith('cipher_order_TLS') or server_preference['id'].startswith('cipherorder_TLS'):
                    tls_protocol = ''
                    if server_preference['id'] == 'cipherorder_TLSv1_3' or server_preference['id'] == 'cipher_order_TLSv1.3':
                        tls_protocol = 'TLSv13'
                    elif server_preference['id'] == 'cipherorder_TLSv1_2' or server_preference['id'] == 'cipher_order_TLSv1.2':
                        tls_protocol = 'TLSv12'
                    elif server_preference['id'] == 'cipherorder_TLSv1_1' or server_preference['id'] == 'cipher_order_TLSv1.1':
                        tls_protocol = 'TLSv11'
                    else:
                        tls_protocol = ''
                    if server_preference['id'].startswith('cipherorder'):
                        for algo in server_preference['finding'].split():
                            cipher_suite[algo] = tls_protocol
                    elif server_preference['id'].startswith('cipher_order'):
                        cipher_suite[server_preference['finding'].split()[0]] = tls_protocol
    except:
        return "Failed to scan target API"
    
    cipher_list = [x for x in cipher_suite.keys()]

    # Check each cipher suite details
    safety_check = checkPQCSafety(cipher_list)

    # Use the cipher suite details to generate the dependency graph
    nodes = []
    edges = []
    # Root node
    nodes.append({"id":scan_target, "size":1500})

    # Level 1 nodes for TLS protocols found
    for tls_protocol in set(cipher_suite.values()):
        nodes.append({"id":tls_protocol, "size": 800})
        edges.append({"source":scan_target, "target":tls_protocol})
    
    # Variables to count safe and unsafe records
    safe = 0
    unsafe = 0
    safe_risk_factor = 0
    unsafe_risk_factor = 0
    global_risk_factor = 0
    detectors = []

    # Parse the cipher suite list to generate edges and add level 2 nodes with the cipher suite names
    for tls_record in safety_check['tls_algo_record']:
        if tls_record['pqc_safe'] == True: #and cipher_suite[tls_record['name']]=='TLSv13'
            detectors.append({
                'name': tls_record['name'],
                'remediation': tls_record['remediation'],
                'risk_factor': tls_record['risk_factor'],
                'tls_version': cipher_suite[tls_record['name']],
                'quantum_safe': 'Yes'
            })
            safe += 1
            safe_risk_factor += float(tls_record['risk_factor'])
            nodes.append({"id":tls_record['name'],"color":"green"})
            edges.append({"source":cipher_suite[tls_record['name']], "target":tls_record['name']})
        else:
            detectors.append({
                'name': tls_record['name'],
                'remediation': tls_record['remediation'],
                'risk_factor': tls_record['risk_factor'],
                'tls_version': cipher_suite[tls_record['name']],
                'quantum_safe': 'No'
            })
            unsafe += 1
            unsafe_risk_factor += float(tls_record['risk_factor'])
            nodes.append({"id":tls_record['name'], "color":"red"})
            edges.append({"source":cipher_suite[tls_record['name']], "target":tls_record['name']})
    stats = [{'Safe': safe, 'Unsafe': unsafe}]
    pie_chart_data = [{ "title": 'safe', "value": safe, "color": '#90EE90' }, { "title": 'unsafe', "value": unsafe, "color": '#F75D59' }]
        #print(pie_chart_data)
    if safe != 0 or unsafe != 0:
        global_risk_factor = round(unsafe_risk_factor/(unsafe+safe),2)
    scan_status = "Target: " + scan_target + (':' + scan_target_port + '; ' if scan_target_port != '' else '') + ("Protocol: " + scan_target_protocol if scan_target_protocol != '' else '') + "; Type: api; PQC Secure: " + ("No" if unsafe>0 else "Yes")
    return {"scan_result":[detectors,pie_chart_data,stats], "graph": {"nodes":nodes, "edges":edges}, "scan_details":[{"params":"Scan Details", "values" : scan_status}, {"params":"Quantum Risk Factor", "values":global_risk_factor}]}

def createParser():
    # Create the parser
    parser = argparse.ArgumentParser()
    # Add arguments
    parser.add_argument('--host', type=str, required=True)
    parser.add_argument('--port', type=str)
    parser.add_argument('--protocol', type=str)
    return parser

if __name__=='__main__':
    parser = createParser()
    # Parse the argument
    args = parser.parse_args()
    scan_target = args.host
    scan_target_port = args.port
    scan_target_protocol = args.protocol
    scan_results = getScanAnalysis(scan_target, scan_target_port, scan_target_protocol)
    print(scan_results)


