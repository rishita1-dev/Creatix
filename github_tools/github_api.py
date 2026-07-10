from github import Github
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Read GitHub Token
TOKEN = os.getenv("GITHUB_TOKEN")

# Connect to GitHub
github = Github(TOKEN)


def get_repository(repo_name):
    """
    Returns the GitHub repository object.
    Example:
    repo_name = "octocat/Hello-World"
    """

    repo = github.get_repo(repo_name)

    return repo

def get_files(repo):

    contents = repo.get_contents("")

    files = []

    while contents:

        file = contents.pop(0)

        if file.type == "dir":

            contents.extend(repo.get_contents(file.path))

        else:

            files.append(file.path)

    return files

def read_file(repo, file_path):

    file = repo.get_contents(file_path)

    content = file.decoded_content.decode()

    return content

def get_repository_content(repo):
    """
    Reads all supported files from a GitHub repository
    and combines them into one string.
    """

    files = get_files(repo)
    print(files)

    repository_text = ""

    allowed_extensions = (
        ".py",
        ".java",
        ".cpp",
        ".c",
        ".js",
        ".ts",
        ".md",
        ".txt"
    )

    for file in files:

        if file.endswith(allowed_extensions) or file.upper().startswith("README"):

            try:

                content = read_file(repo, file)

                repository_text += f"\n\n===== {file} =====\n"

                repository_text += content

            except Exception as e:

                print(e)

    return repository_text