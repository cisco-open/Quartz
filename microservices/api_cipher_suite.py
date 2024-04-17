# MIT License

# Copyright (c) 2024 Cisco Systems, Inc. and its affiliates

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


# Inbuilt modules
import json
import os
import argparse

# Flask imports
import mysql.connector as connector
from mysql.connector import Error

# connecting databases
with open('/etc/pqc.config.json','r') as config_file:
    config = json.load(config_file)


token = config.get("ACCESS_TOKEN")
db_host = config.get("DB_HOST")
repo_db = config.get("DB_DATABASE")
db_user = config.get("DB_USER")
pass_word = config.get("DB_PASSWORD")
server_ip = config.get("HOST_IP")

mydb = connector.connect(
    host=db_host,
    database=repo_db,
    user=db_user,
    password=pass_word
)

def update_scan_query_generator():
    parameterized_query = "update api_scan set status=%s where scan_id=%s"
    return parameterized_query

def sql_update(query,params):
    if mydb.is_connected():
        # creating database cursor
        cursor = mydb.cursor()
        print("created cursor")
        cursor.execute(query,params)
        print("Executed query")
        mydb.commit()
        #Closing the cursor
        cursor.close()

# Run MySQL query
def sql_statement(query,params):
    if mydb.is_connected():
        # creating database cursor
        cur = mydb.cursor()
        cur.execute(query,params)
        # record = cur.fetchall()
        #Closing the cursor
        cur.close()
    # return record

def getScanAnalysis(api_host, port, protocol, file_name):
    json_out = file_name
    protocol_option = ''
    port_option = ''
    if protocol != "":
        protocol_option = " -t " + protocol
    if port != "":
        port_option = ":" + port 
    cmd = "/tmp/testssl.sh/testssl.sh -P -oJ " + json_out + protocol_option + " " + api_host + port_option + " 1>/dev/null"
    os.system(cmd)
    return
    """ scan_out_file = open(json_out, 'r')
    scan_output = json.loads(scan_out_file.read())
    scan_out_file.close()
    #print(output['ciphers'][0]['cipher_suites'])
    cipher_suite = []
    vulns = {}
    for entry in scan_output['scanResult']:
        for server_preference in entry['serverPreferences']:
            if server_preference['id'].startswith('supportedciphers'):
                for algo in server_preference['finding'].split():
                    cipher_suite.append(algo)
        for vuln in entry['vulnerabilities']:
            print(vuln)
            vulns[vuln['id']] = {"finding":vuln['finding']}
    return {"cipher_suite":cipher_suite, "vulnerabilities":vulns} """

def apiScanInitiate(scan_id, host, port, protocol, file_name):
    # Read input
    # scan_id = args.scan_id
    # host = args.host
    # port = args.port
    # protocol = args.protocol
    # file_name = args.file_name
    scan_id = str(scan_id)
    # set scan status to Running
    parameterized_query = update_scan_query_generator()
    try:
        sid = sql_update(parameterized_query,("Runnning", scan_id))
    except:
        parameterized_query = update_scan_query_generator()
        try:
            print('3')
            sid = sql_update(parameterized_query,("Failed",scan_id))
        except:
            #app.logger.error("Failed to update scan record after failure to initialize.")
            return
        return
    # Call script to run scan
    try:
        getScanAnalysis(host, port, protocol, file_name)
    except:
        parameterized_query = update_scan_query_generator()
        try:
            print('1')
            sid = sql_update(parameterized_query,("Failed",scan_id))
        except:
            #app.logger.error("Failed to update scan record after failure to initialize.")
            return
    
    parameterized_query = update_scan_query_generator()
    # Update scan status as Complete, update file name
    try:
        sid = sql_update(parameterized_query,("Complete",scan_id))
    except:
        #Update scan status in database as "Failed"
        parameterized_query = update_scan_query_generator()
        try:
            print('2')
            sid = sql_update(parameterized_query,("Failed",scan_id))
        except:
            #app.logger.error("Failed to update scan record after failure to initialize.")
            return
    return

def createParser():
    # Create the parser
    parser = argparse.ArgumentParser()
    # Add arguments
    parser.add_argument('--scan_id', type=str, required=True)
    parser.add_argument('--host', type=str, required=True)
    parser.add_argument('--file-name', type=str, required=True)
    parser.add_argument('--port', type=str)
    parser.add_argument('--protocol', type=str)
    return parser

#if __name__=='__main':
    #parser = createParser()
    # Parse the argument
    #args = parser.parse_args()
    #apiScanInitiate(args)


