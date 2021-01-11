import sys
import os
import json
import logging
import logging.handlers
from pathlib import Path
from urllib.parse import unquote

# Invoke splunklib from '../lib' into python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

import splunklib.client as SPLUNK_CLIENT

def setup_logger(level=logging.INFO):
	logger = logging.getLogger("splunk_savedsearch_alert_logger")
	logger.propagate = False
	logger.setLevel(level)
	if 'SPLUNK_HOME' in os.environ:
		logfile = Path(os.environ['SPLUNK_HOME'] + '/var/log/splunk/splunk_savedsearch_alert.log')
	else:
		raise KeyError("Environment Variable: 'SPLUNK_HOME' is not set, but required!")
	file_handler = logging.handlers.RotatingFileHandler(logfile)
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	file_handler.setFormatter(formatter)
	logger.addHandler(file_handler)
	return logger

def main(data, logger=None):
	session_key = data.get('session_key')
	config = data.get('configuration')
	savedsearch_url = unquote(config.get('savedsearch'))
	savedsearch_uri = f"/{savedsearch_url.split('/', 3)[-1]}"  # prepend '/'
	
	splunk_service = SPLUNK_CLIENT.connect(token=session_key)
	savedsearch = SPLUNK_CLIENT.SavedSearch(splunk_service, savedsearch_uri)
	job = savedsearch.dispatch()
	logger.info(f"Dispatch saved search: {savedsearch.name}. Job ID:{job.name}")
	
	return 0
	
if __name__ == '__main__':
	logger = setup_logger()
	if len(sys.argv) > 1 and sys.argv[1] == '--execute':
		try:
			payload = json.loads(sys.stdin.read())
			sys.exit(main(payload, logger=logger))
		except Exception as exc:
			logger.error(str(exc))
	else:
		logger.error("Unsupported execution mode (expected --execute flag)")
	sys.exit(1)
