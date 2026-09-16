"""Build the consolidated access-control ground-truth entity index.

This utility reads only the JSON annotations stored beside it and writes only
``entities.csv`` in this directory.  It is deliberately independent from the
DRHL extraction and repair pipelines.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
APPLICATIONS = ROOT / "applications"
OUTPUT = ROOT / "entities.csv"


def normalized_name(value: Any) -> str:
    """Match the normalization used by the extraction evaluation."""
    text = str(value or "").strip().casefold().replace('"', "'")
    text = re.sub(r"\s+", "", text)
    return text.lstrip("$")


def read_document(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def merge_text(values: list[str]) -> str:
    return " | ".join(dict.fromkeys(value for value in values if value))


def build_rows() -> list[dict[str, str | int]]:
    grouped: dict[tuple[str, str, str], dict[str, Any]] = {}
    for app_dir in sorted(path for path in APPLICATIONS.iterdir() if path.is_dir()):
        for entity_type, filename, collection in (
            ("parameter", "parameters.json", "parameters"),
            ("function", "functions.json", "functions"),
        ):
            document = read_document(app_dir / filename)
            app = str(document.get("app") or app_dir.name)
            language = str(document.get("language") or "")
            for item in document.get(collection, []):
                name = str(item.get("name") or "").strip()
                key = (app.casefold(), entity_type, normalized_name(name))
                if not key[2]:
                    continue
                row = grouped.setdefault(
                    key,
                    {
                        "Application": app,
                        "Language": language,
                        "Entity Type": entity_type,
                        "Name": name,
                        "Kind": [],
                        "Source": [],
                        "Files": [],
                        "Start Line": [],
                        "End Line": [],
                        "Rationale": [],
                        "Annotation Occurrences": 0,
                    },
                )
                row["Annotation Occurrences"] += 1
                row["Kind"].append(str(item.get("kind") or ""))
                row["Source"].append(str(item.get("source") or ""))
                files = list(item.get("files") or [])
                if item.get("file"):
                    files.append(item["file"])
                row["Files"].extend(str(value).replace("\\", "/") for value in files)
                if item.get("start_line") is not None:
                    row["Start Line"].append(str(item["start_line"]))
                if item.get("end_line") is not None:
                    row["End Line"].append(str(item["end_line"]))
                row["Rationale"].append(str(item.get("rationale") or ""))

    rows: list[dict[str, str | int]] = []
    for row in grouped.values():
        rows.append(
            {
                "Application": row["Application"],
                "Language": row["Language"],
                "Entity Type": row["Entity Type"],
                "Name": row["Name"],
                "Kind": merge_text(row["Kind"]),
                "Source": merge_text(row["Source"]),
                "Files": merge_text(row["Files"]),
                "Start Line": merge_text(row["Start Line"]),
                "End Line": merge_text(row["End Line"]),
                "Rationale": merge_text(row["Rationale"]),
                "Annotation Occurrences": row["Annotation Occurrences"],
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            str(row["Application"]).casefold(),
            str(row["Entity Type"]),
            normalized_name(row["Name"]),
        ),
    )


def main() -> None:
    rows = build_rows()
    fieldnames = [
        "Application",
        "Language",
        "Entity Type",
        "Name",
        "Kind",
        "Source",
        "Files",
        "Start Line",
        "End Line",
        "Rationale",
        "Annotation Occurrences",
    ]
    with OUTPUT.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    parameter_count = sum(row["Entity Type"] == "parameter" for row in rows)
    function_count = sum(row["Entity Type"] == "function" for row in rows)
    if (parameter_count, function_count) != (140, 23):
        raise ValueError(
            "unexpected unique ground-truth counts: "
            f"parameters={parameter_count}, functions={function_count}"
        )
    print(
        f"wrote {OUTPUT}: {parameter_count} parameters, "
        f"{function_count} functions"
    )


if __name__ == "__main__":
    main()
