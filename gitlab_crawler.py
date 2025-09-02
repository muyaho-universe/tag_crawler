import requests
import json

# libtiff 공식 GitLab 저장소 정보
GITLAB_PROJECT = "libtiff/libtiff"
GITLAB_API_URL = "https://gitlab.com/api/v4/projects"
# 프로젝트 ID 대신 URL-encoded 경로 사용
GITLAB_PROJECT_ENCODED = requests.utils.quote(GITLAB_PROJECT, safe='')

def get_gitlab_tags(project_encoded):
    """GitLab 저장소의 모든 태그를 가져옵니다."""
    tags = []
    url = f"{GITLAB_API_URL}/{project_encoded}/repository/tags?per_page=100"
    while url:
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if not data:
                break
            for tag in data:
                tags.append(tag['name'])
            # 페이지네이션: 'X-Next-Page' 헤더 사용
            next_page = response.headers.get('X-Next-Page')
            if next_page:
                url = f"{GITLAB_API_URL}/{project_encoded}/repository/tags?per_page=100&page={next_page}"
            else:
                url = None
        except requests.exceptions.RequestException as e:
            print(f"오류 발생: GitLab 저장소 태그를 가져올 수 없습니다. ({e})")
            return []
    return tags

def save_versions_jsonl(project, versions, filename):
    with open(filename, "w", encoding="utf-8") as f:
        for version in versions:
            line = json.dumps({"project": project, "version": version})
            f.write(line + "\n")

def append_versions_to_all_projects(project, versions, filename="all_projects_versions.jsonl"):
    with open(filename, "a", encoding="utf-8") as f:
        for version in versions:
            line = json.dumps({"project": project, "version": version})
            f.write(line + "\n")

def main():
    print("--- libtiff GitLab 저장소 태그 수집 시작 ---\n")
    versions = get_gitlab_tags(GITLAB_PROJECT_ENCODED)
    if versions:
        print(f"✅ [libtiff] 총 {len(versions)}개의 버전을 찾았습니다.")
        print(f"   (샘플: {', '.join(versions[:5])}, ..., {', '.join(versions[-5:])})\n")
        save_versions_jsonl("libtiff", versions, "libtiff_gitlab_versions.jsonl")
        append_versions_to_all_projects("libtiff", versions, "all_projects_versions.jsonl")
    else:
        print("❌ [libtiff] 버전을 가져오지 못했습니다.\n")
    print("--- 작업 완료 ---")

if __name__ == "__main__":
    main()