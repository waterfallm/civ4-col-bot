"""
src.config
==========
Loads bot configuration from config.json at the project root.
"""

import json
import logging
import os
from typing import Any, Dict

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.json")


def load_config() -> Dict[str, Any]:
    """Read and return the parsed config.json dictionary."""
    with open(_CONFIG_PATH, "r") as fh:
        return json.load(fh)


# Module-level singleton so the config is only read once per process.
config: Dict[str, Any] = load_config()

# Configure the root logger based on the config file.
logging.basicConfig(
    level=getattr(logging, config.get("logging", {}).get("level", "INFO")),
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
