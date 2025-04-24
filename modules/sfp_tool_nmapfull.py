# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:         sfp_tool_nmapfull
# Purpose:      SpiderFoot plug-in for using Nmap to perform OS fingerprinting.
#
# Author:      Steve Micallef <steve@binarypool.com>
#
# Created:     03/05/2020
# Copyright:   (c) Steve Micallef 2020
# Licence:     MIT
# -------------------------------------------------------------------------------

import os.path
from subprocess import PIPE, Popen
from spiderfoot import SpiderFootEvent, SpiderFootPlugin

class sfp_tool_nmapfull(SpiderFootPlugin):

    meta = {
        'name': "Tool - Nmap Full",
        'summary': "Identify what Operating System might be used.",
        'flags': ["tool", "slow", "invasive"],
        'useCases': ["Footprint", "Investigate"],
        'categories': ["Crawling and Scanning"],
        'toolDetails': {
            'name': "Nmap",
            'description': "Nmap (\"Network Mapper\") is a free and open source utility for network discovery and security auditing.\n"
            "Nmap uses raw IP packets in novel ways to determine what hosts are available on the network, "
            "what services (application name and version) those hosts are offering, "
            "what operating systems (and OS versions) they are running, "
            "what type of packet filters/firewalls are in use, and dozens of other characteristics.\n",
            'website': "https://nmap.org/",
            'repository': "https://svn.nmap.org/nmap"
        },
    }

    # Default options
    opts = {
        'nmappath': "/usr/bin/nmap",
    }

    # Option descriptions
    optdescs = {
        'nmappath': "Path to the where the nmap binary lives. Must be set.",
    }

    results = None
    errorState = False

    def setup(self, sfc, userOpts=dict()):
        self.sf = sfc
        self.results = self.tempStorage()
        self.errorState = False
        self.__dataSource__ = "Target Network"

        for opt in list(userOpts.keys()):
            self.opts[opt] = userOpts[opt]

    # Quais eventos esse módulo escuta
    def watchedEvents(self):
        return ["IP_ADDRESS", "NETBLOCK_OWNER"]

    # Quais eventos ele gera
    def producedEvents(self):
        return ["RAW_RIR_DATA"]

    # Função principal do módulo
    def handleEvent(self, event):
        eventName = event.eventType
        eventData = event.data
        srcModuleName = event.module

        if self.errorState:
            return

        self.debug(f"Received event: {eventName} from {srcModuleName}")

        # Evita escanear duas vezes o mesmo IP
        if eventData in self.results:
            self.debug(f"Skipping {eventData}, already scanned.")
            return

        self.results[eventData] = True

        # Verifica se o caminho do Nmap foi definido corretamente
        exe = self.opts['nmappath']
        if not exe.endswith("nmap"):
            exe = os.path.join(self.opts['nmappath'], "nmap")

        # Verifica se o binário do Nmap existe
        if not os.path.isfile(exe):
            self.error(f"Nmap binary not found at {exe}")
            self.errorState = True
            return

        # Verifica se o input é válido
        if not self.sf.validIP(eventData) and not self.sf.validIpNetwork(eventData):
            self.error(f"Invalid input: {eventData}")
            return

        try:
            # Executa o Nmap
            p = Popen([exe, "-sV", eventData], stdout=PIPE, stderr=PIPE)
            stdout, stderr = p.communicate(input=None)

            # Trata erro na execução do Nmap
            if p.returncode != 0:
                self.error(f"Nmap execution failed. Error: {stderr.decode('utf-8', errors='replace')}")
                return

            # Converte saída do Nmap para string
            content = stdout.decode('utf-8', errors='replace').strip()

            if not content:
                self.debug(f"Nmap scan for {eventData} returned empty results.")
                return

            # Envia TODO o output do Nmap para o SpiderFoot como um único evento
            self.debug(f"Nmap scan result for {eventData}: {content}")

            evt = SpiderFootEvent("RAW_RIR_DATA", f"Nmap scan result:\n{content}", self.__name__, event)
            self.notifyListeners(evt)

        except Exception as e:
            self.error(f"Error running Nmap: {e}")
            return
