import json
import yaml

# filepath: c:\Users\kimda\Documents\tag_crawler\all_projects_versions_stable.jsonl
STABLE_JSONL = "all_projects_versions_stable.jsonl"
# filepath: c:\Users\kimda\Documents\tag_crawler\temp.yaml
TEMP_YAML = "temp.yaml"
# 출력 파일
OUTPUT_YAML = "dale_projects3.yaml"

def load_project_urls(temp_yaml):
    with open(temp_yaml, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    # {project_name: url_template} 형태로 변환
    return {p["name"]: p["url"] for p in data["projects"]}

def load_versions(jsonl_file):
    projects = {}
    with open(jsonl_file, encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            name = obj["project"]
            version = obj["version"]
            projects.setdefault(name, []).append(version)
    return projects

def make_yaml(project_urls, project_versions):
    result = {"projects": []}
    for name, versions in project_versions.items():
        url_template = project_urls.get(name)
        if not url_template:
            continue
        for version in versions:
            url = url_template.replace("*", version)
            result["projects"].append({
                "name": name,
                "version": version,
                "url": url
            })
    return result

def main():
    project_urls = load_project_urls(TEMP_YAML)
    project_versions = load_versions(STABLE_JSONL)
    result_yaml = make_yaml(project_urls, project_versions)
    with open(OUTPUT_YAML, "w", encoding="utf-8") as f:
        yaml.dump(result_yaml, f, allow_unicode=True, sort_keys=False)

if __name__ == "__main__":
    main()