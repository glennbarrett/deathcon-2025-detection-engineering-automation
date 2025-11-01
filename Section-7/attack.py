from attackcti import attack_client
import os
import json
import mistune
from bs4 import BeautifulSoup

layer_file = "./layer.json"
with open(layer_file, "r") as f:
    layer_data = json.load(f)

current_directory = os.fsencode("./")

lift = attack_client()
attack_enterprise = lift.get_enterprise()

def extract_technique(file):
    with open(file, "r", encoding="UTF-8") as f:
        body = f.read()

    parsed_markdown = mistune.markdown(body)
    soup = BeautifulSoup(parsed_markdown, "html.parser")
    query_header = soup.find_all(string="Techniques")
    if query_header:
        query_string = query_header[0].next_element.next_element.string
    else:
        query_string = ""

    return query_string

covered_techniques = {}
technique_ids = []
for technique in attack_enterprise["techniques"]:
    technique_ids.append(technique["external_references"][0]["external_id"])

for id in technique_ids:
    covered_techniques[id] = []

for file in os.listdir(current_directory):
    file_name = os.fsdecode(file)
    if file_name.endswith(".md"):
        parent_techs = set()
        current_techs = extract_technique(file_name).split(",")
        for technique in current_techs:
            technique = technique.strip()
            if not technique: continue
            covered_techniques[technique].append(file_name)
            if "." in technique:
                parent_techs.add(technique.split(".")[0])
        for parent in parent_techs:
            covered_techniques[parent].append(file_name)
    else:
        continue

for covered_technique, files in covered_techniques.items():
    for data_techniques in layer_data["techniques"]:
        if data_techniques["techniqueID"] == covered_technique:
            data_techniques["score"] = len(files)

os.remove(layer_file)
with open(layer_file, 'w') as f:
    json.dump(layer_data, f, indent=4)