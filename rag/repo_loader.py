import os
import shutil
import subprocess
import tempfile


class RepoLoader:
    """
    Clones a public GitHub repository and reads supported source-code files.
    """

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
        ".hpp",
        ".html",
        ".css",
        ".json",
        ".md",
        ".yml",
        ".yaml",
        ".xml",
        ".sql",
        ".sh",
    }

    IGNORED_DIRECTORIES = {
        ".git",
        "node_modules",
        "__pycache__",
        ".venv",
        "venv",
        "env",
        "dist",
        "build",
        ".idea",
        ".vscode",
    }

    def __init__(self):
        self.temp_dir = None

    def clone_repository(self, repo_url):
        """
        Clone the GitHub repository into a temporary directory.
        """

        if not repo_url or not repo_url.strip():
            raise ValueError("Repository URL cannot be empty.")

        self.temp_dir = tempfile.mkdtemp(prefix="creatix_repo_")

        repo_path = os.path.join(
            self.temp_dir,
            "repository"
        )

        try:
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    repo_url,
                    repo_path,
                ],
                check=True,
                capture_output=True,
                text=True,
                timeout=120,
            )

            return repo_path

        except subprocess.TimeoutExpired:
            self.cleanup()

            raise RuntimeError(
                "Repository cloning timed out."
            )

        except subprocess.CalledProcessError as e:
            self.cleanup()

            error_message = e.stderr.strip()

            raise RuntimeError(
                f"Failed to clone repository: {error_message}"
            )

    def load_files(self, repo_path):
        """
        Read supported source-code files from the cloned repository.
        """

        documents = []

        for root, dirs, files in os.walk(repo_path):

            dirs[:] = [
                directory
                for directory in dirs
                if directory not in self.IGNORED_DIRECTORIES
            ]

            for filename in files:

                extension = os.path.splitext(
                    filename
                )[1].lower()

                if extension not in self.SUPPORTED_EXTENSIONS:
                    continue

                full_path = os.path.join(
                    root,
                    filename
                )

                relative_path = os.path.relpath(
                    full_path,
                    repo_path
                )

                try:
                    with open(
                        full_path,
                        "r",
                        encoding="utf-8",
                        errors="ignore",
                    ) as file:
                        content = file.read()

                    if content.strip():
                        documents.append(
                            {
                                "path": relative_path,
                                "content": content,
                            }
                        )

                except Exception as e:
                    print(
                        f"Skipping {relative_path}: {e}"
                    )

        return documents

    def load_repository(self, repo_url):
        """
        Clone repository and return readable documents.
        """

        repo_path = self.clone_repository(repo_url)

        documents = self.load_files(repo_path)

        if not documents:
            raise ValueError(
                "No supported source-code files were found."
            )

        return documents

    def cleanup(self):
        """
        Delete the temporary cloned repository.
        """

        if (
            self.temp_dir
            and os.path.exists(self.temp_dir)
        ):
            shutil.rmtree(
                self.temp_dir,
                ignore_errors=True
            )

            self.temp_dir = None