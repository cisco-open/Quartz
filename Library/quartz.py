# MIT License

# Copyright (c) 2024 Cisco Systems, Inc. and its affiliates

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


from microservices import client_cipher_suite, server_cipher_suite, api_cipher_suite, repo_cipher_scan
from pq_safety_check import tls_checker

from time import sleep
import argparse
import logging
import sys
import os

def createParser():
    # Create the parser
    parser = argparse.ArgumentParser()
    # Add arguments
    parser.add_argument('-s', '--server', type=str, help="Scan a remote web server")
    parser.add_argument('-c','--client', type=str, help="Scan the local host")
    parser.add_argument('-l', '--logging', default=logging.INFO, type=int, help="Set logging level")
    parser.add_argument('-a', '--api', type=str, help="Scan an API server: URL | URL:PORT | IP | IP:PORT")
    parser.add_argument('-t', '--type', default='cipher', type=str, help="Type of API scan: cipher | full")
    parser.add_argument('-p', '--port', default=443, type=int, help="Remote port on the server to scan, By default, set to 443.")
    parser.add_argument('-P', '--protocol', type=str, help="Remote protocol on the server to scan, By default, set to https.")
    parser.add_argument('-r', '--repo', type=str, help="Repository to scan for presence of imported cryptographic modules.")
    return parser

def main():
    # Define arguments
    parser = createParser() # Creates a new parser for the arguments
    # Parse the argument
    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
    #apiScanInitiate(args)

    #logging.basicConfig(level=logging.ERROR)
    logger = logging.getLogger()
    logger.setLevel(args.logging)
    port = args.port
    # Call check for host
    if args.client:
        remote_host = args.client
        logging.info('Launching client scan')
        logging.info("Scanning against remote host: " + remote_host)

        # Get the supported cipher suite for the client system
        cipher_suite_support = client_cipher_suite.checkPQSafety((remote_host,port))

        """ Returns two separate cipher suite lists
            1. Cipher suite supported on the client OS
            2. Cipher suite shared by the client on initiating connection with the server from within the code
        """
        host_tls_check_result = tls_checker(cipher_suite_support['host'])
        shared_tls_check_result = tls_checker(cipher_suite_support['shared'])

        # Check if PQ safe algorithms are supported by the client on a system level
        if not host_tls_check_result['is_safe']:
            print({'status' : "Fail", "reason" : "Host system does not support PQ safe algorithms.", "recommendation":host_tls_check_result['result']})
        # Check if PQ safe algorithms are chosen to be shared in the context of the program
        elif not shared_tls_check_result['is_safe']:
            print({'status' : "Fail", "reason" : "PQ safe algorithm not chosen for connection.",'recommendation':shared_tls_check_result['result']})
        else:
            # Return the recommendations against each algorithm discovered during the check
            print({'status' : "Pass", "recommendation" : shared_tls_check_result['result']})
        return
    if args.server:
        server_address = args.server
        logging.info("Launching Server Scan")
        logging.info("Scanning remote server: " + server_address)
        # Get the supported cipher suite for the client system
        cipher_suite_support = server_cipher_suite.checkPQSafety(server_address)

        """ Returns a single cipher suite list of algorithm accepted by the server
        """
        server_tls_check_result = tls_checker(cipher_suite_support)

        # Check if PQ safe algorithms are supported by the client on a system level
        if not server_tls_check_result['is_safe']:
            print({'status' : "Fail", "reason" : server_tls_check_result['result']})
        else:
            # Return the recommendations against each algorithm discovered during the check
            print({'status' : "Pass", "recommendation" : server_tls_check_result['result']})
        return
    if args.api:
        api_endpoint = args.api
        logging.info("Launching API Scan")
        logging.info("Scanning API host: " + api_endpoint)

        port = args.port
        protocol = args.protocol
        # Initiate API scan and return here
        s='a'
        # Check if user wants to perform full scan
    
        file_name = api_cipher_suite.apiScanInitiate(api_endpoint, port, protocol, args.type)

        if file_name == 'Failed':
            print("Failed to initiate scan.")
            return

        if args.type == 'full':
            file = open(file_name,'r')
            scan_result = file.read()
            print(scan_result)
            return
        
        cipher_suite_support = api_cipher_suite.checkPQSafety(file_name)

        api_tls_check_result = tls_checker(cipher_suite_support)

        # Check if PQ safe algorithms are supported by the client on a system level
        if not api_tls_check_result['is_safe']:
            print({'status' : "Fail", "reason" : api_tls_check_result['result']})
        else:
            # Return the recommendations against each algorithm discovered during the check
            print({'status' : "Pass", "recommendation" : api_tls_check_result['result']})
        return

    if args.repo:
        remote_repo = args.repo
        scan_results,pie_chart_data,stats = repo_cipher_scan.scan_repo(remote_repo)
        print(scan_results)
        if stats['Safe'] > 0:
            print({'status' : "Pass", "recommendation" : scan_results})
        else:
            print({'status' : "Fail", "reason" : scan_results})
    pass

if __name__=='__main__':
    main()
