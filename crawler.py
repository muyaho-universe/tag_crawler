import requests
import os
import json

# 각 프로젝트의 GitHub '소유자/저장소' 정보
# 참고: libtiff의 공식 저장소는 GitLab에 있어 GitHub API로는 조회가 어렵습니다.
#       여기서는 널리 사용되는 미러(mirror) 저장소를 대상으로 합니다.
PROJECTS = {
    "exiv2": "Exiv2/exiv2",
    "freetype": "freetype/freetype",
    "libexif": "libexif/libexif",
    "libexpat": "libexpat/libexpat",
    "liblouis": "liblouis/liblouis",
    "libming": "libming/libming",
    "libpng": "glennrp/libpng",
    "libredwg": "LibreDWG/libredwg",
    "libtiff": "remotesensinginfo/libtiff", # 공식 저장소는 GitLab에 있음
    "libxml2": "GNOME/libxml2",
    "libxslt": "GNOME/libxslt",
    "openssl": "openssl/openssl",
    "tcpdump": "the-tcpdump-group/tcpdump",
}

# (선택사항) GitHub API 토큰 설정. 
# API 요청 횟수 제한을 늘리기 위해 사용하는 것을 강력히 권장합니다.
# https://github.com/settings/tokens 에서 발급받을 수 있습니다.
# 발급받은 토큰을 아래에 직접 넣거나, 환경 변수로 설정하세요.
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", None)

def get_all_tags(owner, repo):
    """지정된 GitHub 저장소의 모든 태그를 가져옵니다."""
    tags = []
    # GitHub API는 결과를 여러 페이지에 나눠서 제공하므로, 다음 페이지를 계속 요청해야 합니다.
    url = f"https://api.github.com/repos/{owner}/{repo}/tags?per_page=100"
    headers = {"Accept": "application/vnd.github.v3+json"}

    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
        print(f"INFO: 인증된 API 요청을 사용합니다. (요청 제한 상향)")

    while url:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # HTTP 오류가 발생하면 예외를 발생시킴

            data = response.json()
            if not data:
                break
                
            for tag in data:
                tags.append(tag['name'])

            # 다음 페이지 URL 확인 (페이지네이션)
            if 'next' in response.links:
                url = response.links['next']['url']
            else:
                url = None # 마지막 페이지
                
        except requests.exceptions.HTTPError as e:
            print(f"오류 발생: {repo} 저장소를 찾을 수 없거나 API 요청에 실패했습니다. (에러: {e})")
            return []
        except requests.exceptions.RequestException as e:
            print(f"네트워크 오류가 발생했습니다: {e}")
            return []
            
    return tags


def save_all_projects_versions_jsonl(project_versions_dict, filename="all_projects_versions.jsonl"):
    """전체 프로젝트별 모든 버전 정보를 jsonl 파일로 저장합니다."""
    with open(filename, "w", encoding="utf-8") as f:
        for project, versions in project_versions_dict.items():
            for version in versions:
                line = json.dumps({"project": project, "version": version})
                f.write(line + "\n")

def save_project_release_version_txt(project, version, filename=None):
    """프로젝트별 release version을 텍스트 파일로 저장합니다."""
    if filename is None:
        filename = f"{project}_release.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(str(version) + "\n")

def save_project_release_version_jsonl(project, version, filename=None):
    """프로젝트별 release version을 jsonl 파일로 저장합니다."""
    if filename is None:
        filename = f"{project}_release.jsonl"
    with open(filename, "w", encoding="utf-8") as f:
        line = json.dumps({"project": project, "version": version})
        f.write(line + "\n")
def main():
    """메인 실행 함수"""
    print("--- 프로젝트 버전 정보 수집 시작 ---\n")
    
    # 전체 프로젝트별 모든 버전 정보를 저장할 dict
    all_project_versions = {}
    for name, path in PROJECTS.items():
        owner, repo = path.split('/')
        
        print(f"[{name}] 저장소의 태그를 가져오는 중...")
        
        versions = get_all_tags(owner, repo)
        if versions:
            print(f"✅ [{name}] 총 {len(versions)}개의 버전을 찾았습니다.")
            # 찾은 버전 중 처음 5개와 마지막 5개만 샘플로 출력
            if len(versions) > 10:
                print(f"   (샘플: {', '.join(versions[:5])}, ..., {', '.join(versions[-5:])})\n")
            else:
                print(f"   - 버전: {', '.join(versions)}\n")
            # 전체 버전 저장
            all_project_versions[name] = versions
            # 최신(release) 버전 추정: 태그 리스트의 첫 번째 값 사용 (정렬 필요시 추가)
            latest_version = versions[0]
            save_project_release_version_txt(name, latest_version)
            save_project_release_version_jsonl(name, latest_version)
        else:
            print(f"❌ [{name}] 버전을 가져오지 못했습니다.\n")

    # 전체 프로젝트별 모든 버전 정보를 jsonl로 저장
    save_all_projects_versions_jsonl(all_project_versions)
    print("--- 모든 작업 완료 ---")


if __name__ == "__main__":
    main()