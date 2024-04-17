# MIT License

# Copyright (c) 2024 Cisco Systems, Inc. and its affiliates

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import re
import argparse

# Regular expression pattern to match encryption function calls and extract the parameters
aes_pattern = r"(AES_ENCRYPT|AES_DECRYPT)\s*\((.*?)(?:,\s*(.*?))?(?:,\s*(.*?))?(?:,\s*(.*?))?(?:,\s*(.*?))?(?:,\s*(.*?))?(?:,\s*(.*?))?\)"
md5_pattern = r"(MD5)\s*\((.*?)\)"
sha_or_sha1_pattern = r"(SHA1|SHA)\s*\((.*?)\)"
sha2_pattern = r"(SHA2)\s*\((.*?)(,\s*(.*?))\)"

# Get select statement from user
#select_statement = input("Enter select statement: ")

def find_references(sql_statement):
    """
    Takes a SQL statement as input and finds all references to encryption and hashing method calls within it.

    Input: 
        - sql_statement : string
    Output: Returns a dictionary with two keys:
    - encryption_references: list of dictionaries, where each dictionary represents one method call. It has the following keys:
        - algorithm: name of the algorithm
        - encrypted_value: string or column being encrypted
        - key: string used as key for the encryption algorithm
        - iv: Initialization vector string, if required
        - kdf: Key derivation function name like pbkdf2
        - salt: string provided as salt to the kdf
        - iterations: no of iterations of the KDF
        - remediation: comments on the usage of the algorithm
    - hashing_references: list of dictionaries, where each dictionary represents one method call. It has the following keys:
        - algorithm: name of the hashing algorithm
        - hashed_value: string or column being hashed
        - hash_length: length of the hash generated
        - remediation: comments on the usage of the algorithm
    """
    encryption_references = []

    # Search for the pattern for AES calls in the statement
    matches = re.finditer(aes_pattern, sql_statement, re.IGNORECASE)
    for match in matches:
        encryption_reference = {}
        encryption_reference['algorithm'] = match.group(1)
        encryption_reference['encrypted_value'] = match.group(2)
        encryption_reference['key'] = match.group(3)
        encryption_reference['iv'] = match.group(4)
        encryption_reference['kdf'] = match.group(5)
        encryption_reference['salt'] = match.group(6)
        encryption_reference['iterations'] = match.group(7)
        encryption_reference['remediation'] = "MySQL uses AES with 128-bit key by default. AES-128 is insecure, and it should be replaced with 256-bit keys. Check the value of 'block_encryption_mode' variable to find more information."
        encryption_references.append(encryption_reference)

    hashing_references = []
    # Search for the pattern for MD5 hashing in the select statement
    matches = re.finditer(md5_pattern, sql_statement, re.IGNORECASE)
    for match in matches:
        hashing_reference = {}
        hashing_reference['algorithm'] = match.group(1)
        hashing_reference['encrypted_value'] = match.group(2)
        hashing_reference['hash_length'] = "128 bits"
        hashing_reference['remediation'] = "MD5 is not PQC secure. Replace all uses with SHA2."
        hashing_references.append(hashing_reference)

    # Search for the pattern for SHA1 hashing in the select statement
    matches = re.finditer(sha_or_sha1_pattern, sql_statement, re.IGNORECASE)
    for match in matches:
        hashing_reference = {}
        hashing_reference['algorithm'] = match.group(1)
        hashing_reference['encrypted_value'] = match.group(2)
        hashing_reference['hash_length'] = "160 bits"
        hashing_reference['remediation'] = "SHA1 is not PQC secure. Replace all uses with SHA2."
        hashing_references.append(hashing_reference)

    # Search for the pattern for SHA2 hashing in the select statement
    matches = re.finditer(sha2_pattern, sql_statement, re.IGNORECASE)
    for match in matches:
        hashing_reference = {}
        hashing_reference['algorithm'] = match.group(1)
        hashing_reference['encrypted_value'] = match.group(2)
        hashing_reference['hash_length'] = match.group(3).strip() + " bits"
        hashing_reference['remediation'] = "SHA2 is PQC secure."
        hashing_references.append(hashing_reference)

    return {"encryption_references" : encryption_references, "hashing_references" : hashing_references, "statement" : sql_statement, "search_strings" : ["AES_ENCRYPT", "AES_DECRYPT", "MD5", "SHA", "SHA1", "SHA2"]}

def createParser():
    # Create the parser
    parser = argparse.ArgumentParser()
    # Add arguments
    parser.add_argument('--statement', type=str, required=True, help="Provide the sql statement to be analysed.")
    return parser

if __name__=='__main__':
    parser = createParser()
    # Parse the argument
    args = parser.parse_args()
    sql_statement = args.statement
    print(find_references(sql_statement))