from datetime import datetime
import json
import logging
import os
import re
import requests


def get_sorted_versions():
    # "https://your-harbor-domain/api/v2.0/projects/{project_name_or_id}/repositories/{repository_name}/artifacts"

    url = "https://" + os.environ.get("HARBOR_URL") + "/api/v2.0/projects/" + \
        os.environ.get("PROJECT") + "/repositories/" + os.environ.get("REPO") + "/artifacts/"
    credentials = (os.getenv("HARBOR_IMAGE_USERNAME"), os.getenv("HARBOR_ROBOT_PASSWORD"))

    try:
        result = requests.get(url, auth=credentials)
    except Exception as inst:
        logging.error("Failed to load data from hub." + repr(inst))
        exit(1)


    sorted_images = sorted(json.loads(result.text), key=get_push_time, reverse=True) 
    for im in sorted_images:
        for tag in im["tags"]:
            logging.info(tag["push_time"] + "    " + tag["name"])

    return sorted_images


def get_push_time(obj):
    push_time_str = obj["tags"][0]["push_time"]
    return datetime.fromisoformat(push_time_str.replace('Z', '+00:00'))


def get_new_tag_from_old(versions):
    first_match = None

    for version in versions:
        for tag in version["tags"]:
            match = re.search(r'(\d+)\.(\d+)\.(\d+)', tag["name"])
            if not first_match:
                first_match = match

    if not first_match:
        return "0.1.0"
    
    major = int(first_match.group(1))
    minor = int(first_match.group(2))
    patch = int(first_match.group(3))

    if int(os.getenv("MAJOR")) == major + 1:
        major += 1
        minor = 0
        patch = 0
    elif int(os.getenv("MINOR")) == minor + 1:
        minor += 1
        patch = 0
    else:
        patch += 1

    return ".".join([str(major), str(minor), str(patch)])
    

def main():
    logging.basicConfig(level=logging.DEBUG)
    tags = get_sorted_versions()
    with open("vars.env", "w") as file:
        file.write(os.getenv("REPO_ENV_VAR") + '=' + get_new_tag_from_old(tags))

if __name__ == "__main__":
    main()
