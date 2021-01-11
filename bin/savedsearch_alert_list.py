import sys
import os
import json
import logging
import logging.handlers
from pathlib import Path
from urllib.parse import unquote
from time import sleep

# Invoke splunklib from '../lib' into python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

import splunklib.client as SPLUNK_CLIENT

def setup_logger(level=logging.INFO):
	logger = logging.getLogger("splunk_savedsearch_alert_logger")
	logger.propagate = False
	logger.setLevel(level)
	logfile = Path(os.environ['SPLUNK_HOME'] + '/var/log/splunk/splunk_savedsearch_alert_list.log')
	file_handler = logging.handlers.RotatingFileHandler(logfile)
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	file_handler.setFormatter(formatter)
	logger.addHandler(file_handler)
	return logger

def main(data, logger=None):
	session_key = data.get('session_key')
	config = data.get('configuration')
	
	seperator = config.get('seperator')
	exec_mode = config.get('exec_mode')
	savedsearches_string = config.get('savedsearches')
	
	splunk_service = SPLUNK_CLIENT.connect(token=session_key)
	
	# Could also be done using the actual seperator character as the <option> value ¯\_(ツ)_/¯
	# Might raise Keyerror... catched in line 77
	if seperator == "comma":
		savedsearches = [splunk_service.saved_searches[ssn] for ssn in savedsearches_string.split(',')]
	elif seperator == "newline":
		savedsearches = [splunk_service.saved_searches[ssn] for ssn in savedsearches_string.split('\n')]
	else:
		raise KeyError(f"Undefined seperator: '{seperator}'. Choose between 'comma' or 'newline'.")
	
	jobs = {}
	
	for savedsearch in savedsearches:
		job = savedsearch.dispatch()
		jobs[savedsearch.name] = job.name
		
		if exec_mode == "normal":
			continue
		elif exec_mode == "blocking":
			# This seems to be the proposed solution by splunk! (https://dev.splunk.com/enterprise/docs/devtools/python/sdk-python/howtousesplunkpython/howtorunsearchespython#To-create-a-normal-search-poll-for-completion-and-display-results) :o
			while not job.is_done():
				if job.is_ready():
					stats = {"isDone": job["isDone"],
						"doneProgress": float(job["doneProgress"])*100, 
						"scanCount": int(job["scanCount"]),
						"eventCount": int(job["eventCount"]),
						"resultCount": int(job["resultCount"])}
					logger.info(f"Job Status ({savedsearch.name}, {job.name}): {stats!s}")
				sleep(2)
		else:
			raise KeyError(f"Undefined Exec-Mode: '{exec_mode}'. Choose between 'normal' or 'blocking'.")
		
	logger.info(f"Dispatch saved searches: {jobs!s}")
	
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
		logger.error(f"Unsupported execution mode: {sys.argv[1]} (expected --execute flag)")
	sys.exit(1)
