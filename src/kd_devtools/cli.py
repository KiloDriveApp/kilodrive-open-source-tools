from __future__ import annotations

import argparse
from pathlib import Path

from . import contractforge, docstruth, schemacert, storeframe


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="kd-devtools")
    commands = root.add_subparsers(dest="command", required=True)
    frame = commands.add_parser("storeframe", help="Generate store-listing artwork")
    frame.add_argument("config", type=Path)
    contract = commands.add_parser("contractforge", help="Generate Dart models from OpenAPI")
    contract.add_argument("openapi", type=Path)
    contract.add_argument("output", type=Path)
    docs = commands.add_parser("docstruth", help="Validate documentation policy and local links")
    docs.add_argument("config", type=Path)
    schema = commands.add_parser("schemacert", help="Apply and verify SQL in a disposable MySQL database")
    schema.add_argument("scripts", nargs="+", type=Path)
    schema.add_argument("--check", action="append", default=["SELECT 1"])
    schema.add_argument("--mysql", default="mysql")
    schema.add_argument("--host", default="127.0.0.1")
    schema.add_argument("--port", type=int, default=3306)
    schema.add_argument("--user", default="root")
    schema.add_argument("--password-env", default="MYSQL_CERT_PASSWORD")
    schema.add_argument("--prefix", default="schemacert")
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "storeframe":
        outputs = storeframe.generate(args.config)
        print(f"Generated {len(outputs)} asset(s)")
    elif args.command == "contractforge":
        contractforge.generate(args.openapi, args.output)
        print(f"Generated {args.output}")
    elif args.command == "docstruth":
        errors = docstruth.validate(args.config)
        for error in errors:
            print(f"ERROR: {error}")
        return 1 if errors else 0
    elif args.command == "schemacert":
        name = schemacert.certify(mysql=args.mysql, host=args.host, port=args.port, user=args.user,
                                  password_env=args.password_env, scripts=args.scripts,
                                  checks=args.check, prefix=args.prefix)
        print(f"Certified and removed disposable database {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
