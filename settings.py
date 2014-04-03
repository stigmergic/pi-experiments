import json
import os
import sys

import logging
log = logging.getLogger(__name__)
out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
out_hdlr.setLevel(logging.INFO)
log.addHandler(out_hdlr)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

try:
    settings = json.load(open(os.path.join(BASE_DIR, 'settings.json')))
except:
    log.error('failed to load settings.json')
    settings = {}

print settings

LOG_TEMPERATURE = True
