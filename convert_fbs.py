#!/usr/bin/env python3

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


SCALAR_TO_ROS = {
    "bool": "bool",
    "byte": "int8",
    "ubyte": "uint8",
    "short": "int16",
    "ushort": "uint16",
    "int": "int32",
    "uint": "uint32",
    "long": "int64",
    "ulong": "uint64",
    "float": "float32",
    "double": "float64",
    "string": "string",
}

REPO_ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Definition:
    kind: str
    name: str
    namespace: str
    source: Path
    members: list[tuple[str, str]]

    @property
    def qname(self) -> str:
        return f"{self.namespace}.{self.name}"

    @property
    def package(self) -> str:
        return self.namespace.split(".")[0]


COMMENT_BLOCK_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
COMMENT_LINE_RE = re.compile(r"//.*?$", re.MULTILINE)
NAMESPACE_RE = re.compile(r"namespace\s+([A-Za-z0-9_.]+)\s*;")
DEFINITION_RE = re.compile(r"(struct|table|union)\s+([A-Za-z0-9_]+)\s*\{(.*?)\}", re.DOTALL)


def strip_comments(text: str) -> str:
    return COMMENT_LINE_RE.sub("", COMMENT_BLOCK_RE.sub("", text))


def snake_case(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def upper_snake(name: str) -> str:
    return snake_case(name).upper()


def parse_struct_or_table(body: str) -> list[tuple[str, str]]:
    members: list[tuple[str, str]] = []
    for statement in body.split(";"):
        statement = statement.strip()
        if not statement:
            continue
        field = statement.split("=", 1)[0].split("(", 1)[0].strip()
        name, type_name = [part.strip() for part in field.split(":", 1)]
        members.append((name, type_name))
    return members


def parse_union(body: str) -> list[tuple[str, str]]:
    members: list[tuple[str, str]] = []
    for entry in body.split(","):
        entry = entry.strip()
        if not entry:
            continue
        members.append((snake_case(entry.split(".")[-1]), entry))
    return members


def parse_fbs_file(path: Path) -> list[Definition]:
    text = strip_comments(path.read_text())
    namespace_match = NAMESPACE_RE.search(text)
    if not namespace_match:
        raise ValueError(f"{path} is missing a namespace declaration")
    namespace = namespace_match.group(1)

    definitions: list[Definition] = []
    for kind, name, body in DEFINITION_RE.findall(text):
        if kind == "union":
            members = parse_union(body)
        else:
            members = parse_struct_or_table(body)
        definitions.append(
            Definition(kind=kind, name=name, namespace=namespace, source=path, members=members)
        )
    return definitions


def load_definitions(schema_root: Path) -> list[Definition]:
    definitions: list[Definition] = []
    for path in sorted(schema_root.rglob("*.fbs")):
        definitions.extend(parse_fbs_file(path))
    return definitions


def resolve_type(type_name: str, current: Definition, qname_map: dict[str, Definition]) -> str:
    if type_name.startswith("[") and type_name.endswith("]"):
        inner = type_name[1:-1].strip()
        if ":" in inner:
            base, length = [part.strip() for part in inner.split(":", 1)]
            return f"{resolve_type(base, current, qname_map)}[{length}]"
        return f"{resolve_type(inner, current, qname_map)}[]"

    if type_name in SCALAR_TO_ROS:
        return SCALAR_TO_ROS[type_name]

    if "." in type_name:
        qname = type_name
    else:
        qname = f"{current.namespace}.{type_name}"
        if qname not in qname_map:
            matches = [candidate for candidate in qname_map if candidate.endswith(f".{type_name}")]
            if len(matches) != 1:
                raise ValueError(f"cannot resolve type {type_name} from {current.qname}")
            qname = matches[0]

    target = qname_map[qname]
    if target.package == current.package:
        return target.name
    return f"{target.package}/{target.name}"


def render_definition(definition: Definition, qname_map: dict[str, Definition]) -> str:
    source_path = definition.source
    try:
        source_hint = source_path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        source_hint = source_path.as_posix()

    lines = [
        f"# Generated from {source_hint} by convert_fbs.py.",
        "# Do not edit by hand.",
        "",
    ]

    if definition.kind == "union":
        lines.append("uint8 NONE=0")
        for index, (_, type_name) in enumerate(definition.members, start=1):
            constant = upper_snake(type_name.split(".")[-1])
            lines.append(f"uint8 {constant}={index}")
        lines.append("uint8 type")
        for field_name, type_name in definition.members:
            lines.append(f"{resolve_type(type_name, definition, qname_map)} {field_name}")
        lines.append("")
        return "\n".join(lines)

    for field_name, type_name in definition.members:
        lines.append(f"{resolve_type(type_name, definition, qname_map)} {field_name}")
    lines.append("")
    return "\n".join(lines)


def write_messages(definitions: list[Definition], output_root: Path, clean: bool) -> None:
    qname_map = {definition.qname: definition for definition in definitions}
    packages = sorted({definition.package for definition in definitions})

    if clean:
        for package in packages:
            msg_dir = output_root / package / "msg"
            if msg_dir.exists():
                for path in msg_dir.glob("*.msg"):
                    path.unlink()

    for definition in definitions:
        msg_dir = output_root / definition.package / "msg"
        msg_dir.mkdir(parents=True, exist_ok=True)
        msg_path = msg_dir / f"{definition.name}.msg"
        msg_path.write_text(render_definition(definition, qname_map))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate minimal ROS .msg files from FlatBuffer schemas."
    )
    parser.add_argument(
        "schema_root",
        nargs="?",
        default="fbs/cerebri",
        help="directory containing the active .fbs schemas",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="msg",
        help="output root for generated ROS message packages",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="remove existing generated .msg files in affected packages before writing",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    schema_root = Path(args.schema_root).resolve()
    if not schema_root.is_dir():
        raise SystemExit(f"schema root does not exist: {schema_root}")

    definitions = load_definitions(schema_root)
    if not definitions:
        raise SystemExit(f"no .fbs files found under {schema_root}")

    write_messages(definitions, Path(args.output).resolve(), clean=args.clean)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
