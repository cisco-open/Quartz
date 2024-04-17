# MIT License

# Copyright (c) 2024 Cisco Systems, Inc. and its affiliates

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from mysql.connector import Error
import mysql.connector as connector
import json
import sys
import subprocess
import argparse

# Project DB
with open('/backend/pqc.config.json','r') as config_file:
    config = json.load(config_file)

service_user = config.get("SERVICE_USER")
service_password = config.get("SERVICE_PASSWORD")

token = config.get("ACCESS_TOKEN")
db_host = config.get("DB_HOST")
repo_db = config.get("DB_DATABASE")
db_user = config.get("DB_USER")
pass_word = config.get("DB_PASSWORD")
server_ip = config.get("HOST_IP")

# Create MySQL connector
project_db = connector.connect(
    host=db_host,
    database=repo_db,
    user=db_user,
    password=pass_word
)

# Specific Database Checks

def check_cipher(ciphers):
    pqc_safe = False
    ciphers = [x.strip() for x in ciphers.split(',')]
    params = len(ciphers)
    parameter_strings = "%s," * params
    generated_query = f"select * from tls_crypto_algo where algo_name in ({parameter_strings[:-1]})"
    if project_db.is_connected():
        # creating database cursor
        cursor = project_db.cursor()
        cursor.execute(generated_query,tuple(ciphers))
        records = cursor.fetchall()
        #Closing the cursor
        cursor.close()
    output = {}
    for record in records:
        output[record[0]] = {"status" : f"'name' : {record[0]}, 'risk_factor' : {record[2]}, 'remediation' : {record[3]}", "is_safe" : record[1]}
    for cipher in ciphers:
        if cipher not in output.keys():
            output[cipher] = {"status" : f"'name' : {cipher}, 'status' : 'Record not found for cipher'", "is_safe" : False}
    return output

