import os
import sys
import time
import mistune
import requests
from bs4 import BeautifulSoup
import subprocess
from splunklib import client

TOKEN = os.environ["SPLUNK_API"]
service = client.connect(
    host="localhost", port=8089, username="admin", splunkToken=TOKEN, app="search"
)

def get_updates():
    updated_entries = subprocess.check_output(f"git diff-tree --no-commit-id --name-only -r {os.environ['BUILD_SOURCE_VERSION']}", shell=True, text=True)
    return updated_entries.split("\n")

def extract_test(file):
    with open(file, "r", encoding="UTF-8") as f:
        body = f.read()

    parsed_markdown = mistune.markdown(body)
    soup = BeautifulSoup(parsed_markdown, "html.parser")
    query_header = soup.find_all(string="Test Case")
    query_string = query_header[0].next_element.next_element.string

    return "{" + query_string.rstrip() + "}"

def set_params():
    search_params = {
    "alert_comparator": "greater than",
    "alert_threshold": "0",
    "alert_type": "number of events",
    "cron_schedule": "*/1 * * * *",
    "description": "Documented in Azure DevOps wiki",
    "dispatch.earliest_time": "-1h",
    "dispatch.latest_time": "now",
    "is_scheduled": "1",
    "alert.track": "1",
}

    return search_params

def build_query(file):
    with open(file, "r", encoding="UTF-8") as f:
        body = f.read()

    parsed_markdown = mistune.markdown(body)
    soup = BeautifulSoup(parsed_markdown, "html.parser")
    query_header = soup.find_all(string="Query")
    query_string = query_header[0].next_element.next_element.string

    return query_string

def create_alert(title, query, params):
    service.saved_searches.create(title, query, **params)
    
def run_test(command):
    subprocess.call(f'C:\\Windows\\SysWOW64\\WindowsPowerShell\\v1.0\\powershell.exe Invoke-Command {command}', shell=True)

def process_updates(entry_list):
    validate_list = []
    for entry in entry_list:
        print(entry + "\n")
        if entry.endswith(".md") and entry != "README.md":
            if not os.path.exists(entry): continue
            title = os.path.basename(entry).rsplit(".", 1)[0]
            test = extract_test(entry)
            query = build_query(entry)
            params = set_params()
            create_alert(title, query, params)
            run_test(test)
            validate_list.append(title)
    return validate_list

def validate_alerts(validate_list):
    print(f"validate list is {validate_list}")
    failed_alerts = []
    live_alerts = []
    triggered_alerts = service.fired_alerts.list()
    for alert in triggered_alerts: live_alerts.append(alert.name)
    for alert in validate_list:
        print(f"working on alert {alert}")
        if alert not in live_alerts:
            print(f"We had a failure with {alert}")
            failed_alerts.append(alert)
    
    if failed_alerts:
        return failed_alerts
    else:
        print("ALL DETECTIONS SUCCESSFULLY VALIDATED")

def fail_pipeline(failed_alerts):
    fail_block = " ".join(failed_alerts)
    raise SystemExit(f"ALERTS DID NOT PASS VALIDATION \n {fail_block}")


if __name__ == "__main__":
    entry_list = get_updates()
    validate_list = process_updates(entry_list)
    failed_alerts = []
    if validate_list:
        time.sleep(60)
        failed_alerts = validate_alerts(validate_list)
    if failed_alerts:
        fail_pipeline(failed_alerts)



