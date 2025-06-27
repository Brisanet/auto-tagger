import requests


class GitHubTagger:
    def __init__(self, owner: str, repo: str, token: str):
        if not token:
            raise EnvironmentError("Variável de ambiente AUTO_TAG_TOKEN não definida")

        self._owner = owner,
        self._repo = repo,
        self._token = token
        self._api_url = f"https://api.github.com/repos/{owner}/{repo}"
        self._headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        self.message = "Version updated by auto_tagger"

    def run(self):
        last_req = -1
        tag = 2

        last_pr = self.get_last_pr_info()[last_req]
        last_tag = last_pr.get('ref', "").split("/")[tag]
        new_tag = self.increment_tag(last_tag)
        last_object = last_pr.get('object', {}).get('sha', "")
        last_type = last_pr.get('object', {}).get('type', "")

        if new_tag:
            self.create_tag(new_tag, last_object, last_type)
        else:
            print("Tag atual inválida ou não segue padrão semântico.")

    def get_last_pr_info(self):
        url = f"{self._api_url}/git/matching-refs/tags"
        response = requests.get(url, headers=self._headers)
        response.raise_for_status()
        last_pr = response.json()
        if not last_pr:
            raise ValueError("Nenhuma tag encontrada. Crie uma tag inicial, como v0.0.0")
        return last_pr

    def increment_tag(self, tag: str) -> str | None:
        letter = "v"
        if tag.startswith(letter) and tag.count(".") == 2:
            major, minor, patch = map(int, tag[1:].split("."))
            if patch == 9:
                patch = 0
                minor += 1
                if minor > 9:
                    minor = 0
                    major += 1
            else:
                patch += 1
            return f"{letter}{major}.{minor}.{patch}"
        return None

    def create_tag(self, tag: str, last_obj: str, obj_type: str):
        tag_body = {
            "tag": tag,
            "message": self.message,
            "object": last_obj,
            "type": obj_type,
        }

        tag_url = f"{self._api_url}/git/tags"
        tag_resp = requests.post(tag_url, headers=self._headers, json=tag_body)
        tag_resp.raise_for_status()
        tag_data = tag_resp.json()

        ref_body = {
            "ref": f"refs/tags/{tag}",
            "sha": tag_data["sha"]
        }
        ref_url = f"{self._api_url}/git/refs"
        ref_resp = requests.post(ref_url, headers=self._headers, json=ref_body)
        ref_resp.raise_for_status()

        print(f"Nova tag criada: {tag}")
