"""
build_static_data.py
Genera docs/data.js (datos estáticos para GitHub Pages) a partir de
curriculum_data.py y academic_data.json.

Uso:
    python3 tools/build_static_data.py
"""

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from curriculum_data import AREAS, CURRICULUM  # noqa: E402

DATA_FILE = ROOT / "academic_data.json"
OUT_FILE = ROOT / "docs" / "data.js"


def main() -> None:
    academic = {}
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as fh:
            academic = json.load(fh)

    payload = {
        "areas": AREAS,
        "curriculum": CURRICULUM,
        "student": academic.get("student_info", {}),
        "history": academic.get("academic_history", {}),
    }

    body = json.dumps(payload, ensure_ascii=False, indent=2)
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(
        "/* Generado por tools/build_static_data.py - no editar a mano. */\n"
        "window.CDO_DATA = " + body + ";\n",
        encoding="utf-8",
    )
    print(
        f"OK  {OUT_FILE.relative_to(ROOT)}  "
        f"({len(CURRICULUM)} materias, {len(payload['history'])} registros)"
    )


if __name__ == "__main__":
    main()
