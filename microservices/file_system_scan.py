# MIT License

# Copyright (c) 2024 Cisco Systems, Inc. and its affiliates

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import subprocess
import re
import os
import json

def is_encrypted_device(device):
    """
    Check if a block device is encrypted using LUKS
    Returns True if the device is encrypted, False otherwise
    """
    try:
        output = subprocess.check_output(["cryptsetup", "isLuks", device], stderr=subprocess.STDOUT).decode()
    except FileNotFoundError:
        return "cryptsetup not installed. Run 'apt install cryptsetup' to install."
    except:
        return False
    return "is a LUKS device" in output


def get_encryption_details(device):
    """
    Get encryption details for a block device encrypted using LUKS
    Returns a dictionary with the following keys:
    - cipher: the encryption algorithm used
    - key_size: the key size in bits
    - mode: the encryption mode (e.g., "xts")
    """
    try:
        encryption = subprocess.check_output(['cryptsetup', 'luksDump', '/dev/{}'.format(device)]).decode()
    except FileNotFoundError:
        return "cryptsetup not installed. Run 'apt install cryptsetup' to install."
    except:
        return False
        
    # Parse the encryption output and print relevant details
    cipher_name = encryption.split('\n')[2].split(':')[1].strip()
    cipher_mode = encryption.split('\n')[3].split(':')[1].strip()
    hash_spec = encryption.split('\n')[4].split(':')[1].strip()
    mk_bits = encryption.split('\n')[5].split(':')[1].strip()
    mk_iterations = encryption.split('\n')[10].split(':')[1].strip()
    
    return {"cipher": f"{cipher_name}", "mode" : f"{cipher_mode}", "hash_spec": f"{hash_spec}", "key_size" : f"{mk_bits}", "key_iterations" : f"{mk_iterations}"}

def get_disk_encryption_details():
    """
    Get disk encryption details for all block devices
    Returns a list of dictionaries, where each dictionary represents one block device.
    The dictionary contains the following keys:
    - name: the name of the block device
    - encrypted: True if the device is encrypted, False otherwise
    - cipher: the encryption algorithm used (if encrypted)
    - key_size: the key size (if encrypted)
    - key_iterations: no of iterations used to derive the key
    - hash_spec: the hashing method used
    """
    disks = []
    # Get list of all block devices and their mount points
    devices = subprocess.check_output(['lsblk', '-o', 'NAME,MOUNTPOINT']).decode().split('\n')[1:-1]
    devices = [d.split() for d in devices]

    # Loop through all devices and check if they are encrypted
    for device in devices:
        dev_name = device[0]
        try:
            disk = {"name": dev_name, "encrypted": False, "cipher": "", "hash_spec": "", "key_size": "", "key_iterations": ""}
            if is_encrypted_device(dev_name):
                disk["encrypted"] = True
                encryption_details = get_encryption_details(disk["name"])
                if encryption_details:
                    disk["cipher"] = encryption_details["cipher"]
                    disk["key_size"] = encryption_details["key_size"]
                    disk["hash_spec"] = encryption_details["hash_spec"]
                    disk["key_iterations"] = encryption_details["key_iterations"]
            disks.append(disk)
        except:
            pass
    return disks

def get_all_files(path):
    """
    Recursively get all files in a directory and its subdirectories.
    Returns a list of file paths found
    """
    all_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            all_files.append(file_path)
    return all_files

def get_file_encryption_status(file_path):
    """
    Check the encryption status of a file.
    Returns a dictionary with the following keys:
    - file_path: the name of the file being checked
    - key_size: the key size in bits
    - method: the encryption method (e.g., "aes")
    - encrypted: True if file is encrypted, False otherwise
    """
    output = subprocess.check_output(['file', '-L', '-b', file_path]).decode('utf-8')
    if 'encrypted' in output.lower():
        # Get the encryption method and key size
        try:
            output = subprocess.check_output(['cryptsetup', 'luksDump', file_path]).decode('utf-8')
        except FileNotFoundError:
            return "cryptsetup not installed. Run 'apt install cryptsetup' to install."
        except:
            return False
        method = re.findall(r'Cipher name:\s+(\w+)', output)[0]
        key_size = re.findall(r'Key Slot 0:\s+(\d+) bits', output)[0]
        encrypted_file = {
            'file_path': file_path,
            'encrypted': True,
            'method': method,
            'key_size': key_size
        }
    else:
        # Add the file to the list of unencrypted files
        encrypted_file = {
            'file_path': file_path,
            'encrypted': False,
            'method': None,
            'key_size': None
        }
    return encrypted_file

def get_all_file_encryption_status(path):
    """
    Get the encryption status of all files in a directory and its subdirectories.
    Returns a list of dictionaries with the following keys:
    - file_path: the name of the file being checked
    - key_size: the key size in bits
    - method: the encryption method (e.g., "aes")
    - encrypted: True if file is encrypted, False otherwise
    """
    all_files = get_all_files(path)
    file_encryption_status = []
    for file in all_files:
        status = get_file_encryption_status(file)
        file_encryption_status.append(status)
    return file_encryption_status

