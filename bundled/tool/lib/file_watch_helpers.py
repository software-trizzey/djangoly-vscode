import os
import re

import pathlib
from typing import List
from pygls import workspace, server
from lsprotocol.types import MessageType


def is_django_view_file(document: workspace.Document) -> bool:
    """Check if the current file is a Django view file."""
    view_file_pattern = re.compile(r"views\.py$")
    return view_file_pattern.search(document.path) is not None


def notify_user_to_test_change(LSP_SERVER: server.LanguageServer, document: workspace.Document) -> None:
    """Notify the user to test changes when a Django view file is saved."""
    base_file_name = os.path.basename(document.path)
    message = f"The Django view file '{base_file_name}' was modified and saved. Please ensure the changes are tested."
    LSP_SERVER.show_message(message, MessageType.Warning)


def get_possible_test_paths(source_uri: str) -> List[str]:
    """Generate possible test paths for the given source file."""
    parsed_path = pathlib.Path(source_uri)
    test_paths = []

    if parsed_path.suffix in [".py"]:
        test_paths = get_python_test_paths(parsed_path)
    
    return test_paths


def get_python_test_paths(parsed_path: pathlib.Path) -> List[str]:
    """Generate possible test paths for Python files."""
    if "/tests/" in parsed_path.parent.as_posix():
        print(f"Already in tests directory: {parsed_path}")
        return []

    if parsed_path.name == "views.py":
        return [
            parsed_path.parent / "tests" / "test_views.py",
            parsed_path.parent.parent / "tests" / "test_views.py",
            parsed_path.parent.parent / "tests" / "views" / "test_views.py"
        ]

    # Possible test directories based on the source file path
    test_dirs = [
        parsed_path.parent,
        parsed_path.parent / "tests",
        parsed_path.parent.parent / "tests" / parsed_path.parent.name,
        parsed_path.parent.parent / "tests" / "views",
        parsed_path.parent.parent / "tests" / "api",
        parsed_path.parent.parent / "tests" / parsed_path.parent.name,
        parsed_path.parent.parent / "tests",
    ]

    # Possible test file names based on the source file name
    test_names = [
        f"test_{parsed_path.stem}{parsed_path.suffix}",
        f"test_{parsed_path.stem}s{parsed_path.suffix}",
        f"{parsed_path.stem}_tests{parsed_path.suffix}",
        f"{parsed_path.stem}s_tests{parsed_path.suffix}",
    ]

    # Combine test directories and test names to generate full test paths
    test_paths = []
    for test_dir in test_dirs:
        for test_name in test_names:
            test_paths.append(os.path.join(test_dir.as_posix(), test_name))
    
    return test_paths


def check_for_test_file(source_uri: str) -> bool:
    """Check if a test file exists for the given source file."""
    test_paths = get_possible_test_paths(source_uri)
    for test_path in test_paths:
        if os.path.exists(test_path):
            return True
    return False
