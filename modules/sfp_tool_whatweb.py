# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:         sfp_tool_whatweb
# Purpose:      SpiderFoot plug-in for using WhatWeb to identify web technologies.
#
# Author:       SpiderFoot Community
#
# Created:      28/02/2025
# Licence:      MIT
# -------------------------------------------------------------------------------

import json
import os.path
from subprocess import PIPE, Popen, TimeoutExpired
from spiderfoot import SpiderFootEvent, SpiderFootPlugin, SpiderFootHelpers

class sfp_tool_whatweb(SpiderFootPlugin):

    meta = {
        'name': "Tool - WhatWeb",
        'summary': "Identify technologies used on a target website.",
        'flags': ["tool"],
        'useCases': ["Footprint", "Investigate"],
        'categories': ["Content Analysis"],
        'toolDetails': {
            'name': "WhatWeb",
            'description': "WhatWeb identifies websites and their technologies, including CMS, web servers, JavaScript libraries, "
            "and more. It has over 1800 plugins for detection.",
            'website': 'https://github.com/urbanadventurer/whatweb',
            'repository': 'https://github.com/urbanadventurer/whatweb'
        },
    }

    opts = {
        'aggression': 1,
        'ruby_path': 'ruby',
        'whatweb_path': '/opt/whatweb/whatweb'
    }

    optdescs = {
        'aggression': 'Set WhatWeb aggression level (1-4)',
        'ruby_path': "Path to Ruby interpreter to use for WhatWeb. If just 'ruby' then it must be in your $PATH.",
        'whatweb_path': "Path to the whatweb executable file. Must be set."
    }

    results = None
    errorState = False

    def setup(self, sfc, userOpts=dict()):
        self.sf = sfc
        self.results = self.tempStorage()
        self.errorState = False
        self.__dataSource__ = "Target Website"

        for opt in list(userOpts.keys()):
            self.opts[opt] = userOpts[opt]

    def watchedEvents(self):
        return ['INTERNET_NAME', 'DOMAIN_NAME']

    def producedEvents(self):
        return ['RAW_RIR_DATA']

    def handleEvent(self, event):
        eventName = event.eventType
        eventData = event.data
        srcModuleName = event.module

        self.debug(f"Received event: {eventName} from {srcModuleName}")

        if self.errorState:
            return

        if eventData in self.results:
            self.debug(f"Skipping {eventData}, already scanned.")
            return

        self.results[eventData] = True

        if not self.opts['whatweb_path']:
            self.error("You enabled sfp_tool_whatweb but did not set a path to the tool!")
            self.errorState = True
            return

        exe = self.opts['whatweb_path']
        if self.opts['whatweb_path'].endswith('/'):
            exe = exe + 'whatweb'

        # Verifica se o binário existe
        if not os.path.isfile(exe):
            self.error(f"WhatWeb binary not found at {exe}")
            self.errorState = True
            return

        # Sanitiza o input
        if not SpiderFootHelpers.sanitiseInput(eventData):
            self.error("Invalid input, refusing to run.")
            return

        # Define o nível de agressividade
        try:
            aggression = int(self.opts['aggression'])
            if aggression > 4:
                aggression = 4
            if aggression < 1:
                aggression = 1
        except Exception:
            aggression = 1

        # Comando para rodar o WhatWeb
        args = [
            self.opts['ruby_path'],
            exe,
            "--quiet",
            f"--aggression={aggression}",
            "--log-json=-",
            "--user-agent=Mozilla/5.0",
            "--follow-redirect=never",
            eventData
        ]

        try:
            self.debug(f"Running WhatWeb: {' '.join(args)}")

            p = Popen(args, stdout=PIPE, stderr=PIPE)
            stdout, stderr = p.communicate()

            if p.returncode != 0:
                self.error(f"WhatWeb execution failed. Error: {stderr.decode('utf-8', errors='replace')}")
                return

            content = stdout.decode('utf-8', errors='replace').strip()

            if not content:
                self.debug(f"WhatWeb scan for {eventData} returned empty results.")
                return

            # Log do resultado completo
            self.debug(f"WhatWeb scan result for {eventData}: {content}")

            # Envia TODO o output do WhatWeb como um único evento no SpiderFoot
            evt = SpiderFootEvent("RAW_RIR_DATA", f"WhatWeb scan result:\n{content}", self.__name__, event)
            self.notifyListeners(evt)

        except TimeoutExpired:
            p.kill()
            stdout, stderr = p.communicate()
            self.error(f"Timeout running WhatWeb on {eventData}")
            return
        except Exception as e:
            self.error(f"Error running WhatWeb: {e}")
            return
