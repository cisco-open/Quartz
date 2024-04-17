# MIT License

# Copyright (c) 2024 Cisco Systems, Inc. and its affiliates

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


from flask import Flask,request,jsonify
#from flask_mysqldb import MySQL
import mysql.connector as connector
from mysql.connector import Error
from flask_mongoengine import MongoEngine
from logging.config import dictConfig
from database.db import initialize_db
from database.models import scan

import subprocess
from threading import Thread
from datetime import datetime
import json

#Logging

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] [%(levelname)s | %(module)s] %(message)s",
                "datefmt": "%B %d, %Y %H:%M:%S %Z",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
            "time-rotate": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "filename": "pqc_analyze.log",
                "when": "D",
                "interval": 2,
                "backupCount": 5,
                "formatter": "default",
            },
        },
        "root": {"level": "DEBUG", "handlers": ["console", "time-rotate"]},
    }
)

app = Flask(__name__)

with open('/etc/sscs.config.json','r') as config_file:
    config = json.load(config_file)


token = config.get("ACCESS_TOKEN")
db_host = config.get("DB_HOST")
repo_db = config.get("DB_DATABASE")
db_user = config.get("DB_USER")
pass_word = config.get("DB_PASSWORD")
server_ip = config.get("HOST_IP")

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

initialize_db(app)

# Change to include cipher name validation
def algo_name_validation(cipher_suite):
    pass

# Change to include normal server url validation, either as IP or domain
def url_validation(server_host):
    return server_host['server']

def fetch_scan_query_generator():
    parameterized_query = "select * from api_scan where scan_id = %s"
    return parameterized_query

def create_algo_query_generator():
    parameterized_query = "insert into tls_crypto_algo(algo_name,pqc_safe,risk_factor,comments) values(%s,%s,%s,%s)"
    return parameterized_query

def update_algo_query_generator():
    parameterized_query = "update tls_crypto_algo set pqc_safe=%s, risk_factor=%s, comments=%s where algo_name=%s"
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
    parameterized_query = "insert into api_scan(host,port,protocol,status) values(%s,%s,%s,%s)"
    return parameterized_query

def update_scan_query_generator():
    parameterized_query = "update api_scan set scan_status=%s where scan_id=%s"
    return parameterized_query

def tls_query_generator(cipher_suite):
    params = len(cipher_suite)
    parameter_strings = "%s," * params
    paramterized_query = "select * from tls_crypto_algo where algo_name in (" + parameter_strings[:-1] + ")"
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
    algo_name = request.json['spec']['algo_name']
    response = {}
    try:
        # verify and sanitize the input
        parameterized_query = delete_algo_query_generator()
        updated_id = sql_delete(parameterized_query,(algo_name,))
        response[algo_name] = "Deleted record successfully!"
    except:
        # alert for failure
        app.logger.error("Failed to delete record: " + algo_name)
        response[algo_name] = "Failed to delete record."
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
    response = {}
    try:
        # verify and sanitize the input
        parameterized_query = fetch_all_algo_query_generator()
        records = sql_select(parameterized_query,())
        for record in records:
            response[record[0]] = {"pqc_safe": record[1], "risk_factor": record[2], "comments":record[3]}
    except:
        # alert for failure
        app.logger.error("Failed to fetch records")
        response['status'] = "Failed to fetch records"
    return response

def check_pqc_safety(cipher_suite):
    pqc_safe = False
    generated_query = tls_query_generator(cipher_suite)
    results = sql_select(generated_query,tuple(cipher_suite))
    output = []
    for result in results:
        if result[1]==True:
            pqc_safe = True
        output.append({"name":result[0], "pqc_safe":result[1], "risk_factor":result[2], "recommendation":result[3]})
    return {'is_safe': pqc_safe, "tls_algo_record": output}

@app.route("/getHostSecurity", methods = ['POST'])
def check_host_safety():
    cipher_suite = request.json['cipher_suite']
    safety_check = check_pqc_safety(cipher_suite)
    return jsonify(safety_check)

