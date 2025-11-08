"""
process_updates.py

CI helper that:
 - reads the commit changed files (from BUILD_SOURCE_VERSION)
 - parses Markdown files for "Query" and "Test Case" sections
 - creates scheduled Splunk saved searches for updated detection docs
 - invokes a Windows PowerShell test command for each test case
 - validates that alerts fired in Splunk and fails the pipeline on errors

Notes / warnings:
 - This script expects BUILD_SOURCE_VERSION and SPLUNK_API to be set in the environment.
 - It connects to a local Splunk management port (localhost:8089) using splunklib.
 - Running extracted content in a shell (PowerShell Invoke-Command) is potentially
   unsafe if the Markdown content is untrusted (risk of command injection).
 - The PowerShell invocation is Windows-specific; the pipeline must run on a Windows agent
   for run_test() to succeed.
"""
import os
import sys
import time
import mistune
import requests
from bs4 import BeautifulSoup
import subprocess
from splunklib import client

# Read Splunk API token from environment (set in pipeline variables/CI environment)
TOKEN = os.environ["SPLUNK_API"]

# Connect to Splunk management port using splunklib.client.
# Assumes local Splunk at localhost:8089 and admin credentials; adjust for production use.
service = client.connect(
    host="localhost", port=8089, username="admin", splunkToken=TOKEN, app="search"
)

def get_updates():
    """
    Return a list of files changed in the commit referenced by BUILD_SOURCE_VERSION.

    Uses git diff-tree to list file paths for the single commit SHA provided by the
    BUILD_SOURCE_VERSION environment variable (Azure Pipelines provides this).
    The output is split on newlines to return a Python list.

    Returns:
      list of file paths (strings). May include empty string at the end due to trailing newline.
    """
    updated_entries = subprocess.check_output(f"git diff-tree --no-commit-id --name-only -r {os.environ['BUILD_SOURCE_VERSION']}", shell=True, text=True)
    return updated_entries.split("\n")

def extract_test(file):
    """
    Extract the "Test Case" section from a Markdown file.

    Steps:
      - Read the Markdown file (UTF-8).
      - Render to HTML with mistune so structure can be parsed reliably.
      - Use BeautifulSoup to find the first text node equal to "Test Case".
      - Return the following element's string wrapped in braces.

    Returns:
      A string like "{...test case text...}".

    Raises:
      IndexError if "Test Case" is not found or the expected structure is missing.
    """
    with open(file, "r", encoding="UTF-8") as f:
        body = f.read()

    parsed_markdown = mistune.markdown(body)
    soup = BeautifulSoup(parsed_markdown, "html.parser")
    query_header = soup.find_all(string="Test Case")
    query_string = query_header[0].next_element.next_element.string

    # Trim trailing whitespace and wrap in braces to form a JSON-like payload for testing
    return "{" + query_string.rstrip() + "}"

def set_params():
    """
    Return a dictionary of saved search / alert parameters for Splunk.

    These parameters configure scheduling, alert thresholds, and dispatch window.
    Modify values here to change how created alerts behave.
    """
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
    """
    Extract the "Query" section from a Markdown file.

    Same approach as extract_test(): render to HTML and use BeautifulSoup to
    locate the "Query" label and return the following element's string.
    """
    with open(file, "r", encoding="UTF-8") as f:
        body = f.read()

    parsed_markdown = mistune.markdown(body)
    soup = BeautifulSoup(parsed_markdown, "html.parser")
    query_header = soup.find_all(string="Query")
    query_string = query_header[0].next_element.next_element.string

    return query_string

def create_alert(title, query, params):
    """
    Create a Splunk saved search (alert) in the connected Splunk service.

    title: saved search name
    query: search string executed by the saved search
    params: dict of saved search attributes (from set_params)
    """
    service.saved_searches.create(title, query, **params)
    
def run_test(command):
    """
    Invoke a Windows PowerShell command to exercise the test case.

    The command parameter is expected to be a string previously wrapped in braces
    by extract_test(). This function calls PowerShell's Invoke-Command.

    WARNING: Running arbitrary extracted content in a shell is dangerous if the
    Markdown is not trusted. This is Windows-only and will fail on non-Windows agents.
    """
    subprocess.call(f'C:\\Windows\\SysWOW64\\WindowsPowerShell\\v1.0\\powershell.exe Invoke-Command {command}', shell=True)

def process_updates(entry_list):
    """
    Process a list of changed files:
      - For each Markdown file (excluding README.md), extract its Query and Test Case.
      - Create a Splunk saved search for the Query and run the Test Case command.
      - Collect titles of created alerts for subsequent validation.

    Returns:
      validate_list: list of saved-search titles that were created and need validation.
    """
    validate_list = []
    for entry in entry_list:
        print(entry + "\n")
        # Only consider markdown files (skip README.md)
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
    """
    Check Splunk fired alerts and confirm that each expected alert is present.

    Returns:
      failed_alerts: list of alert titles that were not observed; or None if all validated.
    """
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
    """
    Fail the pipeline by raising SystemExit with a summary of failed alerts.
    """
    fail_block = " ".join(failed_alerts)
    raise SystemExit(f"ALERTS DID NOT PASS VALIDATION \n {fail_block}")


if __name__ == "__main__":
    # Entry point used by the pipeline:
    # 1) Get the changed files from the commit SHA
    # 2) Create alerts and run tests for changed detection docs
    # 3) Wait briefly and validate that alerts fired in Splunk
    entry_list = get_updates()
    validate_list = process_updates(entry_list)
    failed_alerts = []
    if validate_list:
        # Give Splunk a short window to evaluate scheduled searches and fire alerts
        time.sleep(60)
        failed_alerts = validate_alerts(validate_list)
    if failed_alerts:
        fail_pipeline(failed_alerts)



