## Client Scan

**Function** : Determines the TLS cipher suites supported on a host system, and the cipher suites it choses to share while initiating a TLS connection with a client.

### Invoking on the command line

```
python3 client_cipher_suite.py --host <host> --port <port>
```

### Invoking as a method

```
from client_cipher_suite import checkPQSafety
scan_results = checkPQSafety((target,port)) # Target can be IP or hostname
```

### Invoking as a REST API

#### Request

```
POST /scanClient HTTP/1.1
Host: localhost:5000
Content-Type: application/json
Content-Length: 124

Example payload for testing /scanClient

{
    "scan_type" : "client",
    "target" : "google.com",
    "scan_target_port" : "443",
    "scan_target_protocol" : ""
}
```

## Server Scan

**Function** : Identify TLS cipher suites selected by a target server while accepting a TLS connection.

**Libraries** :

- sslscan 0.5.1

### Invoking on the command line

```
python server_cipher_suite.py --host <host>
```

### Invoking as a method

```
from server_cipher_suite import getServerScanAnalysis
scan_results = getServerScanAnalysis(target) # Target can be IP or hostname
```

### Invoking as a REST API

#### Request

```
POST /scanServer HTTP/1.1
Host: localhost:5000
Content-Type: application/json
Content-Length: 124

Example payload for testing /scanServer

{
    "scan_type" : "server",
    "target" : "google.com",
    "scan_target_port" : "443",
    "scan_target_protocol" : ""
}
```

## Repo Scan

**Function** : Identify components used in a source code repository and determine their PQC safety status

**Libraries** :

