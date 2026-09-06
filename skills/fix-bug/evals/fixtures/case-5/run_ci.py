import importlib.util
import json
from pathlib import Path
import sys

root = Path(__file__).parent
config = json.loads((root / "ci_config.json").read_text(encoding="utf-8"))
dependency_path = root / config["sluglib_path"]
spec = importlib.util.spec_from_file_location("sluglib", dependency_path)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)
sys.modules["sluglib"] = module

from src.slugs import build_slug

result = build_slug("Café Guide")
assert result == "café-guide", result
print(result)
