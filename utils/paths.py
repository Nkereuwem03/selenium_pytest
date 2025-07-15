import os


def get_absolute_path(*path_parts: str) -> str:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.abspath(os.path.join(project_root, *path_parts))
