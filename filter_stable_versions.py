import json
import re

def is_stable_version(version):
    exclude_keywords = [
        "rc", "beta", "alpha", "nightly", "dev", "test", "preview", "pre", "draft",
        "master", "signed", "bp", "before", "after", "LEVITTE", "COMPAQ_PATCH",
        "engine", "FIPS", "SSLeay", "ChangeLog", "CVE", "GNUMERIC", "GNOME", "EAZEL", "STATE"
    ]
    version_lower = version.lower()
    for kw in exclude_keywords:
        if kw.lower() in version_lower:
            return False
    # 정식 버전 패턴: 숫자가 포함된 태그 허용 (예: tcpdump-4.99.5)
    if re.match(r".*\d+([.\-_]\d+)*([a-z]?)$", version_lower):
        return True
    return False

def filter_stable_versions(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as fin, open(output_file, "w", encoding="utf-8") as fout:
        for line in fin:
            try:
                obj = json.loads(line)
                version = obj.get("version", "")
                if is_stable_version(version):
                    fout.write(line)
            except Exception:
                continue

if __name__ == "__main__":
    filter_stable_versions("all_projects_versions.jsonl", "all_projects_versions_stable.jsonl")
