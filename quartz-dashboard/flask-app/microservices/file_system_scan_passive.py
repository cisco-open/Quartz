# MIT License

# Copyright (c) 2024 Cisco Systems, Inc. and its affiliates

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import docker
import re
import json
import argparse

available_dockers = ['ubuntu','red hat','kali']

def get_algos(scan_os):

    """
    Takes an OS name as input and finds all cipher suite details natively supported on it.

    Input: 
        - scan_os : string
    Output: Returns two details:
        - String of scan result source details
        - Dictionary of cipher algorithm details
    """

    parsed_algorithm_info = {}
    if scan_os in available_dockers:
        if scan_os == "ubuntu":
            with open('/backend/microservices/file_system_info/ubuntu.json') as ubuntu:
                crypto_content = json.loads(ubuntu.read())
            parsed_algorithm_info = crypto_content
        elif scan_os == "red hat":
            with open('/backend/microservices/file_system_info/red_hat.json') as redhat:
                crypto_content = json.loads(redhat.read())
            parsed_algorithm_info = crypto_content
        elif scan_os == "kali":
            with open('/backend/microservices/file_system_info/kali.json') as kali:
                crypto_content = json.loads(kali.read())
            parsed_algorithm_info = crypto_content
        return "/proc/crypto on latest docker image", parsed_algorithm_info
    else:
        if scan_os == "windows":
            # Read from existing information about cryptographic algorithms supported on Windows
            with open('/backend/microservices/file_system_info/windows_info.txt', 'r') as windows_info_file:
                for line in windows_info_file.readlines():
                    # readlines preserves next line character, so while tokenizing each line we need to remove the line terminator
                    extracted_info = line[:-1].split(',')
                    parsed_algorithm_info[extracted_info[0]] = [extracted_info[1], extracted_info[2]]
            return "https://learn.microsoft.com/en-us/windows/security/threat-protection/fips-140-validation?source=recommendations", parsed_algorithm_info
        # Display details for supported cryptographic algorithms on the target OS version
        # print(f"Supported cryptographic algorithms on {scan_os}:")
        # for algorithm in algorithm_details.keys():
        #     if scan_os.lower() in algorithm_details[algorithm].lower():
        #         print(f"{algorithm}: {algorithm_details[algorithm]}")
        return "'cryptography' library", parsed_algorithm_info
    
def createParser():
    # Create the parser
    parser = argparse.ArgumentParser()
    # Add arguments
    parser.add_argument('--os', type=str, required=True)
    return parser

if __name__=='__main__':
    parser = createParser()
    # Parse the argument
    args = parser.parse_args()
    scan_target = args.os
    scan_results = get_algos(scan_target)

    print(scan_results)