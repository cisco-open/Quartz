# MIT License

# Copyright (c) 2024 Cisco Systems, Inc. and its affiliates

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import logging
import os
import time

def tls_checker(cipher_suite):
    cwd = os.getcwd()
    algo_info_path = cwd+'/static/algo.info'
    # Update algorithm info, if not updated in the last 24 hours
    last_modified_time = os.path.getmtime(algo_info_path)
    current_time = time.time()
    if (current_time - last_modified_time)/3600 > 24:
        # Download the file again
        pass

    if len(cipher_suite)==0:
        return {"is_safe":False, "result": "No cipher suite provided."}
    # Capture algorithm recommendations for comparison against input suite
    cipher_info = {}
    # For the library implementation, we are using a static file to store the algorithm information
    
    with open(algo_info_path, 'r') as algo:
        algo_data = algo.readlines()
        for data in algo_data:
            delimited_data = data.split(',')
            cipher_info[delimited_data[0]] = {'pqc_safe' : delimited_data[1], 'risk_factor' : delimited_data[2], 'comments' : delimited_data[3]}
    check_result = {}
    is_safe = False
    for cipher in cipher_suite:
        if cipher not in cipher_info.keys():
            check_result[cipher] = {'pqc_safe' : 'Unknown', 'risk_factor' : 'Unknown', 'comments' : 'Might not be safe to use, please use a recommended algorithm!'}
        else:
            check_result[cipher] = cipher_info[cipher]
            if cipher_info[cipher]['pqc_safe'] == '1':
                is_safe = True
    return {'is_safe': is_safe, 'result': check_result}