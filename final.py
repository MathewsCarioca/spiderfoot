import subprocess

# Comando original com a adição do WhatWeb
command = """
/opt/venv/bin/python -c 'from spiderfoot import SpiderFootDb; \
db = SpiderFootDb({"__database": "/var/lib/spiderfoot/spiderfoot.db"}); \
db.configSet({"sfp_tool_nmap:nmappath": "/usr/bin/nmap", \
              "sfp_tool_whatweb:whatweb_path": "/opt/whatweb/whatweb"})' || true && \
/opt/venv/bin/python ./sf.py -l 0.0.0.0:5001
"""

# Executando o comando no shell para manter o comportamento original
subprocess.run(command, shell=True, executable="/bin/sh")
