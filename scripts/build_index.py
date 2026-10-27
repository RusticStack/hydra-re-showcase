"""Validate every project and write index.json, the file the website reads.

    python scripts/build_index.py          # rewrite index.json
    python scripts/build_index.py --check  # fail if a project is invalid or index.json is stale

A project is a folder projects/<slug>/ with project.json (see project.schema.json) and one cover
image, cover.jpg, cover.png or cover.webp, 1200x630 or the same 1.9:1 shape, at most 600 KB.
Standard library only.
"""
import json
import pathlib
import re
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "project.schema.json").read_text(encoding="utf-8"))
COVERS = ("cover.jpg", "cover.png", "cover.webp")
MAX_COVER = 600 * 1024


def image_size(path):
    data = path.read_bytes()
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", data[16:24])
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        if data[12:16] == b"VP8X":
            return int.from_bytes(data[24:27], "little") + 1, int.from_bytes(data[27:30], "little") + 1
        if data[12:16] == b"VP8 ":
            return struct.unpack("<HH", data[26:30])[0] & 0x3FFF, struct.unpack("<HH", data[26:30])[1] & 0x3FFF
    if data[:2] == b"\xff\xd8":
        i = 2
        while i < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2):
                h, w = struct.unpack(">HH", data[i + 5 : i + 9])
                return w, h
            i += 2 + struct.unpack(">H", data[i + 2 : i + 4])[0]
    raise ValueError("not a JPEG, PNG or WebP image")


def check(value, schema, where):
    errors = []
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{where}: must be one of {schema['enum']}")
    kind = schema.get("type")
    if kind == "string":
        if not isinstance(value, str):
            return [f"{where}: must be a string"]
        if len(value) < schema.get("minLength", 0) or len(value) > schema.get("maxLength", 10**9):
            errors.append(f"{where}: length {len(value)} outside {schema.get('minLength', 0)}..{schema.get('maxLength')}")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{where}: does not match {schema['pattern']}")
    elif kind == "array":
        if not isinstance(value, list):
            return [f"{where}: must be a list"]
        if len(value) > schema.get("maxItems", 10**9):
            errors.append(f"{where}: at most {schema['maxItems']} items")
        for i, item in enumerate(value):
            errors += check(item, schema["items"], f"{where}[{i}]")
    elif kind == "object":
        if not isinstance(value, dict):
            return [f"{where}: must be an object"]
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{where}: missing '{key}'")
        for key, item in value.items():
            if key not in schema["properties"]:
                errors.append(f"{where}: unknown field '{key}'")
            else:
                errors += check(item, schema["properties"][key], f"{where}.{key}")
    return errors


def build():
    projects, errors = [], []
    for folder in sorted((ROOT / "projects").iterdir()):
        if not folder.is_dir():
            continue
        slug = folder.name
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug):
            errors.append(f"{slug}: folder names are lowercase words joined by '-'")
        try:
            data = json.loads((folder / "project.json").read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            errors.append(f"{slug}/project.json: {e}")
            continue
        errors += check(data, SCHEMA, f"{slug}/project.json")
        covers = [c for c in COVERS if (folder / c).exists()]
        if len(covers) != 1:
            errors.append(f"{slug}: needs exactly one of {', '.join(COVERS)}")
        else:
            cover = folder / covers[0]
            try:
                w, h = image_size(cover)
                if abs(w / h - 1200 / 630) > 0.05:
                    errors.append(f"{slug}/{covers[0]}: {w}x{h} is not 1.9:1 (1200x630)")
            except ValueError as e:
                errors.append(f"{slug}/{covers[0]}: {e}")
            if cover.stat().st_size > MAX_COVER:
                errors.append(f"{slug}/{covers[0]}: larger than 600 KB")
            data = {"slug": slug, **data, "cover": f"projects/{slug}/{covers[0]}"}
        projects.append(data)
    projects.sort(key=lambda p: (p.get("added", ""), p["slug"]), reverse=True)
    return {"version": 1, "projects": projects}, errors


def main():
    index, errors = build()
    text = json.dumps(index, indent=2, ensure_ascii=False) + "\n"
    target = ROOT / "index.json"
    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(1)
    if "--check" in sys.argv:
        if not target.exists() or target.read_text(encoding="utf-8") != text:
            print("index.json is out of date: run python scripts/build_index.py", file=sys.stderr)
            sys.exit(1)
        print(f"ok: {len(index['projects'])} projects")
        return
    target.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote index.json: {len(index['projects'])} projects")


if __name__ == "__main__":
    main()
