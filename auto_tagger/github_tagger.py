import re
import requests


SEMVER_REGEX = re.compile(r"^v(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)$")


class GitHubTagger:
    def __init__(self, owner: str, repo: str, token: str):
        if not token:
            raise EnvironmentError("Variável de ambiente AUTO_TAG_TOKEN não definida")

        self._owner = owner
        self._repo = repo
        self._token = token
        self._api_url = f"https://api.github.com/repos/{owner}/{repo}"
        self._headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        self.message = "Version updated by auto_tagger"

    def run(self):
        last_tag_info = self.get_last_tag_info()
        last_tag = last_tag_info["ref"].split("/")[-1]

        new_tag = self.increment_patch(last_tag)

        if not new_tag:
            raise ValueError("Tag atual inválida ou não segue o padrão SemVer (vMAJOR.MINOR.PATCH)")

        head_sha = self.get_default_branch_head()

        self.create_tag(new_tag, head_sha, "commit")

    def get_last_tag_info(self) -> dict:
        url = f"{self._api_url}/git/matching-refs/tags"
        response = requests.get(url, headers=self._headers)
        response.raise_for_status()

        tags = response.json()
        semver_tags = [tag for tag in tags if SEMVER_REGEX.match(tag["ref"].split("/")[-1])]
        if not semver_tags:
            raise ValueError("Nenhuma tag encontrada. Crie uma tag inicial, como v0.0.0")

        # A API retorna as refs em ordem alfabética (v1.0.10 vem antes de v1.0.9),
        # então a última tag precisa ser resolvida comparando os números da versão
        return max(semver_tags, key=self._semver_key)

    @staticmethod
    def _semver_key(tag_info: dict) -> tuple[int, int, int]:
        match = SEMVER_REGEX.match(tag_info["ref"].split("/")[-1])
        return (int(match.group("major")), int(match.group("minor")), int(match.group("patch")))

    def get_default_branch_head(self) -> str:
        repo_resp = requests.get(self._api_url, headers=self._headers)
        repo_resp.raise_for_status()
        default_branch = repo_resp.json()["default_branch"]

        ref_url = f"{self._api_url}/git/ref/heads/{default_branch}"
        ref_resp = requests.get(ref_url, headers=self._headers)
        ref_resp.raise_for_status()

        return ref_resp.json()["object"]["sha"]

    def increment_patch(self, tag: str) -> str | None:
        match = SEMVER_REGEX.match(tag)
        if not match:
            return None

        major = int(match.group("major"))
        minor = int(match.group("minor"))
        patch = int(match.group("patch")) + 1

        return f"v{major}.{minor}.{patch}"

    def create_tag(self, tag: str, obj_sha: str, obj_type: str):
        tag_body = {
            "tag": tag,
            "message": self.message,
            "object": obj_sha,
            "type": obj_type,
        }

        tag_url = f"{self._api_url}/git/tags"
        tag_resp = requests.post(tag_url, headers=self._headers, json=tag_body)
        tag_resp.raise_for_status()
        tag_data = tag_resp.json()

        ref_body = {
            "ref": f"refs/tags/{tag}",
            "sha": tag_data["sha"],
        }

        ref_url = f"{self._api_url}/git/refs"
        ref_resp = requests.post(ref_url, headers=self._headers, json=ref_body)
        ref_resp.raise_for_status()

        print(f"Nova tag criada: {tag}")