- crypto detector (https://github.com/Wind-River/crypto-detector)

### Invoking on the command line

```
python repo_cipher_scan.py --repo <repo>
```

### Invoking as a method

```
from repo_cipher_scan import scan_repo
scan_results = scan_repo(target) # Target can be IP or hostname
```

### Invoking as a REST API

#### Request

```
POST /scanRepo HTTP/1.1
Host: localhost:5000
Content-Type: application/json
Content-Length: 79

Example payload for testing /scanRepo

{
    "scan_type" : "repo",
    "target" : "github_url"
}
```

## API Scan

**Function** : Scans servers hosting TLS connections over any port using STARTTLS mechanism. It identifies TLS cipher suites used to setup the connection.

**Library** :

- testtls.sh 3.0 (https://github.com/drwetter/testssl.sh.git)

### Invoking on the command line

```
python3 api_cipher_suite.py --host <host> --port <port> --protocol <protocol>
```

### Invoking as a method

```
from api_cipher_suite import getScanAnalysis
scan_results = getScanAnalysis(host, port, protocol)
```

### Invoking as a REST API

```
POST /scanApi HTTP/1.1
Host: localhost:5000
Content-Type: application/json
Content-Length: 122

Example payload for testing /scanApi

{
    "scan_type" : "api",
    "target" : "mysql",
    "scan_target_port" : "3306",
    "scan_target_protocol" : "mysql"
}
```

## File System Scan

**Function** : Returns details of encryption algorithms supported natively on OS.

### Invoking on the command line

```
python3 file_system_scan_passive.py --os <os>
```

### Invoking as a method

```
from file_system_scan_passive import get_algos
scan_results = get_algos(os)
```

### Invoking as a REST API

```
POST /scanFS HTTP/1.1
Host: localhost:5000
Content-Type: application/json
Content-Length: 85

Example payload for testing /scanFS

{
    "scan_type" : "fs",
    "target" : "mysql",
    "scan_target_type" : "ubuntu"
}
```

## Database Config Scan

**Function** : Checks the configuration of target database and returns identified values.

### Invoking on the command line

```
python3 database_scan.py --type TYPE --host HOST --port PORT
```

### Invoking as a method

```
from database_scan import scanner
scan_results = scanner(type, host, port)
```

### Invoking as a REST API

```
POST /scanDatabase HTTP/1.1
Host: localhost:5000
Content-Type: application/json
Content-Length: 123

Example payload for testing /scanDatabase

{
    "scan_type" : "database",
    "target" : "mysql",
    "scan_target_port" : "3306",
    "scan_target_type" : "mysql"
}
```

## Database Statement Scan

**Function** : Scans an input SQL statement to identify references to encryption and hashing methods.

### Invoking on the command line

```
python3 encrypt_search.py --statement STATEMENT
```

### Invoking as a method

```
from encrypt_search import find_references

scan_results = find_references(statement)
```

### Invoking as a REST API

```
POST /scanDatabase HTTP/1.1
Host: localhost:5000
Content-Type: application/json
Content-Length: 279

Example payload for testing /scanDatabase

{
    "scan_type" : "statement",
    "target" : "mysql",
    "scan_target_type" : "mysql",
    "scan_target_statement" : "sql_statement"
}
```

## Cloud Storage Scan

**Function** : Scans a target cloud storage account to check if it has encryption enabled and determine the key details.

### Invoking on the command line

```
python3 cloud_storage.py --target TARGET --owner OWNER --cloud-type CLOUD_TYPE
```

### Invoking as a method

```
from cloud_storage import get_scan_result
scan_results = get_scan_result(target, cloud_owner, cloud_type)
```

### Invoking as a REST API

```
POST /scanCloudStorage HTTP/1.1
Host: localhost:5000
Content-Type: application/json
Content-Length: 179

Example payload for testing /scanCloudStorage

{
    "scan_type": "cloud",
    "target": "s3bucket url",
    "scan_target_cloud_owner": "cloud_owner_key",
    "scan_target_type": "s3"
}
```

## Cloud Application Scanning

**Function** : Identifies deployed resources and validates the configuration of each resource

### Invoking on the command line

```
python3 cloud_app_scan.py --access-key-id ACCESS_KEY_ID --secret-access-key SECRET_ACCESS_KEY --cloud-type CLOUD_TYPE
```

### Invoking as a method

```
from cloud_app_scan import scan_cloud_app
scan_results = scan_cloud_app(acces_key_id, secret_access_key, cloud_type)
```

### Invoking as a REST API

```
POST /scanCloudApplication HTTP/1.1
Host: localhost:5000
Content-Type: application/json
Content-Length: 261

Example payload for testing /scanCloudApplication

{
    "scan_type": "cloudApplication",
    "target": "https://aws.amazon.com/",
    "scan_target_cloud_access_key_id": "acceskeyid",
    "scan_target_cloud_secret_access_key": "secret_access_key",
    "scan_target_type": "aws"
}
```

## Terraform Scan

**Function** : Scans terraform file and checks specified configuration against policies

### Invoking on the command line

```
python3 terraform_scan.py --file FILE
```

### Invoking as a method

```
from terraform_scan import get_scan_results
scan_results = get_scan_results(file)
```

### Invoking as a REST API

```
POST /scanTerraform HTTP/1.1
Host: localhost:5000
Content-Type: application/json
Content-Length: 1112

Example payload for testing /scanTerraform

{
    "scan_type":"terraform",
    "target":"none",
    "scan_target_statement":"provider \"aws\" {\n  region = \"us-west-2\"  # Replace with your desired AWS region\n}\n\nresource \"aws_s3_bucket\" \"example_bucket\" {\n  bucket = \"your-bucket-name\"  # Replace with your desired bucket name\n\n  versioning {\n    enabled = true\n  }\n}\n\nresource \"aws_redshift_cluster\" \"example_cluster\" {\n  cluster_identifier      = \"your-cluster-name\"  # Replace with your desired cluster name\n  node_type               = \"dc2.large\"\n  cluster_type            = \"single-node\"\n  master_username         = \"your-username\"  # Replace with your desired username\n  master_password         = \"your-password\"  # Replace with your desired password\n  publicly_accessible    = true\n  skip_final_snapshot     = true\n  encrypted               = false  # Setting encryption to false for an unencrypted cluster\n}\n\noutput \"s3_bucket_name\" {\n  value = aws_s3_bucket.example_bucket.id\n}\n\noutput \"redshift_cluster_id\" {\n  value = aws_redshift_cluster.example_cluster.id\n}",
    "scan_target_type":"aws"
}
```
