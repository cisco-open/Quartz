# MIT License

# Copyright (c) 2024 Cisco Systems, Inc. and its affiliates

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import sslscan
from sslscan.module.scan import BaseScan

def checkPQSafety(server):

    sslscan.modules.load_global_modules()
    sslscan.logger.setLevel(40)

    scanner = sslscan.Scanner()

    for name in ["ssl2", "ssl3", "tls10", "tls11", "tls12"]:
        scanner.config.set_value(name, True)

    scanner.append_load('server.ciphers', '', base_class=BaseScan)
    module = scanner.load_handler_from_uri(server)
    scanner.set_handler(module)
    scanner.run()

    ciphers = scanner.get_knowledge_base().get('server.ciphers')
    if ciphers is None:
        return []
    cipher_suite = []
    for cipher in ciphers:
        if cipher.status_name == 'accepted':
            cipher_suite.append(cipher.cipher_suite.name)
    return cipher_suite