@app.route("/getServerSecurity", methods = ['POST'])
def check_server_safety():
    from microservices import server_cipher_suite
    server_obj = request.json
    server_url = url_validation(server_obj)
    cipher_suite = server_cipher_suite.getServerCipherSuites(server_url)
    safety_check = check_pqc_safety(cipher_suite)
    return jsonify(safety_check)

def launch_scan(scan_id, api_host, port, protocol, file_name):
    from microservices import api_cipher_suite
    api_cipher_suite.apiScanInitiate(scan_id, api_host, port, protocol, file_name)

@app.route("/launchAPIScan", methods = ['POST'])
def launch_API_scan():
    from microservices import api_cipher_suite
    # create a scan record as Initiating
    server_obj = request.json
    api_host = server_obj['host'] #url_validation(server_obj)
    port = server_obj['port']
    protocol = server_obj['protocol']
    # Change this to python script execution from shell instead of method call
    now = datetime.now()
    json_out = api_host + '_' + now.strftime("%Y%m%d-%H%M") + '.json'
    # Update scan status as "Initiated"
    parameterized_query = create_scan_query_generator()
    try:
        scan_id = sql_insert(parameterized_query,(api_host,port,protocol,"Initiated"))
    except:
        app.logger.error("Failed to insert new scan record")
        return {"status": "Failed to initialize scan. Try again later!!"}
    options = '--host=' + api_host + ' --scan_id=' + str(scan_id) + ' --file-name=' + json_out
    if port != '':
        options += ' --port=' + port
    if protocol != '':
        options += ' --protocol=' + protocol
    try:
        thread = Thread(target=launch_scan,args=(scan_id, api_host, port, protocol, json_out))
        thread.start()
        #proc = subprocess.Popen(["python3 ./microservices/api_cipher_suite.py " + options], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
    except:
        app.logger.error("Failed to launch bash script.")

        #Update scan status in database as "Failed"
        parameterized_query = update_scan_query_generator()
        try:
            scan_id = sql_update(parameterized_query,("Failed",scan_id))
        except:
            app.logger.error("Failed to update scan record after failure to initialize.")
            return {"status": "Failed to initialize scan. Try again later!!"}

        return {"status": "Failed to initialize scan. Try again later!!"}
    #scan_analysis = api_cipher_suite.getScanAnalysis(server_url,server_obj['port'],server_obj['protocol'])

    # Return to user without waiting for completion of script
    return {"scan_id": scan_id, "status": "Scan initiated. Please wait for the results to be updated."}

@app.route("/getScanDetails", methods = ['POST'])
def get_scan_details():
    # create a scan record
    scan_obj = request.json
    scan_id = scan_obj['scanId'] #url_validation(server_obj)

    # Call method to fetch scan status from DB
    query = fetch_scan_query_generator()
    scan_results = sql_select(query,(scan_id,))

    for scan_result in scan_results:
        if scan_result[4] != "Complete":
            return {"status": scan_result[4]}
        elif scan.objects(scan_id=scan_result[0]):
            scan_out = open(scan_result[5], 'r')
            scan_output = json.loads(scan_out.read())
            scan_out.close()
            scan_obj = scan(scan_id=scan_id,scan_result=scan_output)
            scan_obj.save()
        else:
            scan_output = scan.objects(scan_id=scan_id).first()
            return {"scan_id":scan_id, "scan_result": scan_output.scan_result}

    # Return scan as "In progress" if scan is still running, otherwise return scan details
    return {"scan_id":scan_id, "scan_result": scan_output}

@app.route("/getScanStatus", methods = ['POST'])
def get_scan_status():
    scan_obj = request.json
    response = {}
    scan_ids = list(scan_obj['scan_ids'])
    scan_db_obj = ''
    for scan_id in scan_ids:
        scan_db_obj = scan.objects(scan_id=scan_id)
        if scan_db_obj:
            response[scan_id] = 'Completed'
        else:
            response[scan_id] = 'In Progress'
    return response

if __name__ == '__main__':
    app.run(host= '127.0.0.1', port=5000, debug=True)

