# MIT License

# Copyright (c) 2024 Cisco Systems, Inc. and its affiliates

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from flask import Flask,request,jsonify
from flask_cors import CORS

import sys
import os
import argparse
import subprocess
import logging
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# get currewnt logged in USER Home
loggedin_user  = os.path.expanduser('~')

executable_name = 'terrascan'

def check_executable(executable_name):

    """
    Takes an executable name as input and checks if it is installed on the system.

    Input: 
        - executable_name : string
    Output: Returns a boolean value
    """
    
    try:
        subprocess.check_output(['which', executable_name])
        return True
    except subprocess.CalledProcessError:
        return False

def get_terrascan():

    """
    Downloads and installs the Terrascan executable.

    Input: N/A
    Output: Returns True if the executable is succesfully installed, False otherwise
    """

    os.system('curl -L "$(curl -s https://api.github.com/repos/tenable/terrascan/releases/latest | grep -o -E "https://.+?_Darwin_x86_64.tar.gz")" > terrascan.tar.gz')
    os.system('tar -xf terrascan.tar.gz terrascan && rm terrascan.tar.gz')
    os.system('install terrascan /usr/local/bin && rm terrascan')
    return check_executable('terrascan')

def build_docker_image():

    """
    Builds docker image from the input Dockerfile contents.

    Input: N/A
    Output: N/A
    """

    try:
        os.system("docker build -t test-scanner:latest .")
    except:
        return "Failed to build image"
    return

def get_pasive_scan_results(config_file):

    """
    Takes a Dockerfile as input and returns details of scanned configurations.

    Input: 
        - config_file : string
    Output: Returns a dictionary with following keys:
    - policies_validated : no of policies scanned
    - violated_policies : no of scanned policies that were violated
    - pie_chart_data : list of dictionaries with high, medium, and low data to be used for generating pie plot
    - high : high risk violations
    - medium : medium risk violations
    - low : low risk violations
    """

    if check_executable(executable_name):
        print(f"{executable_name} is installed.")
    else:
        print(f"{executable_name} is not installed.")
        logging.info(f"Terrascan is not installed. Calling installer.")
        if get_terrascan():
            print('Succesfully installed Terrascan..!')
            logging.info(f"Terrascan is successfully installed.")
        else:
            logging.error("Failed to install Terrascan..!")

    violations = []
    scan_cmd = f"terrascan scan -i docker -f {config_file} -o json > temp.json"
    os.system(scan_cmd)
    with open('temp.json', 'r') as scan_result_file:
        scan_result = json.loads(scan_result_file.read())
    scan_summary = scan_result['results']['scan_summary']
    policies_validated = scan_summary['policies_validated']
    violated_policies = scan_summary['violated_policies']
    low = scan_summary['low']
    medium = scan_summary['medium']
    high = scan_summary['high']
    if violated_policies != 0:
        violations = scan_result['results']['violations']
    os.system('rm temp.json')
    pie_chart_data = [{ "title": 'Low', "value": low, "color": '#90EE90' }, { "title": 'Medium', "value": medium, "color": '#e3df50'}, { "title": 'High', "value": high, "color": '#F75D59' }]
    return {"policies_validated" : policies_validated, "violated_policies" : violated_policies, "pie_chart_data" : pie_chart_data, "high" : high, "medium" : medium, "low" : low, "violations" : violations}

def scan_image():

    """
    Scans a docker image and returns the SBOM details and associated CVE details.

    Input: N/A
    Output: Returns a dictionary with three keys:
    - sbom : SBOM list
    - os_details : Docker image OS details
    - vulns : CVE details associated with the image
    """

    os.system("docker sbom test-scanner --format syft-json -o sbom.json")
    with open('sbom.json', 'r') as scan_result_file:
        sbom_result = scan_result_file.read()
    sbom_json = json.loads(sbom_result)
    sbom_list = []
    for artifact in sbom_json['artifacts']:
        sbom_list.append({"name" : artifact['name'], "version" : artifact["version"], "type" : artifact["type"]})
    distro = sbom_json["distro"]
    os_details = {"name" : distro["name"], "version" : distro["version"], "pretty_name" : distro["prettyName"]}
    os.system("grype test-scanner -o json > grype.json")
    with open('grype.json', 'r') as scan_result_file:
        grype_result = json.loads(scan_result_file.read())
    vuln_list = []
    for match in grype_result["matches"]:
        vuln_list.append({"cve_id" : match["relatedVulnerabilities"][0]["id"], "url" : match["relatedVulnerabilities"][0]["dataSource"], "description" : match["relatedVulnerabilities"][0]["description"]})
    return {"sbom" : sbom_list, "os_details" : os_details, "vulns" : vuln_list}

@app.route("/scan", methods = ['POST'])
def scan_config_file():
    scan_params = request.json
    config_file = scan_params['scan_target_statement']
    with open('Dockerfile', 'w') as dockerfile:
        dockerfile.write(config_file)
    passive_scan_result = get_pasive_scan_results('Dockerfile')
    build_docker_image()
    image_scan_result = scan_image()
    os.system('rm Dockerfile')
    return passive_scan_result | image_scan_result

# Command line argument parser
def createParser():
    # Create the parser
    parser = argparse.ArgumentParser()
    # Add arguments
    parser.add_argument('--file', type=str, required=True, help="Path of Terraform file")
    return parser

# if __name__=="__main__":
#     parser = createParser()

#     # Parse the argument
#     args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
#     config_file = args.file
#     # Store check results in a local variable
#     result = ""
    
#     # Check if Terrascan is not installed
#     executable_name = 'terrascan'
#     if check_executable(executable_name):
#         print(f"{executable_name} is installed.")
#     else:
#         print(f"{executable_name} is not installed.")
#         logging.info(f"Terrascan is not installed. Calling installer.")
#         if get_terrascan():
#             print('Succesfully installed Terrascan..!')
#             logging.info(f"Terrascan is successfully installed.")
#         else:
#             logging.error("Failed to install Terrascan..!")

#     result = scan_config_file(config_file)
#     print(result)

if __name__ == '__main__':
    app.run(host= '0.0.0.0', port=6000, debug=True)