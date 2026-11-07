#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""Local JSON project persistence for engineering calculation snapshots."""
import json
import os
import re
import tempfile
from pathlib import Path


def safe_name(name):
    name = name.strip()
    if not name or len(name) > 80 or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 _-]*", name):
        raise ValueError("Project name must use letters, numbers, spaces, _ or - (max 80).")
    return name


class Workspace:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def path(self, name):
        return self.directory / (safe_name(name) + ".json")

    def list_projects(self):
        return sorted(p.stem for p in self.directory.glob("*.json") if p.is_file())

    def load(self, name):
        path = self.path(name)
        if not path.exists():
            return {"name": safe_name(name), "calculations": []}
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or data.get("name") != name or not isinstance(data.get("calculations"), list):
            raise ValueError("Invalid project file format.")
        return data

    def save(self, project):
        name = safe_name(project["name"])
        if not isinstance(project.get("calculations"), list):
            raise ValueError("Calculations must be a list.")
        target = self.path(name)
        payload = json.dumps(project, ensure_ascii=True, indent=2, allow_nan=False)
        fd, temp_path = tempfile.mkstemp(prefix=".workspace-", suffix=".tmp", dir=self.directory)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                stream.write(payload)
            os.replace(temp_path, target)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        return target

    def update_calculation(self, name, index, calculation, inputs, outputs, assumptions):
        project = self.load(name)
        if not 0 <= index < len(project["calculations"]):
            raise IndexError("Calculation index out of range.")
        project["calculations"][index] = {"type": calculation, "inputs": inputs,
                                          "outputs": outputs, "assumptions": assumptions}
        self.save(project)
        return project

    def delete_calculation(self, name, index):
        project = self.load(name)
        if not 0 <= index < len(project["calculations"]):
            raise IndexError("Calculation index out of range.")
        del project["calculations"][index]
        self.save(project)
        return project

    def add_calculation(self, name, calculation, inputs, outputs, assumptions):
        project = self.load(name)
        project["calculations"].append({"type": calculation, "inputs": inputs,
                                         "outputs": outputs, "assumptions": assumptions})
        self.save(project)
        return project
