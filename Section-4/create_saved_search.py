import os
import sys

import mistune
import requests
from bs4 import BeautifulSoup
from splunklib import client

TOKEN = "eyJraWQiOiJzcGx1bmsuc2VjcmV0IiwiYWxnIjoiSFM1MTIiLCJ2ZXIiOiJ2MiIsInR0eXAiOiJzdGF0aWMifQ.eyJpc3MiOiJhZG1pbiBmcm9tIERFU0tUT1AtVEpLMktSSCIsInN1YiI6ImFkbWluIiwiYXVkIjoidGVzdGluZyIsImlkcCI6IlNwbHVuayIsImp0aSI6Ijc2MTIwNGRiMTIwYjdiMjQwY2MzMWQ4ZjliNjY3NjgyOWIyODU2ZTlhNjAwMzUwZTY4N2EwZjY3M2JkZWU5ODgiLCJpYXQiOjE3MTk3MDA4NzUsImV4cCI6MTcxOTc4NzI3NSwibmJyIjoxNzE5NzAwODc1fQ.eXhTTIEM4yddrCVs5CcK5ngjHDkC6tvla1N2FtK3JdB519l4lELQc9Yagltr2-2BfTtnrk-u-V-INX7ZMeLTHw"


def set_params():
    """
    Return a dictionary of parameters used when creating the saved search.

    These parameters map to Splunk saved search attributes:
      - cron_schedule: when the scheduled search runs
      - description: human-readable description
      - dispatch.earliest_time / latest_time: relative time window for the search
      - is_scheduled: "1" to mark the search as scheduled

    Modify these values to change scheduling or dispatch behavior.
    """

    search_params = {
    "cron_schedule": "30 * * * *", # run at minute 30 every hour
    "description": "Documented in Azure DevOps wiki",
    "dispatch.earliest_time": "-1h", # search from 1 hour ago
    "dispatch.latest_time": "now",
    "is_scheduled": "1",
}

    return search_params


def build_query(file):
    """
    Read a markdown file, parse it to HTML, and extract the Query section.

    The function:
      1. Reads the markdown file.
      2. Converts markdown to HTML using mistune.
      3. Parses HTML with BeautifulSoup.
      4. Finds the first text node equal to "Query" and returns the next element's string.

    Assumes the markdown contains a header or label "Query" followed by the query text.
    Raises IndexError if the expected structure is not found.
    """

    with open(file, "r", encoding="UTF-8") as f:
        body = f.read()

    # Convert markdown to HTML so we can reliably navigate structure with BeautifulSoup
    parsed_markdown = mistune.markdown(body)
    soup = BeautifulSoup(parsed_markdown, "html.parser")
    # Find the element that contains the literal string "Query"
    query_header = soup.find_all(string="Query")
    # The query text is expected to be the next element after the header
    query_string = query_header[0].next_element.next_element.string

    return query_string


if __name__ == "__main__":
    # Expect a single argument: path to the markdown file containing the Query
    file = sys.argv[1]
    # Use the filename (without extension) as the saved search title
    title = os.path.basename(file).rsplit(".", 1)[0]
    # Extract query text from the markdown file
    query = build_query(file)
    # Prepare saved search parameters
    params = set_params()
    # Connect to the local Splunk management port using splunklib
    # Note: username and host/port are hardcoded here for local Splunk instance
    service = client.connect(
        host="localhost", port=8089, username="admin", splunkToken=TOKEN, app="search"
    )

    # Create the saved search in the search app
    service.saved_searches.create(title, query, **params)