def check_mysql(host,port):
    # Local variable to store check results
    response = []
    safe = 0
    unsafe = 0
    risk_factor_safe = 0
    risk_factor_unsafe = 0
    global_risk_factor = 0

    # Check connection to target host using service account credentials
    # Create MySQL connector to initiate connection with taget host
    mydb = connector.connect(
        host=host,
        port=port,
        user=service_user,
        password=service_password,
        database="mysql"
    )
    
    if not mydb.is_connected():
        return "Failed to connect using service credentials..!"

    # Check if database is setup to accept SSL connections
    # Open a cursor to run queries
    cursor = mydb.cursor()
    cursor.execute("show variables like 'have_ssl';")
    result = cursor.fetchone()
    # Close the cursor
    cursor.close()

    # Check if SSL support is enabled
    if result[1] == 'YES':
        response.append({"key" : "SSL/TLS Enabled", "value" : 'Yes', "safe" : "Yes"})
        safe += 1
        risk_factor_safe += 0.1
    else:
        response.append({"key" : "SSL/TLS Enabled", "value" : 'No', "safe" : "No"})
        unsafe += 1
        risk_factor_unsafe += 1
    
    # Check if unencrypted connections are allowed by the database
    # Open a cursor to run queries
    cursor = mydb.cursor()
    cursor.execute("show variables like 'require_secure_transport';")
    result = cursor.fetchone()
    # Close the cursor
    cursor.close()

    # Check if secure transport is enabled
    if result[1] == 'ON':
        response.append({"key" : "Require Secure Transport", "value" : 'Yes', "safe" : "Yes"})
        safe += 1
        risk_factor_safe += 0.1
    else:
        response.append({"key" : "Require Secure Transport", "value" : 'No', "safe" : "No"})    
        unsafe += 1
        risk_factor_unsafe += 1

    # Supported TLS versions for normal users and admins
    # Open a cursor to run queries
    cursor = mydb.cursor()
    cursor.execute("show variables like '%tls_version';")
    result = cursor.fetchall()
    # Close the cursor
    cursor.close()

    # Determine supported TLS versions
    for record in result:
        for tls_version in record[1].split(','):
            if record[0].find("admin") != -1:
                if tls_version != "TLSv1.3":
                    response.append({"key" : "TLS Versions Supported (Admin)", "value" : tls_version, "safe" : "No"})
                    unsafe += 1
                    risk_factor_unsafe += 1
                else:
                    response.append({"key" : "TLS Versions Supported (Admin)", "value" : tls_version, "safe" : "Yes"})
                    safe += 1
                    risk_factor_safe += 0.1
            else:
                if tls_version != "TLSv1.3":
                    response.append({"key" : "TLS Versions Supported (Normal Users)", "value" : tls_version, "safe" : "No"})
                    unsafe += 1
                    risk_factor_unsafe += 1
                else:
                    response.append({"key" : "TLS Versions Supported (Normal Users)", "value" : tls_version, "safe" : "Yes"})
                    safe += 1
                    risk_factor_safe += 0.1
    
    # Configured ciphersuites for normal users and admmins
    # Open a cursor to run queries
    cursor = mydb.cursor()
    cursor.execute("show variables like '%tls_ciphersuites';")
    result = cursor.fetchall()
    # Close the cursor
    cursor.close()
    result = [["admin_tls_ciphersuites", "AEAD-CHACHA20-POLY1305-SHA256, TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA, TLS_RSA_WITH_3DES_EDE_CBC_SHA"], ["tls_ciphersuites", "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA, TLS_RSA_WITH_AES_128_CBC_SHA256"]]
    # Determine supported TLS versions
    for record in result:
        if len(record[1]) != 0:
            cipher_states = check_cipher(record[1])
            for tls_cipher in record[1].split(','):
                cipher_state = cipher_states[tls_cipher.strip()]
                if record[0].find("admin") != -1:
                    if cipher_state['is_safe'] == False:
                        response.append({"key" : "TLS Ciphersuites Configured (Admin)", "value" : cipher_state['status'], "safe" : "No"})
                        unsafe += 1
                        risk_factor_unsafe += 1
                    else:
                        response.append({"key" : "TLS Ciphersuites Configured (Admin)", "value" : cipher_state['status'], "safe" : "Yes"})
                        safe += 1
                        risk_factor_safe += 0.1
                else:
                    if cipher_state['is_safe'] == False:
                        response.append({"key" : "TLS Ciphersuites Configured (Normal Users)", "value" : cipher_state['status'], "safe" : "No"})
                        unsafe += 1
                        risk_factor_unsafe += 1
                    else:
                        response.append({"key" : "TLS Ciphersuites Configured (Normal Users)", "value" : cipher_state['status'], "safe" : "Yes"})
                        safe += 1
                        risk_factor_safe += 0.1
        else:
            if record[0].find("Admin") != -1:
                response.append({"key" : "TLS Ciphersuites Configured (Admin)", "value" : "No ciphersuites found!", "safe" : "No"})
                unsafe += 1
                risk_factor_unsafe += 1
            else:
                response.append({"key" : "TLS Ciphersuites Configured (Normal Users)", "value" : "No ciphersuites found!", "safe" : "No"})
                unsafe += 1
                risk_factor_unsafe += 1

    # Check if plugins are installed to manage keyrings
    # Open a cursor to run queries
    cursor = mydb.cursor()
    cursor.execute("select plugin_name from information_schema.plugins where plugin_name like 'keyring%' and plugin_type = 'keyring' and plugin_status = 'active';")
    result = cursor.fetchall()
    # Close the cursor
    cursor.close()

    # Determine active plugins
    active_plugin_list = [record[0] for record in result]
    if len(active_plugin_list) != 0:
        for plugin in active_plugin_list:
            response.append({"key" : "Active Keyring Plugins", "value" : plugin, "safe" : "Yes"})
            safe += 1
            risk_factor_safe += 0.1
    else:
        response.append({"key" : "Active Keyring Plugins", "value" : 'No active plugins. Encryption is not enabled!!', "safe" : "No"})
        unsafe += 1    
        risk_factor_unsafe += 1

    # Find all keys and their type with length (in bytes) using stored procedure
    # Open a cursor to run queries
    cursor = mydb.cursor()
    # Delete stored procedure if it exists
    delete_procedure = """DROP PROCEDURE IF EXISTS find_key_details;"""
    cursor.execute(delete_procedure)
    # Create stored procedure
    stored_procedure = """
        CREATE PROCEDURE find_key_details()
        BEGIN
            select key_id, keyring_key_type_fetch(key_id), keyring_key_length_fetch(key_id) FROM performance_schema.keyring_keys;
        END;"""
    cursor.execute(stored_procedure)
    # try:
    #     cursor.callproc('find_key_details')
    #     key_list = [ record for result in cursor.stored_results() for record in result.fetchall() ]
    # except:
    key_list = []
    #print(key_list)
    # Close the cursor
    cursor.close()

    # Determine active plugins
    if len(key_list) != 0:
        # Find details of each key
        key_details = ""
        for key in key_list:
            # Determine key details for each key Id
            key_details = f"type: {key[2]}, size (in bytes) : {key[1]}"
            if key[2] == "AES"  and int(key[1]) >= 32:
                response.append({"key" : f"Active Keys (key_id = {key[0]})", "value" : key_details, "safe" : "Yes"})
                safe += 1
                risk_factor_safe += 0.1
            else:
                response.append({"key" : f"Active Keys (key_id = {key[0]})", "value" : key_details, "safe" : "No"})
                unsafe += 1
                risk_factor_unsafe += 1
    else:
        response.append({"key" : "Active Keys", "value" : 'No active keys!!', "safe" : "No"}) 
        unsafe += 1   
        risk_factor_unsafe += 1

    # Check if encryption is enabled by default for schemas and tablespaces
    # Open a cursor to run queries
    cursor = mydb.cursor()
    cursor.execute("show variables like 'default_table_encryption';")
    result = cursor.fetchone()
    # Close the cursor
    cursor.close()

    # Check if database level encryption is enabled by default
    if result[1] == 'ON':
        response.append({"key" : "Default Table Encryption", "value" : 'Yes', "safe" : "Yes"})
        safe += 1
        risk_factor_safe += 0.1
    else:
        response.append({"key" : "Default Table Encryption", "value" : 'No', "safe" : "No"})
        unsafe += 1
        risk_factor_unsafe += 1

    # Identify user schemas
    # Open a cursor to run queries
    cursor = mydb.cursor()
    cursor.execute("show schemas;")
    result = cursor.fetchall()
    # Close the cursor
    cursor.close()

    # Determine user defined schemas
    schema_list = ','.join([f"'{record[0]}'" for record in result if record[0] not in ['mysql', 'information_schema', 'performance_schema', 'sys']])

    # Check if encryption is enabled for user defined schemas
    # Open a cursor to run queries
    cursor = mydb.cursor()
    cursor.execute(f"select schema_name, default_encryption from information_schema.schemata where schema_name in ({schema_list});")
    result = cursor.fetchall()
    # Close the cursor
    cursor.close()

    # Determine user defined schemas
    schema_encryption_state = [record for record in result]
    if len(schema_encryption_state) != 0:
        for record in schema_encryption_state:
            if record[1] == "YES":
                response.append({"key" : "User Defined Schema Encryption State", "value" : f"Schema Name : {record[0]}, Encrypted : {record[1].title()}", "safe" : "Yes"})
                safe += 1
                risk_factor_safe += 0.1
            else:
                response.append({"key" : "User Defined Schema Encryption State", "value" : f"Schema Name : {record[0]}, Encrypted : {record[1].title()}", "safe" : "No"})
                unsafe += 1
                risk_factor_unsafe += 1
    else:
        response.append({"key" : "User Defined Schema Encryption State", "value" : f"No user defined schemas", "safe" : "No"})
        unsafe += 1
        risk_factor_unsafe += 1

    # Check if encryption was enabled for user defined tables during creation
    # Open a cursor to run queries
    cursor = mydb.cursor()
    cursor.execute(f"select table_schema, table_name, create_options from information_schema.tables where table_schema in ({schema_list});")
    result = cursor.fetchall()
    # Close the cursor
    cursor.close()

    # Determine table level encryption status
    table_encryption_state = []
    for record in result:
        if record[2].find("ENCRYPTION='Y'") != -1 or record[2].find('ENCRYPTION="Y"') != -1:
            table_encryption_state = f"'schema/table' : {record[0]}/{record[1]}, 'encrypted' : 'Yes'"
            response.append({"key" : f"User Defined Tables Encryption Status", "value" : table_encryption_state, "safe" : "Yes"})
            safe += 1
            risk_factor_safe += 0.1
        else:
            table_encryption_state = f"'schema/table' : {record[0]}/{record[1]}, 'encrypted' : 'No'"
            response.append({"key" : f"User Defined Tables Encryption Status", "value" : table_encryption_state, "safe" : "No"})
            unsafe += 1
            risk_factor_unsafe += 1
    stats = [{'Safe': safe, 'Unsafe': unsafe}]
    pie_chart_data = [{ "title": 'safe', "value": safe, "color": '#90EE90' }, { "title": 'unsafe', "value": unsafe, "color": '#F75D59' }]
    if safe != 0 or unsafe != 0:
        global_risk_factor = risk_factor_unsafe/(safe+unsafe)
    return [response, pie_chart_data, stats, global_risk_factor]

def scanner(db_type, db_host, db_port):
    result = ""
    if db_type == "mysql":
        result = check_mysql(db_host, db_port)
    return result

# Command line argument parser
def createParser():
    # Create the parser
    parser = argparse.ArgumentParser()
    # Add arguments
    parser.add_argument('--type', type=str, required=True, help="Database flavor like MySQL, MSSQL, etc.")
    parser.add_argument('--host', type=str, required=True, help="Target database host (IP|URL)")
    parser.add_argument('--port', type=str, required=True, help="Target database port")
    return parser

if __name__=='__main__':
    parser = createParser()

    # Parse the argument
    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
    db_host = args.host
    db_type = args.type.lower()
    db_port = int(args.port)
    # Store check results in a local variable
    result = ""

    # Check database type to perform specific tests
    if db_type == 'mysql':
        result = check_mysql(db_host, db_port)
        print(result)