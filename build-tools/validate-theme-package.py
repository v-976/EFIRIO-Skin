#!/usr/bin/env python3
"""Validate an EFIRIO Theme Package against the repository's current schema.

Uses only the Python standard library. This implements the JSON Schema keywords
used by schemas/theme-package.schema.json; it is not a general-purpose JSON
Schema implementation.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "schemas" / "theme-package.schema.json"


class ValidationError(Exception):
    pass


def validate(value, schema, root_schema, path="$", ref_stack=()):
    """Validate the schema subset used by the checked-in package schema."""
    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/definitions/"):
            raise ValidationError(f"{path}: unsupported schema reference {ref!r}")
        name = ref.rsplit("/", 1)[1]
        if name in ref_stack:
            raise ValidationError(f"{path}: recursive schema reference {ref!r}")
        target = root_schema.get("definitions", {}).get(name)
        if target is None:
            raise ValidationError(f"{path}: unresolved schema reference {ref!r}")
        validate(value, target, root_schema, path, ref_stack + (name,))
        return

    expected = schema.get("type")
    type_checks = {
        "object": lambda v: isinstance(v, dict),
        "array": lambda v: isinstance(v, list),
        "string": lambda v: isinstance(v, str),
        "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    }
    if expected in type_checks and not type_checks[expected](value):
        raise ValidationError(f"{path}: expected {expected}")

    if "enum" in schema and value not in schema["enum"]:
        raise ValidationError(f"{path}: value {value!r} is not one of {schema['enum']!r}")
    if "pattern" in schema and isinstance(value, str):
        if re.search(schema["pattern"], value) is None:
            raise ValidationError(f"{path}: value {value!r} does not match pattern {schema['pattern']!r}")

    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                raise ValidationError(f"{path}: missing required property {key!r}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extras = sorted(set(value) - set(properties))
            if extras:
                raise ValidationError(f"{path}: unexpected propert{'y' if len(extras) == 1 else 'ies'} {', '.join(map(repr, extras))}")
        for key, child in properties.items():
            if key in value:
                validate(value[key], child, root_schema, f"{path}.{key}", ref_stack)
    elif isinstance(value, list) and "items" in schema:
        for index, item in enumerate(value):
            validate(item, schema["items"], root_schema, f"{path}[{index}]", ref_stack)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate an EFIRIO Theme Package JSON file.")
    parser.add_argument("package", help="path to package.json")
    args = parser.parse_args(argv)
    package_path = Path(args.package)

    try:
        with SCHEMA_PATH.open(encoding="utf-8") as schema_file:
            schema = json.load(schema_file)
        # utf-8-sig accepts legacy BOM input while all generated JSON remains BOM-free.
        with package_path.open(encoding="utf-8-sig") as package_file:
            package = json.load(package_file)
        validate(package, schema, schema)
    except FileNotFoundError as exc:
        target = "schema" if Path(exc.filename) == SCHEMA_PATH else "package"
        print(f"Error: {target} file not found: {exc.filename}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON in {exc.doc[:0]!r} at line {exc.lineno}, column {exc.colno}: {exc.msg}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"Error: cannot read file: {exc}", file=sys.stderr)
        return 1
    except ValidationError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Valid Theme Package: {package_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
