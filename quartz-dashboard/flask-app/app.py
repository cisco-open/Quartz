# MIT License

# Copyright (c) 2024 Cisco Systems, Inc. and its affiliates

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from flask import Flask,request,jsonify
#from flask_mysqldb import MySQL
import mysql.connector as connector
from mysql.connector import Error
from flask_cors import CORS

import subprocess
from threading import Thread
from datetime import datetime
from urllib.parse import urlparse
from io import BytesIO
import json
import os
import socket
import traceback
import requests
from time import sleep
import xmltodict

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
ALLOWED_EXTENSIONS = {'txt', 'sql'}

with open('/backend/pqc.config.json','r') as config_file:
    config = json.load(config_file)


token = config.get("ACCESS_TOKEN")
db_host = config.get("DB_HOST")
repo_db = config.get("DB_DATABASE")
db_user = config.get("DB_USER")
pass_word = config.get("DB_PASSWORD")
server_ip = config.get("HOST_IP")
valid_protocols = config.get("VALID_PROTOCOLS")

app.config['MYSQL_HOST'] = db_host
app.config['MYSQL_DATABASE'] = repo_db
app.config['MYSQL_USER'] = db_user
app.config['MYSQL_PASSWORD'] = pass_word
app.config['MONGODB_SETTINGS'] = {
    'db': 'post_quantum_crypto',
    'alias':'default'
}

