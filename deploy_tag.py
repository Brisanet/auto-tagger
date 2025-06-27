import argparse
import os

from auto_tagger.github_tagger import GitHubTagger

if __name__ == "__main__":
    token = os.getenv("AUTO_TAG_TOKEN")

    parser = argparse.ArgumentParser(description="Auto tagger module")
    parser.add_argument("--repo", type=str, required=True, help="Name repository GitHub")

    args = parser.parse_args()
    repository = str(args.repo).split("/") # --repo "${{ github.repository }}" -> owner/repo

    tagger = GitHubTagger(owner=repository[0], repo=repository[1], token=token)
    tagger.run()
