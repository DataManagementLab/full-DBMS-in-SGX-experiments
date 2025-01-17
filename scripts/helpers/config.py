import json
import pathlib

try:
    with open(pathlib.Path.home() / "machine-config.json") as machine_config_file:
        MachineConfig = json.load(machine_config_file)
except (FileNotFoundError, json.JSONDecodeError):
    print("Unable to load machine-config.json")
    MachineConfig = {}
