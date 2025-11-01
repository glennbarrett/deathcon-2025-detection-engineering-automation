import os
import sys

import mistune
import requests
from bs4 import BeautifulSoup
from splunklib import client

TOKEN = "eyJraWQiOiJzcGx1bmsuc2VjcmV0IiwiYWxnIjoiSFM1MTIiLCJ2ZXIiOiJ2MiIsInR0eXAiOiJzdGF0aWMifQ.eyJpc3MiOiJhZG1pbiBmcm9tIERFU0tUT1AtVEpLMktSSCIsInN1YiI6ImFkbWluIiwiYXVkIjoidGVzdGluZyIsImlkcCI6IlNwbHVuayIsImp0aSI6Ijc2MTIwNGRiMTIwYjdiMjQwY2MzMWQ4ZjliNjY3NjgyOWIyODU2ZTlhNjAwMzUwZTY4N2EwZjY3M2JkZWU5ODgiLCJpYXQiOjE3MTk3MDA4NzUsImV4cCI6MTcxOTc4NzI3NSwibmJyIjoxNzE5NzAwODc1fQ.eXhTTIEM4yddrCVs5CcK5ngjHDkC6tvla1N2FtK3JdB519l4lELQc9Yagltr2-2BfTtnrk-u-V-INX7ZMeLTHw"


def set_params():
    search_params = {
    "cron_schedule": "30 * * * *",
    "description": "Documented in Azure DevOps wiki",
    "dispatch.earliest_time": "-1h",
    "dispatch.latest_time": "now",
    "is_scheduled": "1",
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


if __name__ == "__main__":
    file = sys.argv[1]
    title = os.path.basename(file).rsplit(".", 1)[0]
    query = build_query(file)
    params = set_params()
    service = client.connect(
        host="localhost", port=8089, username="admin", splunkToken=TOKEN, app="search"
    )

    service.saved_searches.create(title, query, **params)
