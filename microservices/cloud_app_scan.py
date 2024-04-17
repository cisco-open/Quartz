# MIT License

# Copyright (c) 2024 Cisco Systems, Inc. and its affiliates

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import sys
import os
import argparse
import subprocess
import logging
import json
import pexpect

# get currewnt logged in USER Home
loggedin_user  = os.path.expanduser('~')

executable_name = 'prowler'

def check_executable(executable_name):

    """
    Takes an executable name and checks if it is already present on the system.

    Input: 
        - executable_name : string
    Output: Returns boolean value; True if the executable is installed, False otherwise
    """

    try:
        subprocess.check_output(['which', executable_name])
        return True
    except subprocess.CalledProcessError:
        return False

def get_prowler():

    """
    Installs the Prowler on the system.

    Input: N/A
    Output: Returns a boolean value depending on whether the installation was completed successully or not
    """

    os.system('pip install prowler')
    return check_executable('prowler')

def set_aws_credentials(access_key_id, secret_access_key):

    """
    Takes an AWS account access_key_id and secret_access_key as input and configures the local AWS credentials to use them as default.

    Input: 
        - access_key_id : string
        - secret_access_key : string
    Output: N/A
    """

    child = pexpect.spawn("aws configure")
    child.expect("AWS Access Key ID \[.*\]:")
    child.sendline(access_key_id)
    child.expect("AWS Secret Access Key \[.*\]:")
    child.sendline(secret_access_key)
    child.expect("Default region name \[None\]:")
    child.sendline('')
    child.expect("Default output format \[None\]:")
    child.sendline('')
    child.wait()
    print("AWS configure command completed.")
    

def find_json_file(directory):

    """
    Takes a SQL statement as input and finds all references to encryption and hashing method calls within it.

    Input: 
        - directory : string
    Output: Returns name of the output file created by the inventory scan, null if no file is created
    """

    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            return filename
    return None

def get_resources():

    """
    Identifies deployed resources on an AWS account.

    Input: N/A
    Output: Returns a list of dictionaries with the following keys:
    - service : AWS service name, e.g. S3
    - resource_type : AWS resource type
    - resource_id : AWS resource ID
    - resource_arn : AWS resource ARN
    """

    identified_resources = []
    os.system('prowler aws -i')
    output_file_name = find_json_file("/backend/output")
    with open(f'/backend/output/{output_file_name}', 'r') as resources_file:
        resources_file_content = resources_file.read()
    inventory_list = json.loads(resources_file_content)
    for resource in inventory_list:
        temp = {}
        temp['service'] = resource['AWS_Service']
        temp['resource_type'] = resource['AWS_ResourceType']
        temp['resource_id'] = resource['AWS_ResourceID']
        temp['resource_arn'] = resource['AWS_ResourceARN']
        identified_resources.append(temp)
    os.system(f'rm /backend/output/{output_file_name}')
    os.system('rm /backend/output/*.csv')
    return identified_resources

def get_scan_analysis():

    """
    Scans deployed resources on the cloud and returns scan results.

    Input: N/A
    Output: Returns a list of dictionaries with following keys:
    - check_title : scan name
    - service_name : AWS service name
    - status : Pass/Fail
    - region : region in which resource is deployed
    - resource_id : AWS resource ID
    - resource_arn : AWS resource ARN
    """

    scan_results = []
    os.system('prowler aws -f us-east-1 -M json -F temp')
    with open('/backend/output/temp.json', 'r') as scan_results_file:
        scan_results_content_json = scan_results_file.read()
    scan_results_content = json.loads(scan_results_content_json)
    for entry in scan_results_content:
        temp = {}
        if "Data Protection" in entry['CheckType']:
            temp['check_title'] = entry['CheckTitle']
            temp['service_name'] = entry['ServiceName']
            temp['status'] = entry['Status']
            temp['region'] = entry['Region']
            temp['resource_id'] = entry['ResourceId']
            temp['resource_arn'] = entry['ResourceArn']
            scan_results.append(temp)
    os.system('rm /backend/output/temp.json')
    return scan_results
    
def scan_cloud_app(access_key_id, secret_access_key, cloud_type):

    """
    Takes access_key_ID and secret_access_key as input and scans a cloud account to identify deployed resources and configurations.

    Input: 
        - access_key_id : string
        - secret_access_key : string
        - cloud_type : string
    Output: Returns a dictionary with two keys:
    - scan_result : Returned value from get_scan_analysis
    - graph : Generated node and edge details from identified resources
    """

    # Check if Prowler is not installed
    if check_executable(executable_name):
        print(f"{executable_name} is installed.")
    else:
        print(f"{executable_name} is not installed.")
        logging.info(f"Prowler is not installed. Calling installer.")
        if get_prowler():
            print('Succesfully installed Prowler..!')
            logging.info(f"Prowler is successfully installed.")
        else:
            logging.error("Failed to install Prowler..!")

    set_aws_credentials(access_key_id, secret_access_key)
    identified_resources = get_resources()
    scan_results = get_scan_analysis()
    nodes = []
    edges = []
    nodes.append({"id": access_key_id, "size":2400})
    resource_types = [x["service"] for x in identified_resources]
    unique_resource_types = set(resource_types)
    for resource_type in unique_resource_types:
        nodes.append({"id" : resource_type, "size" : 1600})
        edges.append({"source":access_key_id, "target":resource_type})
    for resource in identified_resources:
        nodes.append({"id" : resource["resource_id"], "size" : 800})
        edges.append({"source":resource["service"], "target":resource["resource_id"]})
    return {"scan_result": scan_results, "graph": {"nodes":nodes, "edges":edges}}

# Command line argument parser
def createParser():
    # Create the parser
    parser = argparse.ArgumentParser()
    # Add arguments
    parser.add_argument('--access-key-id', type=str, required=True, help="Access Key ID")
    parser.add_argument('--secret-access-key', type=str, required=True, help="Secret Access Key")
    parser.add_argument('--cloud-type', type=str, required=True, help="Cloud Provider Type")
    return parser

if __name__=="__main__":
    parser = createParser()

    # Parse the argument
    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
    access_key_id = args.access_key_id
    secret_access_key = args.secret_access_key
    cloud_type = args.cloud_type

    #terraform_file = args.file
    # Store check results in a local variable
    result = ""
    
    # Check if Terrascan is not installed
    if check_executable(executable_name):
        print(f"{executable_name} is installed.")
    else:
        print(f"{executable_name} is not installed.")
        logging.info(f"Prowler is not installed. Calling installer.")
        if get_prowler():
            print('Succesfully installed Prowler..!')
            logging.info(f"Prowler is successfully installed.")
        else:
            logging.error("Failed to install Prowler..!")
    
    scan_results = scan_cloud_app(access_key_id, secret_access_key, cloud_type)
    print(scan_results)

    #identified_resources = get_resources()
    #scan_results = get_scan_analysis()
    #print(scan_results)
