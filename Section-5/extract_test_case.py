import os
import sys
import subprocess
import mistune
import requests
from bs4 import BeautifulSoup
from splunklib import client

def extract_test(file):
    with open(file, "r", encoding="UTF-8") as f:
        body = f.read()

    parsed_markdown = mistune.markdown(body)
    soup = BeautifulSoup(parsed_markdown, "html.parser")
    query_header = soup.find_all(string="Test Case")
    query_string = query_header[0].next_element.next_element.string

    return "{" + query_string.rstrip() + "}"

if __name__ == "__main__":
    file = sys.argv[1]
    print(extract_test(file))
    command_to_run = extract_test(file)
    subprocess.call(f'C:\\Windows\\SysWOW64\\WindowsPowerShell\\v1.0\\powershell.exe Invoke-Command {command_to_run}', shell=True)