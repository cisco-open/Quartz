# MIT License

# Copyright (c) 2024 Cisco Systems, Inc. and its affiliates

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import sslscan
import argparse
import json
from sslscan.module.scan import BaseScan
from sslscan.module.report import BaseReport

def checkPQCSafety(cipher_list):
    # Update cipher suite details
    # Read cipher suite details from static JSON file
    cipher_suite_details_file = open('pqc_cipher_info.json', 'r')
    cipher_suite_details = json.loads(cipher_suite_details_file.read())
    cipher_suite_details_file.close()

    # Parse the cipher suite list against the existing information and store the results
    output = []
    pqc_safe = True
    for cipher in cipher_list:
        try:
            cipher_suite_record = cipher_suite_details[cipher]
            if cipher_suite_record['pqc_safe'] == False:
                pqc_safe = False
            output.append({"name":cipher, "pqc_safe":cipher_suite_record['pqc_safe'], "risk_factor":cipher_suite_record['risk_factor'], "remediation":cipher_suite_record['remediation']})
        except:
            continue
    return {'is_safe': pqc_safe, "tls_algo_record": output}

def getServerCipherSuites(server):

    """
    Takes a server address as input and returns details of TLS cipher suites shared by the server when TLS connection is initiated.

    Input: 
        - server : string
    Output: Returns a dictionary with TLS cipher_suite name as key and TLS protocol version as value
    """

    sslscan.modules.load_global_modules()

    scanner = sslscan.Scanner()

    for name in ["ssl2", "ssl3", "tls10", "tls11", "tls12"]:
        scanner.config.set_value(name, True)

    scanner.append_load('server.ciphers', '', base_class=BaseScan)
    module = scanner.load_handler_from_uri(server)
    scanner.set_handler(module)
    scanner.run()

    ciphers = scanner.get_knowledge_base().get('server.ciphers')
    if ciphers is None:
        return []
    cipher_suite = {}
    for cipher in ciphers:
        if cipher.status_name == 'accepted':
            cipher_suite[cipher.cipher_suite.name] = cipher.protocol_version_name
    return cipher_suite

def getServerScanAnalysis(scan_target):
    sslscan.modules.load_global_modules()

    scanner = sslscan.Scanner()

    for name in ["ssl2", "ssl3", "tls10", "tls11", "tls12"]:
        scanner.config.set_value(name, True)

    scanner.append_load('server.ciphers', '', base_class=BaseScan)
    module = scanner.load_handler_from_uri(scan_target)
    scanner.set_handler(module)
    scanner.run()

    ciphers = scanner.get_knowledge_base().get('server.ciphers')
    if ciphers is None:
        return []
    cipher_suite = {}
    for cipher in ciphers:
        if cipher.status_name == 'accepted':
            cipher_suite[cipher.cipher_suite.name] = cipher.protocol_version_name
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
    scan_status = "Target: " + scan_target + "; Type: api; PQC Secure: " + ("No" if unsafe>0 else "Yes")
    return {"scan_result":[detectors,pie_chart_data,stats], "graph": {"nodes":nodes, "edges":edges}, "scan_details":[{"params":"Scan Details", "values" : scan_status}, {"params":"Quantum Risk Factor", "values":global_risk_factor}]}

def createParser():
    # Create the parser
    parser = argparse.ArgumentParser()
    # Add arguments
    parser.add_argument('--host', type=str, required=True)
    return parser

if __name__=='__main__':
    parser = createParser()
    # Parse the argument
    args = parser.parse_args()
    scan_target = args.host
    scan_results = getServerScanAnalysis(scan_target)

    print(scan_results)

#print(getServerCipherSuites('google.com'))