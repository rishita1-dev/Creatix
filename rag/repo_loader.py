import os
import shutil
import tempfile
from git import Repo


# File types that Creatix will read from a repository
SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".cpp",
    ".c",
    ".h",
    ".html",
    ".css",
    ".json",
    ".md",
}


def clone_repository(repo_url):
    """
    Clone a GitHub repository into a temporary folder.
    """

    temp_dir = tempfile.mkdtemp()

    try:
        Repo.clone_from(repo_url, temp_dir)
        return temp_dir

    except Exception as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise Exception(f"Failed to clone repository: {str(e)}")


def load_repository_files(repo_path):
    """
    Read all supported code files from the repository.
    """

    documents = []

    for root, dirs, files in os.walk(repo_path):

        # Ignore unnecessary large folders
        dirs[:] = [
            directory
            for directory in dirs
            if directory not in {
                ".git",
                "node_modules",
                "__pycache__",
                ".venv",
                "venv",
            }
        ]

        for file in files:

            extension = os.path.splitext(file)[1].lower()

            if extension in SUPPORTED_EXTENSIONS:

                file_path = os.path.join(root, file)

                try:
                    with open(
                        file_path,
                        "r",
                        encoding="utf-8",
                        errors="ignore",
                    ) as f:

                        content = f.read()

                    relative_path = os.path.relpath(
                        file_path,
                        repo_path,
                    )

                    documents.append(
                        {
                            "file_path": relative_path,
                            "content": content,
                        }
                    )

                except Exception as e:
                    print(f"Could not read {file_path}: {e}")

    return documents


def load_github_repository(repo_url):
    """
    Complete process:
    Clone repository -> Read files -> Delete temporary repository
    """

    repo_path = clone_repository(repo_url)

    try:
        documents = load_repository_files(repo_path)
        return documents

    finally:
        shutil.rmtree(repo_path, ignore_errors=True)