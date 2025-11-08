"""
extract_test_case.py

Utility to extract a "Test Case" section from a Markdown file and return it
formatted as a JSON-like string. When run as a script it prints the extracted
test case and then attempts to invoke a Windows PowerShell command using the
extracted string.

Notes:
- The script expects the Markdown to contain a header or label "Test Case"
  followed by the test case content.
- The subprocess invocation at the bottom is Windows-specific and may be unsafe
  if the extracted content is not trusted (command injection risk).
"""

import os
import sys
import subprocess
import mistune
import requests
from bs4 import BeautifulSoup
from splunklib import client

def extract_test(file):
    """
    Read a markdown file and extract the text that follows the first
    occurrence of the literal string "Test Case".

    Steps:
      1. Read the file contents as UTF-8.
      2. Convert Markdown to HTML using mistune so structure can be parsed.
      3. Parse the HTML with BeautifulSoup and find the first text node equal
         to "Test Case".
      4. Return the next element's string wrapped in braces.

    Returns:
      A string containing the extracted test case wrapped in curly braces,
      e.g. "{...extracted text...}".

    Raises:
      IndexError if "Test Case" is not present or the document structure is
      not as expected.
    """
    with open(file, "r", encoding="UTF-8") as f:
        body = f.read()

    # Convert markdown to HTML for reliable structural navigation
    parsed_markdown = mistune.markdown(body)
    soup = BeautifulSoup(parsed_markdown, "html.parser")

    # Find the element that contains the literal string "Test Case"
    query_header = soup.find_all(string="Test Case")
    # Expect the test case text to be in the element following the header
    query_string = query_header[0].next_element.next_element.string

    # Normalize trailing whitespace and wrap in braces so it doesn't conflict with the braces in Invoke-Command later on
    return "{" + query_string.rstrip() + "}"

if __name__ == "__main__":
    # Expect a single CLI argument: path to the markdown file
    file = sys.argv[1]
    # Print the extracted test case to stdout
    print(extract_test(file))
    # Prepare command to run: this uses PowerShell Invoke-Command and is Windows-only.
    # WARNING: Using extracted content directly in a shell is potentially unsafe and
    # can lead to command injection if the Markdown is untrusted.
    command_to_run = extract_test(file)
    subprocess.call(f'C:\\Windows\\SysWOW64\\WindowsPowerShell\\v1.0\\powershell.exe Invoke-Command {command_to_run}', shell=True)