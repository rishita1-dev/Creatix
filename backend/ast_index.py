from pathlib import Path
from typing import Dict, List, Optional

from backend.ast_parser import ASTParser


class ASTIndex:
    """
    Builds a searchable index of the repository's Python code.
    """

    def __init__(self):
        self.parser = ASTParser()

        self.files = {}
        self.function_index = {}
        self.class_index = {}
        self.import_index = {}

    def build(self, repo_path: str):
        """
        Parse every Python file and build indexes.
        """

        repo_data = self.parser.parse_repository(repo_path)

        self.files.clear()
        self.function_index.clear()
        self.class_index.clear()
        self.import_index.clear()

        for file_data in repo_data:

            if "error" in file_data:
                continue

            file_path = file_data["file"]

            self.files[file_path] = file_data

            # -------------------------
            # Functions
            # -------------------------

            for function in file_data["functions"]:

                self.function_index[function["name"]] = {
                    "file": file_path,
                    "data": function
                }

            # -------------------------
            # Classes
            # -------------------------

            for cls in file_data["classes"]:

                self.class_index[cls["name"]] = {
                    "file": file_path,
                    "data": cls
                }

                # Index class methods as functions too
                for method in cls["methods"]:

                    self.function_index[method["name"]] = {
                        "file": file_path,
                        "data": method,
                        "class": cls["name"]
                    }

            # -------------------------
            # Imports
            # -------------------------

            self.import_index[file_path] = file_data["imports"]

    # ==========================================================
    # SEARCH FUNCTIONS
    # ==========================================================

    def get_function(self, function_name: str) -> Optional[Dict]:

        return self.function_index.get(function_name)

    def get_class(self, class_name: str) -> Optional[Dict]:

        return self.class_index.get(class_name)

    def get_file(self, file_path: str) -> Optional[Dict]:

        return self.files.get(file_path)

    def list_functions(self) -> List[str]:

        return sorted(self.function_index.keys())

    def list_classes(self) -> List[str]:

        return sorted(self.class_index.keys())

    def list_files(self) -> List[str]:

        return sorted(self.files.keys())

    def search_import(self, module_name: str) -> List[str]:

        results = []

        for file, imports in self.import_index.items():

            for imp in imports:

                if module_name.lower() in imp.lower():
                    results.append(file)
                    break

        return results

    # ==========================================================
    # SUMMARY
    # ==========================================================

    def summary(self):

        return {
            "python_files": len(self.files),
            "functions": len(self.function_index),
            "classes": len(self.class_index)
        }