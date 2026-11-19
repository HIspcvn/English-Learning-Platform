import argparse
import json
from pathlib import Path

from app.main import app


def main() -> None:
    parser = argparse.ArgumentParser(description="Export the API's OpenAPI schema.")
    parser.add_argument("--output", required=True, type=Path)
    destination = parser.parse_args().output
    schema = json.dumps(app.openapi(), indent=2, sort_keys=True, ensure_ascii=False)
    destination.write_text(schema + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
