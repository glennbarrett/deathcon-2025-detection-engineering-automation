"""
attack.py

Scan local Markdown detection files to determine which MITRE ATT&CK techniques
are covered and update a layer.json file's technique scores accordingly.

Workflow:
 - Load an existing layer.json (expected to contain a "techniques" list with "techniqueID" keys).
 - Query the ATT&CK enterprise matrix via attackcti to obtain valid technique IDs.
 - Iterate over local .md files, extract a "Techniques" field from Markdown, and map
   each technique to files that reference it.
 - Increment the score for each technique in layer.json based on how many files
   reference that technique (including parent technique grouping by numeric prefix).
 - Overwrite the original layer.json with the updated scores.

Notes:
 - The script expects local Markdown files to include a "Techniques" section that
   lists technique IDs separated by commas (e.g., "T1003, T1020").
 - Parent techniques are derived by splitting on '.' and using the left-hand segment
   (this supports sub-techniques like "T1059.001").
"""
from attackcti import attack_client
import os
import json
import mistune
from bs4 import BeautifulSoup

# Path to an existing ATT&CK layer JSON file to be updated
layer_file = "./layer.json"
with open(layer_file, "r") as f:
    layer_data = json.load(f)

# Directory to scan for markdown files (encoded for os.listdir usage)
current_directory = os.fsencode("./")

# Instantiate the ATT&CK CTI client and query the enterprise ATT&CK dataset
lift = attack_client()
attack_enterprise = lift.get_enterprise()

def extract_technique(file):
    """
    Read a Markdown file and extract the text following the literal "Techniques"
    label in the rendered HTML.

    Returns an empty string if the "Techniques" label is not present.

    Expectation: The Techniques line contains comma-separated technique IDs.
    """
    with open(file, "r", encoding="UTF-8") as f:
        body = f.read()

    # Render markdown to HTML so we can reliably find the "Techniques" label
    parsed_markdown = mistune.markdown(body)
    soup = BeautifulSoup(parsed_markdown, "html.parser")
    query_header = soup.find_all(string="Techniques")
    if query_header:
        # The technique text is expected to be the next element after the header
        query_string = query_header[0].next_element.next_element.string
    else:
        # No Techniques section found
        query_string = ""

    return query_string

# Build a dictionary keyed by technique ID initialized with empty lists of files
covered_techniques = {}
technique_ids = []
for technique in attack_enterprise["techniques"]:
    # Each technique entry should contain an external_references list with the ATT&CK ID
    technique_ids.append(technique["external_references"][0]["external_id"])

for id in technique_ids:
    covered_techniques[id] = []

# Iterate over files in the current directory and process .md files
for file in os.listdir(current_directory):
    file_name = os.fsdecode(file)
    if file_name.endswith(".md"):
        parent_techs = set()
        # Extract comma-separated technique IDs from the file (empty string if none)
        current_techs = extract_technique(file_name).split(",")
        for technique in current_techs:
            technique = technique.strip()
            if not technique:
                continue
            # Record that this markdown file references the technique
            covered_techniques[technique].append(file_name)
            # If the technique is a sub-technique like T1059.001, also count the parent T1059
            if "." in technique:
                parent_techs.add(technique.split(".")[0])
        # Add the file to parent technique entries as well
        for parent in parent_techs:
            covered_techniques[parent].append(file_name)
    else:
        # Skip non-markdown files
        continue

# Update the layer_data technique scores based on how many files reference each technique
for covered_technique, files in covered_techniques.items():
    for data_techniques in layer_data["techniques"]:
        if data_techniques["techniqueID"] == covered_technique:
            # Score is the count of markdown files that reference the technique
            data_techniques["score"] = len(files)

# Overwrite the original layer.json with updated scores
os.remove(layer_file)
with open(layer_file, 'w') as f:
    json.dump(layer_data, f, indent=4)