def get_algorithm_details():
    """
    Get the list of all encryption methods supported on the system
    Returns a list of dictionaries with the following keys:
    - name: the name of the algorithm
    - driver: the name of the driver used to implement the algorithm
    - module: the name of the module from which algorithm is loaded (e.g., "kernel")
    - type: type of the algorithm (e.g., "cipher")
    - min_keysize: the minimum key length supported by the algorithm
    - max_keysize: the maximum key length supported by the algorithm
    """
    # Open the /proc/crypto file for reading
    with open('/proc/crypto', 'r') as f:
        contents = f.read()

    # Define regex patterns to match the algorithm details
    name_pattern = re.compile(r'^\s*name\s*:\s*(.*)$')
    driver_pattern = re.compile(r'^\s*driver\s*:\s*(.*)$')
    module_pattern = re.compile(r'^\s*module\s*:\s*(.*)$')
    type_pattern = re.compile(r'^\s*type\s*:\s*(.*)$')
    min_keysize_pattern = re.compile(r'^\s*min keysize\s*:\s*(\d+)$')
    max_keysize_pattern = re.compile(r'^\s*max keysize\s*:\s*(\d+)$')
    #matches = re.findall(pattern, output, re.DOTALL)

    algorithms=[]
    # Read from temp file
    # with open('temp.txt', 'r') as f:
    #     crypto_data = f.read()
    sections = contents.split('\n\n')
    for section in sections:
        algorithm = {}
        for line in section.split('\n'):
            name_match = name_pattern.match(line)
            if name_match:
                algorithm['name'] = name_match.group(1)
                continue
            driver_match = driver_pattern.match(line)
            if driver_match:
                algorithm['driver'] = driver_match.group(1)
                continue
            module_match = module_pattern.match(line)
            if module_match:
                algorithm['module'] = module_match.group(1)
                continue
            type_match = type_pattern.match(line)
            if type_match:
                algorithm['type'] = type_match.group(1)
                continue
            min_keysize_match = min_keysize_pattern.match(line)
            if min_keysize_match:
                algorithm['min_keysize'] = int(min_keysize_match.group(1))
                continue
            max_keysize_match = max_keysize_pattern.match(line)
            if max_keysize_match:
                algorithm['max_keysize'] = int(max_keysize_match.group(1))
                continue
        if len(algorithm.keys()) != 0 and algorithm['type'] == 'cipher':
            algorithms.append(algorithm)

    # Print the list of dictionaries
    return algorithms

def get_certificate_details():
    """
    Returns a list of dictionaries with the following keys:
    - name: the name of the certificate
    - key_size: the key size in bits
    - algorithm: the signing algorithm supported by the certificate
    - hash_algorithm: the hashing algorithm supported by the certificate
    """
    # Run the openssl command to get the list of certificates
    output = subprocess.check_output(['openssl', 'x509', '-in', '/etc/ssl/certs/ca-certificates.crt', '-noout', '-text'])

    # Extract the details for each certificate
    cert_details = []
    cert_blocks = re.split(r'-----END CERTIFICATE-----\n', output.decode('utf-8'))
    for block in cert_blocks:
        # Skip the last block (it's empty)
        if not block:
            continue
        
        # Extract the certificate details
        details = re.findall(r'(\w+) \((\d+) bit\).*\n\s*(Signature Algorithm):\s+(\w+)', block, re.DOTALL)

        # Convert the details to a dictionary and add them to the list
        for d in details:
            cert_detail = {
                'name': d[0],
                'key_size': int(d[1]),
                'algorithm': d[2],
                'hash_algorithm': d[3]
            }
            cert_details.append(cert_detail)

    # Print the list of certificate details
    return cert_details

# Check if the device is the root file system
def is_root_device(device):
    """
    Returns True if the device is the root device, False otherwise
    """
    output = subprocess.check_output(["lsblk", "-no", "name", device], stderr=subprocess.STDOUT)
    return output.decode().strip() == "/"

# Get a list of all block devices
def get_block_devices():
    """
    Returns list of all block devices configured on the system
    """
    output = subprocess.check_output(["lsblk", "-d", "-no", "name"], stderr=subprocess.STDOUT)
    return output.decode().strip().split("\n")

# Check if any block devices are encrypted
def is_encrypted_system():
    """
    Returns true if any block device is encrypted, False otherwise
    """
    devices = get_block_devices()
    for device in devices:
        if is_encrypted_device(device) and not is_root_device(device):
            return True
    return False

# Check if the root file system is encrypted
def is_root_encrypted():
    """
    Returns True if the the root device is encrypted, False otherwise
    """
    return is_encrypted_device("/dev/mapper/root")

# Check if full device encryption is turned on
def is_full_encryption_on():
    """
    Returns True if either the root device or any one of the system devices are encrypted, False otherwise
    """
    return is_encrypted_system() or is_root_encrypted()

def get_scan_results():
    # Supported algorithm information
    algorithms = get_algorithm_details()
    # Configured certificate details
    certificates = get_certificate_details()
    # Device Enryption Information
    device_encryption_details = get_disk_encryption_details()
    # All user files encryption details
    file_encryption_details = get_all_file_encryption_status("/home")
    # Is full disk encryption enabled or not
    if is_full_encryption_on():
        fde = "Full device encryption is ON"
    else:
        fde = "Full device encryption is OFF"
    response = {"algorithms" : algorithms, "certificates" : certificates, "device_encryption_details" : device_encryption_details, "file_encryption_details" : file_encryption_details, "fde" : fde}
    return response

if __name__=='__main__':
    print(get_scan_results())