# Purpose

This is a standalone library with independent modules that can be imported to check the post-quantum safety state of a client, host, server, API, or source code repository.

# Usage
## CLI
The library can be called directly from the command line with the following arguments.

```
% python3 quartz.py 
usage: quartz.py [-h] [-s SERVER] [-c CLIENT] [-l LOGGING] [-a API] [-t TYPE] [-p PORT] [-P PROTOCOL] [-r REPO]

optional arguments:
  -h, --help            show this help message and exit
  -s SERVER, --server SERVER
                        Scan a remote web server
  -c CLIENT, --client CLIENT
                        Scan the local host
  -l LOGGING, --logging LOGGING
                        Set logging level
  -a API, --api API     Scan an API server: URL | URL:PORT | IP | IP:PORT
  -t TYPE, --type TYPE  Type of API scan: cipher | full
  -p PORT, --port PORT  Remote port on the server to scan, By default, set to 443.
  -P PROTOCOL, --protocol PROTOCOL
                        Remote protocol on the server to scan, By default, set to https.
  -r REPO, --repo REPO  Repository to scan for presence of imported cryptographic modules.
```

The user can either check the PQ safety of a client (-c), server (-s), API (-a), or a repository (-r). For scanning APIs running on non-HTTP ports, the user can specify the specific port and protocol using the --port and --protocol options.

API scans can either be performed to check the cipher suite only, or perform a full scan using the -t option.

## Calling the individual modules
### Client Scan
The checkPQSafety method takes a tuple as input of the remote host address and it's port.
```
client_cipher_suite.checkPQSafety((remote_host,port))
```
The method returns a dictionary with two elements: a system level cipher suite and the shared cipher suite with the target host. The former lists the entire set of ciphers supported on the client system, while the latter lists the set chosen when a connection is initiated against the target.

### Server Scan
For scanning traditional web servers or remote hosts, we can use the server_cipher_suite module. The checkPQSafety method takes a host name or IP address as input.
```
server_cipher_suite.checkPQSafety(server_address)
```
It returns the cipher suite suppported by the server as response.

### API Scan
For scanning APIs running over different protocols and on different ports than HTTP(s), we can use the api_cipher_suite module. To initiate a scan against an API, the user needs to provide the API endpoint address, port, protocol, and choose a type of scan.
```
api_cipher_suite.apiScanInitiate(api_endpoint, port, protocol, type)
```
The port and protocol input parameters are optional. If no input is provided, they default to 443 and HTTPS. The type option can be used to run a full scan against the API if required. A full scan will not only check for the API cipher suite support, but also check headers, vulnerabilities, and more. In both cases, the scan result is generated in the form of JSON file.

### Repo Scan
To scan source code repositories, the user just needs to provide the target repo URL. Once the remote repository is cloned successfully, it is analyzed to determine the imported modules and a dictionary is returned with identified relevant modules and their safety status.
```
repo_cipher_scan.scan_repo(remote_repo)
```

### Checking PQC safety status
From the client, server and API modules, we receive a set of cipher suite algorithms determining their individual suppport levels. However, to check if these target systems are indeed PQ safe, the user can call the pq_safety_check module.
```
pq_safety_check.tls_checker(cipher_suite_support)
```
The tls_checker method takes a cipher suite list as input and returns a dictionary with two elements. The first element, is_safe, specifies if the list is PQ safe or not. And the second, lists the safety of each cipher in the list and recommendation against it.