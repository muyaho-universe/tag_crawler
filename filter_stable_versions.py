import json
import re

def is_stable_version(version):
    # 제외할 키워드 (정식 릴리스가 아닌 것들)
    exclude_keywords = [
        "rc", "beta", "alpha", "nightly", "dev", "test", "preview", "pre", "draft",
        "master", "signed", "bp", "before", "after", "LEVITTE", "COMPAQ_PATCH",
        "engine", "FIPS", "SSLeay", "ChangeLog", "CVE", "GNUMERIC", "GNOME", "EAZEL", "STATE"
    ]
    version_lower = version.lower()
    # 키워드가 포함되어 있으면 제외
    for kw in exclude_keywords:
        if kw.lower() in version_lower:
            return False
    # 숫자와 점/하이픈/언더바로 끝나는 경우만 허용 (예: v1.2.3, 1.2.3, OpenSSL_1_1_1w)
    if re.match(r"^(v)?\d+([.\-_]\d+)*([a-z]?)$", version_lower):
        return True
    # 그 외는 제외
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