# Create MySQL connector
mydb = connector.connect(
    host=app.config['MYSQL_HOST'],
    database=app.config['MYSQL_DATABASE'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD']
)

# Change to include cipher name validation
def algo_name_validation(cipher_suite):
    pass

# Change to include normal server url validation, either as IP or domain
def url_validation(server_host):
    return server_host['server']

def port_validation(server_port):
    try:
        if int(server_port) >= 1 and int(server_port) <= 655535:
            return False
        else:
            return True
    except:
        app.logger.error("Invalid port number provided as input!")
        return True

def protocol_validation(server_protocol):
    global valid_protocols
    try:
        if server_protocol in valid_protocols:
            return False
        else:
            return True
    except:
        app.logger.error("Invalid protocol provided as input!")
        return True

def fetch_scan_query_generator():
    parameterized_query = "select * from api_scan where scan_id = %s"
    return parameterized_query

def create_algo_query_generator():
    parameterized_query = "insert into tls_crypto_algo(algo_name,pqc_safe,risk_factor,comments,key_exchange,encryption,hash) values(%s,%s,%s,%s,%s,%s,%s)"
    return parameterized_query

def update_algo_query_generator():
    parameterized_query = "update tls_crypto_algo set pqc_safe=%s, risk_factor=%s, comments=%s, key_exchange=%s, encryption=%s, hash=%s where algo_name=%s"
    return parameterized_query

def fetch_algo_query_generator():
    parameterized_query = "select * from tls_crypto_algo where algo_name=%s"
    return parameterized_query

def fetch_all_algo_query_generator():
    parameterized_query = "select * from tls_crypto_algo"
    return parameterized_query

def delete_algo_query_generator():
    parameterized_query = "delete from tls_crypto_algo where algo_name=%s"
    return parameterized_query

def create_scan_query_generator():
    parameterized_query = "insert into api_scan(host,port,protocol,status,file_name) values(%s,%s,%s,%s,%s)"
    return parameterized_query

def update_scan_query_generator():
    parameterized_query = "update api_scan set scan_status=%s where scan_id=%s"
    return parameterized_query

def tls_query_generator(cipher_suite):
    params = len(cipher_suite)
    parameter_strings = "%s," * params
    paramterized_query = "select * from tls_crypto_algo where algo_name in (" + parameter_strings[:-1] + ")"
    return paramterized_query

def cipher_query_generator(cipher_suite):
    params = len(cipher_suite)
    parameter_strings = "%s," * params
    paramterized_query = "select * from source_crypto_algo where algo_name in (" + parameter_strings[:-1] + ")"
    return paramterized_query

def sql_select(query,params):
    if mydb.is_connected():
        # creating database cursor
        cursor = mydb.cursor()
        cursor.execute(query,params)
        record = cursor.fetchall()
        #Closing the cursor
        cursor.close()
    return record

def sql_insert(query,params):
    if mydb.is_connected():
        # creating database cursor
        cursor = mydb.cursor()
        cursor.execute(query,params)
        mydb.commit()
        insert_id = cursor.lastrowid
        #Closing the cursor
        cursor.close()
    return insert_id

def sql_update(query,params):
    if mydb.is_connected():
        # creating database cursor
        cursor = mydb.cursor()
        cursor.execute(query,params)
        mydb.commit()
        insert_id = cursor.lastrowid
        #Closing the cursor
        cursor.close()
    return insert_id

def sql_delete(query,params):
    if mydb.is_connected():
        # creating database cursor
        cursor = mydb.cursor()
        cursor.execute(query,params)
        mydb.commit()
        delete_id = cursor.lastrowid
        #Closing the cursor
        cursor.close()
    return delete_id

def repo_url_validation(repo_name):
    url = ''
    if 'https://github.com/' in repo_name['gitrepo'] and len(repo_name['gitrepo'].split('/', 5)) >= 5:
            if '.git' in repo_name['gitrepo']:
                url = repo_name['gitrepo'].replace(".git", "")
                url = "/".join(url.split('/',5)[3:5])
                return url
            else:
                url = repo_name['gitrepo']
                url = "/".join(url.split('/',5)[3:5])
                return url
    else:
        return None

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/algoSpec", methods=['POST'])
def algo_spec():
    algo_name = request.json['algo_name']
    pqc_safe = request.json['pqc_safe']
    risk_factor = request.json['risk_factor']
    remediation = request.json['remediation']
    key_exchange = request.json['key_exchange']
    encryption = request.json['encryption']
    hashm = request.json['hash']
    response = {}
    risk_factors = {"AES128" : 0.5, "SHA" : 0.3}
    try:
        # verify and sanitize the input
        if risk_factor == "":
            risk_factor = 0
            if key_exchange == "" or key_exchange in ['RSA', 'ECDHE-RSA']:
                risk_factor = '1'
            elif encryption == "" or encryption in ['3DES', "RSA"]:
                risk_factor = "1"
            elif hashm == "" or hashm in ['MD5']:
                risk_factor = "1"
            else:
                if encryption in ['AES128']:
                    if int(risk_factor) < risk_factors[encryption]:
                        risk_factor = str(risk_factors[encryption])
                if hashm in ['SHA','SHA256']:
                    if int(risk_factor) < risk_factors[hashm]:
                        risk_factor = str(risk_factors[hashm])
        parameterized_query = create_algo_query_generator()
        sql_insert(parameterized_query,(algo_name,pqc_safe,risk_factor,remediation, key_exchange, encryption, hashm))
        response['message'] = "Inserted record successfully!"
    except connector.errors.IntegrityError:
        app.logger.error("Record exists, trying to update.")
        try:
            # verify and sanitize the input
            parameterized_query = update_algo_query_generator()
            updated_id = sql_update(parameterized_query,(pqc_safe, risk_factor, remediation, key_exchange, encryption, hashm, algo_name))
            response['message'] = "Updated record successfully!"
        except:
            # alert for failure
            app.logger.error("Failed to update record: " + ','.join([algo_name, pqc_safe, risk_factor, remediation, key_exchange, encryption, hashm]))
            response = "Failed to update record."
    except:
        # alert for failure
        app.logger.error("Failed to insert record: " + ','.join([algo_name,pqc_safe,risk_factor,remediation, key_exchange, encryption, hashm]))
        response = "Failed to insert record."
    return response

@app.route("/addAlgoSpec", methods=['POST'])
def add_algo_spec():
    algo_specs = request.json['spec']
    response = {}
    for algo_spec in algo_specs:
        try:
            # verify and sanitize the input
            parameterized_query = create_algo_query_generator()
            sql_insert(parameterized_query,tuple(algo_spec))
            response[algo_spec[0]] = "Inserted record successfully!"
        except connector.errors.IntegrityError:
            app.logger.error("Record exists, skipping.")
            response[algo_spec[0]] = "Record exists, skipping."
        except:
            # alert for failure
            app.logger.error("Failed to insert record: " + ','.join(algo_spec))
            response[algo_spec[0]] = "Failed to insert record."
    return response
    
@app.route("/updateAlgoSpec", methods=['POST'])
def update_algo_spec():
    algo_name = request.json['spec']['algo_name']
    pqc_safe = request.json['spec']['pqc_safe']
    risk_factor = request.json['spec']['risk_factor']
    comments = request.json['spec']['comments']
    response = {}
    try:
        # verify and sanitize the input
        parameterized_query = update_algo_query_generator()
        updated_id = sql_update(parameterized_query,(pqc_safe, risk_factor, comments, algo_name))
        response[algo_name] = "Updated record successfully!"
    except:
        # alert for failure
        app.logger.error("Failed to update record: " + ','.join([algo_name, pqc_safe, risk_factor, comments]))
        response[algo_name] = "Failed to update record."
    return response

@app.route("/deleteAlgoSpec", methods=['POST'])
def delete_algo_spec():
    algo_name = request.json['algo_name']
    response = {}
    try:
        # verify and sanitize the input
        parameterized_query = delete_algo_query_generator()
        updated_id = sql_delete(parameterized_query,(algo_name,))
        response['message'] = "Deleted record successfully!"
    except:
        # alert for failure
        app.logger.error("Failed to delete record: " + algo_name)
        response = "Failed to delete record."
    return response

@app.route("/listAlgoSpec", methods=['POST'])
def list_algo_spec():
    algo_name = request.json['spec']['algo_name']
    response = {}
    try:
        # verify and sanitize the input
        parameterized_query = fetch_algo_query_generator()
        record = sql_select(parameterized_query,(algo_name,))

        response[algo_name] = {"pqc_safe": record[0][1], "risk_factor": record[0][2], "comments":record[0][3]}
    except:
        # alert for failure
        app.logger.error("Failed to fetch record: " + algo_name)
        response[algo_name] = "Failed to fetch record."
    return response

@app.route("/listAllAlgoSpec", methods=['POST'])
def list_all_algo_spec():
    response = []
    try:
        # verify and sanitize the input
        parameterized_query = fetch_all_algo_query_generator()
        records = sql_select(parameterized_query,())
        for record in records:
            pqc_safety = "Yes" if record[1]==1 else "No"    
            response.append({"name":record[0], "pqc_safe": pqc_safety, "risk_factor": record[2], "comments":record[3], "key_exchange": record[4], "encryption":record[5], "hash":record[6]})
    except:
        # alert for failure
        app.logger.error("Failed to fetch records")
        response = "Failed to fetch records"
    return response

def check_tls_active(target):
    from microservices import client_cipher_suite
    domain = ''
    if target[0].find('/') != -1:
        domain = urlparse(target[0]).netloc
    else:
        domain = target[0]
    print(domain)
    try:
        cipher_suite = client_cipher_suite.checkPQSafety((domain,int(target[1])))
    except socket.gaierror:
        app.logger.error("Failed to resolve target")
        return False
    except ConnectionRefusedError:
        app.logger.error("Target not accepting SSL connections!")
        return False
    except TimeoutError:
        app.logger.error("Timed out trying to connect to the the target!")
        return False
    except:
        traceback.print_exc()
        app.logger.error("Failed to fetch host's cipher suite details")
        return False
    return True

def check_pqc_safety(cipher_list):
    pqc_safe = False
    generated_query = tls_query_generator(cipher_list)
    results = sql_select(generated_query,tuple(cipher_list))
    output = []
    for result in results:
        if result[1]==True:
            pqc_safe = True
        output.append({"name":result[0], "pqc_safe":result[1], "risk_factor":result[2], "remediation":result[3]})
    return {'is_safe': pqc_safe, "tls_algo_record": output}

def check_algo_pqc_safety(cipher_list):
    pqc_safe = False
    generated_query = cipher_query_generator(cipher_list)
    results = sql_select(generated_query,tuple(cipher_list))
    output = []
    for result in results:
        if result[1]==True:
            pqc_safe = True
        output.append({"name":result[0], "pqc_safe":result[1], "risk_factor":result[2], "remediation":result[3], "keysize" : result[4]} )
    return {'is_safe': pqc_safe, "source_algo_record": output}

# Check for allowed extensions
def allowed_file(filename):
    return '.' in filename and \
        filename.count('.') == 1 and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_scan_results(scan_target, cipher_suite):
    cipher_list = [x for x in cipher_suite.keys()]
    safety_check = check_pqc_safety(cipher_list)
    nodes = []
    edges = []
    nodes.append({"id":scan_target, "size":1500})
    for tls_protocol in set(cipher_suite.values()):
        nodes.append({"id":tls_protocol, "size": 800})
        edges.append({"source":scan_target, "target":tls_protocol})
    safe = 0
    unsafe = 0
    safe_risk_factor = 0
    unsafe_risk_factor = 0
    global_risk_factor = 0
    detectors = []
    for tls_record in safety_check['tls_algo_record']:
        if tls_record['pqc_safe'] == True and cipher_suite[tls_record['name']] not in ['SSLv3', 'TLSv1']:
            detectors.append({
                'name': tls_record['name'],
                'remediation': tls_record['remediation'],
                'risk_factor': tls_record['risk_factor'],
                'tls_version': cipher_suite[tls_record['name']],
                'quantum_safe': 'Yes'
            })
            safe += 1
            safe_risk_factor += tls_record['risk_factor']
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
            unsafe_risk_factor += tls_record['risk_factor']
            nodes.append({"id":tls_record['name'], "color":"red"})
            edges.append({"source":cipher_suite[tls_record['name']], "target":tls_record['name']})
    stats = [{'Safe': safe, 'Unsafe': unsafe}]
    pie_chart_data = [{ "title": 'safe', "value": safe, "color": '#90EE90' }, { "title": 'unsafe', "value": unsafe, "color": '#F75D59' }]
    scan_result = [detectors, pie_chart_data, stats]
    if safe != 0:
        global_risk_factor = round(unsafe_risk_factor/(unsafe+safe),2)
    elif safe == 0:
        global_risk_factor = 1
    return scan_result, nodes, edges, global_risk_factor

@app.route("/scanClient", methods = ['POST'])
def scan_client():
    scan_params = request.json
    
    # Extract values from request body
    # What is the scan target?
    scan_target = scan_params['target'].strip()
    if scan_target == "":
        return "Scan target not provided ..!"
    
    # Extract domain information from scan target URL
    domain = ''
    if scan_target.find('/') != -1:
        domain = urlparse(scan_target).netloc
    else:
        domain = scan_target
    
    # What is the scan target port? [Default value is 443]
    try:
        scan_target_port = scan_params['scan_target_port'] if scan_params['scan_target_port'] != '' else '443'
        # Check if port number is within valid range
        if int(scan_target_port) < 1 or int(scan_target_port) > 65535:
            return "Invalid port provided as input..!"
    except:
        scan_target_port = '443'

    # Pie Plot colors
    pie_green = '#90EE90'
    pie_red = '#F75D59'

    response = {}
    from microservices import client_cipher_suite
    try:
        cipher_suite = client_cipher_suite.checkPQSafety((domain,int(scan_target_port)))
    except socket.gaierror:
        app.logger.error("Failed to resolve target")
        return "Failed to resolve target!"
    except ConnectionRefusedError:
        app.logger.error("Failed to establish connection")
        return "Target not accepting SSL connections!"
    except TimeoutError:
        app.logger.error("Failed to establish connection")
        return "Timed out trying to connect to the the target!"
    except:
        traceback.print_exc()
        app.logger.error("Failed to fetch host's cipher suite details")
        return "Failed to fetch host's cipher suite details..!"
    shared_cipher_suite = cipher_suite['shared']
    if shared_cipher_suite == None:
        return "Failed to connect with the target over TLS..!"
    scan_result, nodes, edges, global_risk_factor = get_scan_results(scan_target, shared_cipher_suite)
    scan_status = "Target: " + scan_target + ':' + scan_target_port + "; PQC Secure: " + ("No" if scan_result[2][0]['Unsafe']>0 else "Yes")
    return {"scan_result":scan_result, "graph": {"nodes":nodes, "edges":edges}, "scan_details":[{"params":"Scan Details", "values" : scan_status}, {"params":"Quantum Risk Factor", "values":global_risk_factor}]}

@app.route("/scanServer", methods = ['POST'])
def scan_server():
    scan_params = request.json
    
    # Extract values from request body
    # What is the scan target?
    scan_target = scan_params['target'].strip()
    if scan_target == "":
        return "Scan target not provided ..!"
    
    # Extract domain information from scan target URL
    domain = ''
    if scan_target.find('/') != -1:
        domain = urlparse(scan_target).netloc
    else:
        domain = scan_target
    
    # What is the scan type?
    scan_type = scan_params['scan_type']
    if scan_type == "":
        return "Scan type not provided ..!"
    
    # What is the scan target port? [Default value is 443]
    try:
        scan_target_port = scan_params['scan_target_port'] if scan_params['scan_target_port'] != '' else '443'
        # Check if port number is within valid range
        if scan_type in ['server', 'host', 'api']:
            if int(scan_target_port) < 1 or int(scan_target_port) > 65535:
                return "Invalid port provided as input..!"
    except:
        scan_target_port = '443'

    # Optional Parameters
    # What is scan target protocol? [For api scans]
    try:
        scan_target_protocol = scan_params['scan_target_protocol']
        # Check if the target protocol value is valid
        if scan_target_protocol not in ['mysql', 'postgres',''] and scan_type == "api":
            return "Invalid protocol provided as input..!"
    except:
        scan_target_protocol = ""
    from microservices import server_cipher_suite
    if not check_tls_active((domain, scan_target_port)):
        return "Scan Failed : Couldn't establish TLS connection with target..!"
    try:
        cipher_suite = server_cipher_suite.getServerCipherSuites(domain)
    except ConnectionRefusedError:
        return "Failed to connect with the target over TLS..!"
    except:
        return "Failed to connect with the target over TLS..!"
    scan_result, nodes, edges, global_risk_factor = get_scan_results(scan_target, cipher_suite)
    scan_status = "Target: " + scan_target + "; Type: " + scan_type + "; PQC Secure: " + ("No" if scan_result[2][0]['Unsafe']>0 else "Yes")
    return {"scan_result":scan_result, "graph": {"nodes":nodes, "edges":edges}, "scan_details":[{"params":"Scan Details", "values" : scan_status}, {"params":"Quantum Risk Factor", "values":global_risk_factor}]}

@app.route("/scanApi", methods = ['POST'])
def scan_api():
    scan_params = request.json
    
    # Extract values from request body
    # What is the scan target?
    scan_target = scan_params['target'].strip()
    if scan_target == "":
        return "Scan target not provided ..!"
    
    # Extract domain information from scan target URL
    domain = ''
    if scan_target.find('/') != -1:
        domain = urlparse(scan_target).netloc
    else:
        domain = scan_target
    
    # What is the scan type?
    scan_type = scan_params['scan_type']
    if scan_type == "":
        return "Scan type not provided ..!"
    
    # What is the scan target port? [Default value is 443]
    try:
        scan_target_port = scan_params['scan_target_port'] if scan_params['scan_target_port'] != '' else '443'
        # Check if port number is within valid range
        if scan_type in ['server', 'host', 'api']:
            if int(scan_target_port) < 1 or int(scan_target_port) > 65535:
                return "Invalid port provided as input..!"
    except:
        scan_target_port = '443'

    # Optional Parameters
    # What is scan target protocol? [For api scans]
    try:
        scan_target_protocol = scan_params['scan_target_protocol']
        # Check if the target protocol value is valid
        if scan_target_protocol not in ['mysql', 'postgres',''] and scan_type == "api":
            return "Invalid protocol provided as input..!"
    except:
        scan_target_protocol = ""
    from microservices import api_cipher_suite
    api_cipher_suite.getScanner()
    file_now = datetime.now()
    domain = ''
    if scan_target.find('/') != -1:
        domain = urlparse(scan_target).netloc
    else:
        domain = scan_target
    json_out = domain + '_' + file_now.strftime("%Y%m%d-%H%M") + '.json'

    protocol_option = ''
    port_option = ''
    if scan_target_protocol != "":
        protocol_option = " -t " + scan_target_protocol
    if scan_target_port != "":
        port_option = ":" + scan_target_port 
    cmd = "/tmp/testssl.sh/testssl.sh -P --openssl-timeout 2 -oJ " + json_out + protocol_option + " " + domain + port_option
    try:
        os.system(cmd)
        #pass
    except:
        return "Failed to execute scan!"
    scan_out = open(json_out, 'r')
    scan_output = json.loads(scan_out.read())
    scan_out.close()
    os.system("rm " + json_out)
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
        app.logger.error("Failed to scan target API")
        return "Failed to scan target API"
    #if scan_target == 'ec2-35-80-145-71.us-west-2.compute.amazonaws.com':
    ##    cipher_suite['ECDHE-RSA-AES256-GCM-SHA384'] = 'TLSv12'
    #    cipher_suite['TLS_AES_256_GCM_SHA384'] = 'TLSv13'
    scan_result, nodes, edges, global_risk_factor = get_scan_results(scan_target, cipher_suite)
    scan_status = "Target: " + scan_target + (':' + scan_target_port + '; ' if scan_target_port != '' else '') + ("Protocol: " + scan_target_protocol if scan_target_protocol != '' else '') + "; Type: " + scan_type + "; PQC Secure: " + ("No" if scan_result[2][0]['Unsafe']>0 else "Yes")
    return {"scan_result":scan_result, "graph": {"nodes":nodes, "edges":edges}, "scan_details":[{"params":"Scan Details", "values" : scan_status}, {"params":"Quantum Risk Factor", "values":global_risk_factor}]}

@app.route("/scanRepo", methods = ['POST'])
def scan_repo():
    scan_params = request.json
    
    # Extract values from request body
    # What is the scan target?
    scan_target = scan_params['target'].strip()
    if scan_target == "":
        return "Scan target not provided ..!"
    
    # Extract domain information from scan target URL
    domain = ''
    if scan_target.find('/') != -1:
        domain = urlparse(scan_target).netloc
    else:
        domain = scan_target

    # Optional Parameters
    from microservices import repo_cipher_scan
    try:
        print("1")
        scan_results,pie_chart_data,stats,global_risk_factor = repo_cipher_scan.scan_repo(scan_target)
        print("1")
        scan_status = "Target: " + scan_target + "; Type: Repo; PQC Secure: " + ("No" if stats[0]['Unsafe']>0 else "Yes") + "; Global Quantum Risk Factor: " + str(global_risk_factor)
        
        return {"scan_result":[scan_results,pie_chart_data,stats], "scan_details":[{"params":"Scan Details", "values" : scan_status}, {"params":"Quantum Risk Factor", "values":global_risk_factor}]}
    except:
        return "Failed to scan target repository"

@app.route("/scanFS", methods = ['POST'])
def scan_fs():
    scan_params = request.json
    
    # Extract values from request body
    # What is the scan target?
    scan_target = scan_params['target'].strip()
    if scan_target == "":
        return "Scan target not provided ..!"
    
    # Extract domain information from scan target URL
    domain = ''
    if scan_target.find('/') != -1:
        domain = urlparse(scan_target).netloc
    else:
        domain = scan_target
    
    # What is the scan type?
    scan_type = scan_params['scan_type']
    if scan_type == "":
        return "Scan type not provided ..!"

    # Optional Parameters
    # What is the scan database type? [For database config scans]
    try:
        scan_target_type = scan_params["scan_target_type"]
    except:
        scan_target_type = ""
    from microservices import file_system_scan_passive
    scan_source, scan_details = file_system_scan_passive.get_algos(scan_target_type)
    scan_cipher_list = [x for x in scan_details.keys()]
    safety_check = check_algo_pqc_safety(scan_cipher_list)
    nodes = []
    edges = []
    nodes.append({"id":scan_target, "size":1500})
    safe = 0
    unsafe = 0
    safe_risk_factor = 0
    unsafe_risk_factor = 0
    global_risk_factor = 0
    detectors = []
    for cipher_record in safety_check['source_algo_record']:
        if cipher_record['pqc_safe'] == True and int(scan_details[cipher_record['name']][0]) >= int(cipher_record['keysize']): #and cipher_suite[tls_record['name']]=='TLSv13'
            detectors.append({
                'name': cipher_record['name'],
                'remediation': cipher_record['remediation'],
                'risk_factor': cipher_record['risk_factor'],
                'keysize': str(scan_details[cipher_record['name']][0]) + " - " + str(scan_details[cipher_record['name']][1]),
                'quantum_safe': 'Yes'
            })
            safe += 1
            safe_risk_factor += cipher_record['risk_factor']
            nodes.append({"id":cipher_record['name'],"color":"green", "size":600})
            edges.append({"source":scan_target, "target":cipher_record['name']})
        elif cipher_record['pqc_safe'] == True and int(scan_details[cipher_record['name']][1]) < int(cipher_record['keysize']): #and cipher_suite[tls_record['name']]=='TLSv13'
            detectors.append({
                'name': cipher_record['name'],
                'remediation': cipher_record['remediation'],
                'risk_factor': 0.5,
                'keysize': str(scan_details[cipher_record['name']][0]) + " - " + str(scan_details[cipher_record['name']][1]),
                'quantum_safe': 'No'
            })
            unsafe += 1
            unsafe_risk_factor += 0.5
            nodes.append({"id":cipher_record['name'],"color":"yellow", "size":600})
            edges.append({"source":scan_target, "target":cipher_record['name']})
        else:
            detectors.append({
                'name': cipher_record['name'],
                'remediation': cipher_record['remediation'],
                'risk_factor': 1.0,
                'keysize': str(scan_details[cipher_record['name']][0]) + " - " + str(scan_details[cipher_record['name']][1]),
                'quantum_safe': 'No'
            })
            unsafe += 1
            unsafe_risk_factor += cipher_record['risk_factor']
            nodes.append({"id":cipher_record['name'], "color":"red", "size":600})
            edges.append({"source":scan_target, "target":cipher_record['name']})
        nodes.append({"id":scan_details[cipher_record['name']][0],"color":"grey"})
        edges.append({"source":cipher_record['name'], "target":scan_details[cipher_record['name']][0]})
        nodes.append({"id":scan_details[cipher_record['name']][1],"color":"grey"})
        edges.append({"source":cipher_record['name'], "target":scan_details[cipher_record['name']][1]})
    stats = [{'Safe': safe, 'Unsafe': unsafe}]
    pie_chart_data = [{ "title": 'safe', "value": safe, "color": '#90EE90' }, { "title": 'unsafe', "value": unsafe, "color": '#F75D59' }]
        #print(pie_chart_data)
    if safe != 0:
        global_risk_factor = round(unsafe_risk_factor/(unsafe+safe),2)
    else:
        global_risk_factor = 1
    scan_status = "Type: File System Scan; PQC Secure: " + ("No" if stats[0]['Unsafe']>0 else "Yes")
    return {"scan_result":[detectors,pie_chart_data,stats], "graph": {"nodes":nodes, "edges":edges}, "scan_details":[{"params":"Scan Details", "values" : scan_status}, {"params":"Quantum Risk Factor", "values":global_risk_factor}, {"params":"Scan Source", "values": scan_source}]}

@app.route("/scanDatabase", methods = ['POST'])
def scan_database():
    scan_params = request.json
    
    # Extract values from request body
    # What is the scan target?
    scan_target = scan_params['target'].strip()
    if scan_target == "":
        return "Scan target not provided ..!"
    
    # Extract domain information from scan target URL
    domain = ''
    if scan_target.find('/') != -1:
        domain = urlparse(scan_target).netloc
    else:
        domain = scan_target
    
    # What is the scan type?
    scan_type = scan_params['scan_type']
    if scan_type == "":
        return "Scan type not provided ..!"
    
    # What is the scan target port? [Default value is 443]
    try:
        scan_target_port = scan_params['scan_target_port'] if scan_params['scan_target_port'] != '' else '443'
        # Check if port number is within valid range
        if scan_type in ['database']:
            if int(scan_target_port) < 1 or int(scan_target_port) > 65535:
                return "Invalid port provided as input..!"
    except:
        scan_target_port = '443'

    # Optional Parameters
    # What is the scan database type? [For database config scans]
    try:
        scan_target_type = scan_params["scan_target_type"]
    except:
        scan_target_type = ""
    if scan_type == "statement":
        # Format sql statement to a single line statement
        sql_statement = scan_params['scan_target_statement']

        from microservices import encrypt_search
        references = encrypt_search.find_references(sql_statement)

        return references
    else:
        from microservices import database_scan
        scan_results,pie_chart_data,stats,global_risk_factor = database_scan.scanner(scan_target_type, scan_target,scan_target_port)
        scan_status = "Target: " + scan_target + "; Type: " + scan_type + "; PQC Secure: " + ("No" if stats[0]['Unsafe']>0 else "Yes") + "; Global Quantum Risk Factor: " + str(global_risk_factor)
        return {"scan_result":[scan_results,pie_chart_data,stats], "scan_details":[{"params":"Scan Details", "values" : scan_status}, {"params":"Quantum Risk Factor", "values":global_risk_factor}]}

@app.route("/scanCloudStorage", methods = ['POST'])
def scan_cloud_storage():
    scan_params = request.json
    
    # Extract values from request body
    # What is the scan target?
    scan_target = scan_params['target'].strip()
    if scan_target == "":
        return "Scan target not provided ..!"
    
    # Extract domain information from scan target URL
    domain = ''
    if scan_target.find('/') != -1:
        domain = urlparse(scan_target).netloc
    else:
        domain = scan_target

    # Optional Parameters
    # What is clowd owner ID? [For cloud storage scan]
    try:
        scan_target_cloud_owner = scan_params['scan_target_cloud_owner']
    except:
        scan_target_cloud_owner = ""
    # What is the scan database type? [For database config scans]
    try:
        scan_target_type = scan_params["scan_target_type"]
    except:
        scan_target_type = ""
    if scan_target_type == "s3":
        key_info_response = requests.get(scan_target+"/?encryption", headers={"HOST" : scan_target, "x-amz-expected-bucket-owner" : scan_target_cloud_owner})
        key_info_xml = key_info_response.text
        try:
            key_info = xmltodict.parse(key_info_xml)
            if len(key_info['ServerSideEncryptionConfiguration']['Rule']) != 0:
                for rule in key_info['ServerSideEncryptionConfiguration']['Rule']:
                    if rule['ApplyServerSideEncryptionByDefault']['SSEAlgorithm'] == "AES256":
                        return {"cloud_target" : scan_target, "status" : "S3 Bucket encrypted using S3 default encryption", "algo" : "AES256", "pqc_secure" : "Yes"}
                    else:
                        key_master_id = rule['ApplyServerSideEncryptionByDefault']['KMSMasterKeyID']
                        return {"cloud_target" : scan_target, "status" : f"S3 Bucket encrypted using AWS KMS (master key ID : {key_master_id})", "algo" : "AES-GCM-256", "pqc_secure" : "Yes"}
            else:
                return  {"cloud_target" : scan_target, "status" : f"S3 Bucket not encrypted", "algo" : "None", "pqc_secure" : "No"}
        except:
            return  {"cloud_target" : scan_target, "status" : f"Failed to access encryption details for the S3 bucket.", "algo" : "None", "pqc_secure" : "No"}

@app.route("/scanCloudApplication", methods = ['POST'])
def scan_cloud_app():
    scan_params = request.json
    scan_target_type = scan_params['scan_target_type']
    access_key_id = scan_params['scan_target_cloud_access_key_id']
    secret_access_key = scan_params['scan_target_cloud_secret_access_key']
    from microservices import cloud_app_scan
    scan_results = cloud_app_scan.scan_cloud_app(access_key_id, secret_access_key, scan_target_type)
    return scan_results

@app.route("/scanTerraform", methods = ['POST'])
def scan_terraform():
    scan_params = request.json
    # Format sql statement to a single line statement
    terraform_statement = scan_params['scan_target_statement']

    with open('terraform.tf', 'w') as terraform_file:
        terraform_file.write(terraform_statement)

    from microservices import terraform_scan
    scan_results = terraform_scan.get_scan_results('terraform.tf')

    return scan_results

@app.route("/scanConfigFile", methods = ['POST'])
def scan_config_file():
    pass

@app.route("/scan", methods = ['POST'])
def start_scan():
    now = datetime.now()
    now = now.strftime("%m/%d/%Y %H:%M:%S")
    scan_params = request.json
    
    # Extract values from request body
    # What is the scan target?
    scan_target = scan_params['target'].strip()
    if scan_target == "":
        return "Scan target not provided ..!"
    
    # Extract domain information from scan target URL
    domain = ''
    if scan_target.find('/') != -1:
        domain = urlparse(scan_target).netloc
    else:
        domain = scan_target
    
    # What is the scan type?
    scan_type = scan_params['scan_type']
    if scan_type == "":
        return "Scan type not provided ..!"
    
    # What is the scan target port? [Default value is 443]
    try:
        scan_target_port = scan_params['scan_target_port'] if scan_params['scan_target_port'] != '' else '443'
        # Check if port number is within valid range
        if scan_type in ['server', 'host', 'api']:
            if int(scan_target_port) < 1 or int(scan_target_port) > 65535:
                return "Invalid port provided as input..!"
    except:
        scan_target_port = '443'

    # Optional Parameters
    # What is clowd owner ID? [For cloud storage scan]
    try:
        scan_target_cloud_owner = scan_params['scan_target_cloud_owner']
    except:
        scan_target_cloud_owner = ""
    # What is scan target protocol? [For api scans]
    try:
        scan_target_protocol = scan_params['scan_target_protocol']
        # Check if the target protocol value is valid
        if scan_target_protocol not in ['mysql', 'postgres',''] and scan_type == "api":
            return "Invalid protocol provided as input..!"
    except:
        scan_target_protocol = ""
    # What is the scan database type? [For database config scans]
    try:
        scan_target_type = scan_params["scan_target_type"]
    except:
        scan_target_type = ""

    # Pie Plot colors
    pie_green = '#90EE90'
    pie_red = '#F75D59'

    response = {}
    # Missing URL validation - to be added
    if scan_type == "host":
        from microservices import client_cipher_suite
        try:
            cipher_suite = client_cipher_suite.checkPQSafety((domain,int(scan_target_port)))
        except socket.gaierror:
            app.logger.error("Failed to resolve target")
            return "Failed to resolve target!"
        except ConnectionRefusedError:
            app.logger.error("Failed to establish connection")
            return "Target not accepting SSL connections!"
        except TimeoutError:
            app.logger.error("Failed to establish connection")
            return "Timed out trying to connect to the the target!"
        except:
            traceback.print_exc()
            app.logger.error("Failed to fetch host's cipher suite details")
            return "Failed to fetch host's cipher suite details..!"
        host_cipher_suite = cipher_suite['host']
        shared_cipher_suite = cipher_suite['shared']
        if shared_cipher_suite == None:
            return "Failed to connect with the target over TLS..!"
        shared_cipher_list = [x for x in shared_cipher_suite.keys()]
        try:
            safety_check = check_pqc_safety(shared_cipher_list)
        except:
            app.logger.error("Check DB connection/query")
            return "Failed to fetch host's cipher suite details..!"
        nodes = []
        edges = []
        nodes.append({"id":"Host", "size":1500})
        for tls_protocol in set(shared_cipher_suite.values()):
            nodes.append({"id":tls_protocol, "size": 800})
            edges.append({"source":"Host", "target":tls_protocol})
        safe = 0
        unsafe = 0
        safe_risk_factor = 0
        unsafe_risk_factor = 0
        global_risk_factor = 0
        detectors = []
        for tls_record in safety_check['tls_algo_record']:
            if tls_record['pqc_safe'] == True and shared_cipher_suite[tls_record['name']] not in ['SSLv3', 'TLSv1']:
                detectors.append({
                    'name': tls_record['name'],
                    'remediation': tls_record['remediation'],
                    'risk_factor': tls_record['risk_factor'],
                    'tls_version': shared_cipher_suite[tls_record['name']],
                    'quantum_safe': 'Yes'
                })
                safe += 1
                safe_risk_factor += tls_record['risk_factor']
                nodes.append({"id":tls_record['name'],"color":"green"})
                edges.append({"source":shared_cipher_suite[tls_record['name']], "target":tls_record['name']})
            else:
                detectors.append({
                    'name': tls_record['name'],
                    'remediation': tls_record['remediation'],
                    'risk_factor': tls_record['risk_factor'],
                    'tls_version': shared_cipher_suite[tls_record['name']],
                    'quantum_safe': 'No'
                })
                unsafe += 1
                unsafe_risk_factor += tls_record['risk_factor']
                nodes.append({"id":tls_record['name'], "color":"red"})
                edges.append({"source":shared_cipher_suite[tls_record['name']], "target":tls_record['name']})
        stats = [{'Safe': safe, 'Unsafe': unsafe}]
        pie_chart_data = [{ "title": 'safe', "value": safe, "color": pie_green }, { "title": 'unsafe', "value": unsafe, "color": pie_red }]
            #print(pie_chart_data)
        if safe != 0:
            global_risk_factor = round(unsafe_risk_factor/(unsafe+safe),2)
        elif safe == 0:
            global_risk_factor = 1
        scan_status = "Target: " + scan_target + ':' + scan_target_port + "; PQC Secure: " + ("No" if unsafe>0 else "Yes")
        return {"scan_result":[detectors,pie_chart_data,stats], "graph": {"nodes":nodes, "edges":edges}, "scan_details":[{"params":"Scan Details", "values" : scan_status}, {"params":"Quantum Risk Factor", "values":global_risk_factor}]}
    elif scan_type == "server":
        from microservices import server_cipher_suite
        if not check_tls_active((domain, scan_target_port)):
            return "Scan Failed : Couldn't establish TLS connection with target..!"
        try:
            cipher_suite = server_cipher_suite.getServerCipherSuites(domain)
        except ConnectionRefusedError:
            return "Failed to connect with the target over TLS..!"
        except:
            return "Failed to connect with the target over TLS..!"
        cipher_list = [x for x in cipher_suite.keys()]
        safety_check = check_pqc_safety(cipher_list)
        nodes = []
        edges = []
        nodes.append({"id":scan_target, "size":1500})
        for tls_protocol in set(cipher_suite.values()):
            nodes.append({"id":tls_protocol, "size": 800})
            edges.append({"source":scan_target, "target":tls_protocol})
        safe = 0
        unsafe = 0
        safe_risk_factor = 0
        unsafe_risk_factor = 0
        global_risk_factor = 0
        detectors = []
        for tls_record in safety_check['tls_algo_record']:
            if tls_record['pqc_safe'] == True:
                detectors.append({
                    'name': tls_record['name'],
                    'remediation': tls_record['remediation'],
                    'risk_factor': tls_record['risk_factor'],
                    'tls_version': cipher_suite[tls_record['name']],
                    'quantum_safe': 'Yes'
                })
                safe += 1
                safe_risk_factor += tls_record['risk_factor']
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
                unsafe_risk_factor += tls_record['risk_factor']
                nodes.append({"id":tls_record['name'], "color":"red"})
                edges.append({"source":cipher_suite[tls_record['name']], "target":tls_record['name']})
        colors = {'Safe': '#00FF00', 'Unsafe': '#FF0000'}
        stats = [{'Safe': safe, 'Unsafe': unsafe}]
        pie_chart_data = [{ "title": 'safe', "value": safe, "color": '#90EE90' }, { "title": 'unsafe', "value": unsafe, "color": '#F75D59' }]
            #print(pie_chart_data)
        if safe != 0 or unsafe != 0:
            global_risk_factor = round(unsafe_risk_factor/(unsafe+safe),2)
        scan_status = "Target: " + scan_target + "; Type: " + scan_type + "; PQC Secure: " + ("No" if unsafe>0 else "Yes")
        return {"scan_result":[detectors,pie_chart_data,stats], "graph": {"nodes":nodes, "edges":edges}, "scan_details":[{"params":"Scan Details", "values" : scan_status}, {"params":"Quantum Risk Factor", "values":global_risk_factor}]}
    elif scan_type == "api":
        #if port_validation(scan_target_port) or protocol_validation(scan_target_protocol):
        #    return {"message":"Invalid inputs"}
        #sleep(20)
        # create a scan record as Initiating
        # Change this to python script execution from shell instead of method call
        from microservices import api_cipher_suite
        api_cipher_suite.getScanner()
        file_now = datetime.now()
        domain = ''
        if scan_target.find('/') != -1:
            domain = urlparse(scan_target).netloc
        else:
            domain = scan_target
        json_out = domain + '_' + file_now.strftime("%Y%m%d-%H%M") + '.json'

        protocol_option = ''
        port_option = ''
        if scan_target_protocol != "":
            protocol_option = " -t " + scan_target_protocol
        if scan_target_port != "":
            port_option = ":" + scan_target_port 
        cmd = "/tmp/testssl.sh/testssl.sh -P --openssl-timeout 2 -oJ " + json_out + protocol_option + " " + domain + port_option
        try:
            os.system(cmd)
            #pass
        except:
            return "Failed to execute scan!"
        scan_out = open(json_out, 'r')
        scan_output = json.loads(scan_out.read())
        scan_out.close()
        os.system("rm " + json_out)
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
            app.logger.error("Failed to scan target API")
            return "Failed to scan target API"
        #if scan_target == 'ec2-35-80-145-71.us-west-2.compute.amazonaws.com':
        ##    cipher_suite['ECDHE-RSA-AES256-GCM-SHA384'] = 'TLSv12'
        #    cipher_suite['TLS_AES_256_GCM_SHA384'] = 'TLSv13'
        cipher_list = [x for x in cipher_suite.keys()]
        safety_check = check_pqc_safety(cipher_list)
        nodes = []
        edges = []
        nodes.append({"id":scan_target, "size":1500})
        for tls_protocol in set(cipher_suite.values()):
            nodes.append({"id":tls_protocol, "size": 800})
            edges.append({"source":scan_target, "target":tls_protocol})
        safe = 0
        unsafe = 0
        safe_risk_factor = 0
        unsafe_risk_factor = 0
        global_risk_factor = 0
        detectors = []
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
                safe_risk_factor += tls_record['risk_factor']
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
                unsafe_risk_factor += tls_record['risk_factor']
                nodes.append({"id":tls_record['name'], "color":"red"})
                edges.append({"source":cipher_suite[tls_record['name']], "target":tls_record['name']})
        colors = {'Safe': '#00FF00', 'Unsafe': '#FF0000'}
        stats = [{'Safe': safe, 'Unsafe': unsafe}]
        pie_chart_data = [{ "title": 'safe', "value": safe, "color": '#90EE90' }, { "title": 'unsafe', "value": unsafe, "color": '#F75D59' }]
            #print(pie_chart_data)
        if safe != 0 or unsafe != 0:
            global_risk_factor = round(unsafe_risk_factor/(unsafe+safe),2)
        scan_status = "Target: " + scan_target + (':' + scan_target_port + '; ' if scan_target_port != '' else '') + ("Protocol: " + scan_target_protocol if scan_target_protocol != '' else '') + "; Type: " + scan_type + "; PQC Secure: " + ("No" if unsafe>0 else "Yes")
        return {"scan_result":[detectors,pie_chart_data,stats], "graph": {"nodes":nodes, "edges":edges}, "scan_details":[{"params":"Scan Details", "values" : scan_status}, {"params":"Quantum Risk Factor", "values":global_risk_factor}]}
    elif scan_type == "repo":
        from microservices import repo_cipher_scan
        try:
            print("1")
            scan_results,pie_chart_data,stats,global_risk_factor = repo_cipher_scan.scan_repo(scan_target)
            print("1")
            scan_status = "Target: " + scan_target + "; Type: " + scan_type + "; PQC Secure: " + ("No" if stats[0]['Unsafe']>0 else "Yes") + "; Global Quantum Risk Factor: " + str(global_risk_factor)
            
            return {"scan_result":[scan_results,pie_chart_data,stats], "scan_details":[{"params":"Scan Details", "values" : scan_status}, {"params":"Quantum Risk Factor", "values":global_risk_factor}]}
        except:
            return "Failed to scan target repository"
    elif scan_type == "database":
        from microservices import database_scan
        scan_results,pie_chart_data,stats,global_risk_factor = database_scan.scanner(scan_target_type, scan_target,scan_target_port)
        scan_status = "Target: " + scan_target + "; Type: " + scan_type + "; PQC Secure: " + ("No" if stats[0]['Unsafe']>0 else "Yes") + "; Global Quantum Risk Factor: " + str(global_risk_factor)
        return {"scan_result":[scan_results,pie_chart_data,stats], "scan_details":[{"params":"Scan Details", "values" : scan_status}, {"params":"Quantum Risk Factor", "values":global_risk_factor}]}
    elif scan_type == "cloud":
        if scan_target_type == "s3":
            key_info_response = requests.get(scan_target+"/?encryption", headers={"HOST" : scan_target, "x-amz-expected-bucket-owner" : scan_target_cloud_owner})
            key_info_xml = key_info_response.text
            try:
                key_info = xmltodict.parse(key_info_xml)
                if len(key_info['ServerSideEncryptionConfiguration']['Rule']) != 0:
                    for rule in key_info['ServerSideEncryptionConfiguration']['Rule']:
                        if rule['ApplyServerSideEncryptionByDefault']['SSEAlgorithm'] == "AES256":
                            return {"cloud_target" : scan_target, "status" : "S3 Bucket encrypted using S3 default encryption", "algo" : "AES256", "pqc_secure" : "Yes"}
                        else:
                            key_master_id = rule['ApplyServerSideEncryptionByDefault']['KMSMasterKeyID']
                            return {"cloud_target" : scan_target, "status" : f"S3 Bucket encrypted using AWS KMS (master key ID : {key_master_id})", "algo" : "AES-GCM-256", "pqc_secure" : "Yes"}
                else:
                    return  {"cloud_target" : scan_target, "status" : f"S3 Bucket not encrypted", "algo" : "None", "pqc_secure" : "No"}
            except:
                return  {"cloud_target" : scan_target, "status" : f"Failed to access encryption details for the S3 bucket.", "algo" : "None", "pqc_secure" : "No"}
    elif scan_type == "fs":
        from microservices import file_system_scan_passive
        scan_source, scan_details = file_system_scan_passive.get_algos(scan_target_type)
        scan_cipher_list = [x for x in scan_details.keys()]
        safety_check = check_algo_pqc_safety(scan_cipher_list)
        nodes = []
        edges = []
        nodes.append({"id":scan_target, "size":1500})
        safe = 0
        unsafe = 0
        safe_risk_factor = 0
        unsafe_risk_factor = 0
        global_risk_factor = 0
        detectors = []
        for cipher_record in safety_check['source_algo_record']:
            if cipher_record['pqc_safe'] == True and int(scan_details[cipher_record['name']][0]) >= int(cipher_record['keysize']): #and cipher_suite[tls_record['name']]=='TLSv13'
                detectors.append({
                    'name': cipher_record['name'],
                    'remediation': cipher_record['remediation'],
                    'risk_factor': cipher_record['risk_factor'],
                    'keysize': str(scan_details[cipher_record['name']][0]) + " - " + str(scan_details[cipher_record['name']][1]),
                    'quantum_safe': 'Yes'
                })
                safe += 1
                safe_risk_factor += cipher_record['risk_factor']
                nodes.append({"id":cipher_record['name'],"color":"green", "size":600})
                edges.append({"source":scan_target, "target":cipher_record['name']})
            elif cipher_record['pqc_safe'] == True and int(scan_details[cipher_record['name']][1]) < int(cipher_record['keysize']): #and cipher_suite[tls_record['name']]=='TLSv13'
                detectors.append({
                    'name': cipher_record['name'],
                    'remediation': cipher_record['remediation'],
                    'risk_factor': 0.5,
                    'keysize': str(scan_details[cipher_record['name']][0]) + " - " + str(scan_details[cipher_record['name']][1]),
                    'quantum_safe': 'No'
                })
                unsafe += 1
                unsafe_risk_factor += 0.5
                nodes.append({"id":cipher_record['name'],"color":"yellow", "size":600})
                edges.append({"source":scan_target, "target":cipher_record['name']})
            else:
                detectors.append({
                    'name': cipher_record['name'],
                    'remediation': cipher_record['remediation'],
                    'risk_factor': 1.0,
                    'keysize': str(scan_details[cipher_record['name']][0]) + " - " + str(scan_details[cipher_record['name']][1]),
                    'quantum_safe': 'No'
                })
                unsafe += 1
                unsafe_risk_factor += cipher_record['risk_factor']
                nodes.append({"id":cipher_record['name'], "color":"red", "size":600})
                edges.append({"source":scan_target, "target":cipher_record['name']})
            nodes.append({"id":scan_details[cipher_record['name']][0],"color":"grey"})
            edges.append({"source":cipher_record['name'], "target":scan_details[cipher_record['name']][0]})
            nodes.append({"id":scan_details[cipher_record['name']][1],"color":"grey"})
            edges.append({"source":cipher_record['name'], "target":scan_details[cipher_record['name']][1]})
        stats = [{'Safe': safe, 'Unsafe': unsafe}]
        pie_chart_data = [{ "title": 'safe', "value": safe, "color": '#90EE90' }, { "title": 'unsafe', "value": unsafe, "color": '#F75D59' }]
            #print(pie_chart_data)
        if safe != 0:
            global_risk_factor = round(unsafe_risk_factor/(unsafe+safe),2)
        else:
            global_risk_factor = 1
        scan_status = "Type: File System Scan; PQC Secure: " + ("No" if stats[0]['Unsafe']>0 else "Yes")
        return {"scan_result":[detectors,pie_chart_data,stats], "graph": {"nodes":nodes, "edges":edges}, "scan_details":[{"params":"Scan Details", "values" : scan_status}, {"params":"Quantum Risk Factor", "values":global_risk_factor}, {"params":"Scan Source", "values": scan_source}]}
    elif scan_type == "statement":
        # Format sql statement to a single line statement
        sql_statement = scan_params['scan_target_statement']

        from microservices import encrypt_search
        references = encrypt_search.find_references(sql_statement)

        return references
    elif scan_type == "terraform":
        # Format sql statement to a single line statement
        terraform_statement = scan_params['scan_target_statement']

        with open('terraform.tf', 'w') as terraform_file:
            terraform_file.write(terraform_statement)

        from microservices import terraform_scan
        scan_results = terraform_scan.get_scan_results('terraform.tf')

        return scan_results
    elif scan_type == "cloudApplication":
        access_key_id = scan_params['scan_target_cloud_access_key_id']
        secret_access_key = scan_params['scan_target_cloud_secret_access_key']
        from microservices import cloud_app_scan
        scan_results = cloud_app_scan.scan_cloud_app(access_key_id, secret_access_key, scan_target_type)
        return scan_results
    else:
        return "Invalid scan type selected..!"
    return response

#Loading config file
with open('config.json') as config_file:
    config_data = json.load(config_file)
api = config_data['HOST1']
if __name__ == '__main__':
    app.run(host= api, port=5000, debug=True)

