import argparse
import dataclasses
import os
import shutil
import tarfile
import tempfile
import zipfile
from io import BytesIO

import requests

DEFAULT_OWNER = "oraNod"
DEFAULT_REPO_NAME = "ansible-documentation"
DEFAULT_OUTPUT_DIR = "output"


@dataclasses.dataclass()
class Args:
    owner: str | None
    repo: str
    output: str


def parse_args(args: list[str] | None = None) -> Args:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--owner",
        help="Specify the repository owner. Default: (%(default)s)",
        default=DEFAULT_OWNER,
    )
    parser.add_argument(
        "--repo",
        help="Specify the repository name. Default: %(default)s",
        default=DEFAULT_REPO_NAME,
    )
    parser.add_argument(
        "--output",
        help="Specify the name of the target output directory. Default: %(default)s",
        default=DEFAULT_OUTPUT_DIR,
    )
    return Args(**vars(parser.parse_args(args)))


def list_artifacts(args: Args):
    url = f"https://api.github.com/repos/{args.owner}/{args.repo}/actions/artifacts"

    headers = {
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github.v3+json",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        artifacts = response.json()["artifacts"]
        if artifacts:
            most_recent_artifact = artifacts[0]["id"]
            return most_recent_artifact
        else:
            print("Could not get the most recent artifact.")
            return None
    else:
        print("Docs build artifacts not available.")
        return None


most_recent_artifact = list_artifacts(parse_args())


def main(args: Args):

    url = f"https://api.github.com/repos/{args.owner}/{args.repo}/actions/artifacts/{most_recent_artifact}"

    headers = {
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github.v3+json",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        download_url = response.json()["archive_download_url"]
        download_response = requests.get(download_url, headers=headers)
        dir = tempfile.mkdtemp()
        tarball = os.path.join(dir, "build.tar.gz")

        if download_response.status_code == 200:
            with open(os.path.join(dir, "build.zip"), "wb") as f:
                f.write(download_response.content)
            print(f"Successfully downloaded docs build archive.")
        else:
            print(f"Failed to download docs build archive.")

        with zipfile.ZipFile(BytesIO(download_response.content), "r") as zip_ref:
            zip_ref.extractall(dir)

        if os.path.exists(args.output):
            shutil.rmtree(args.output)
        os.makedirs(args.output)

        with tarfile.open(tarball, "r:gz") as tar_ref:
            tar_ref.extractall(args.output, filter="fully_trusted")
        print(f"Successfully extracted docs build to the target directory.")

    else:
        print(f"Docs build archive does not exist.")


if __name__ == "__main__":
    main(parse_args())
