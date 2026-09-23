from __future__ import annotations

import os
import re
import subprocess
import uuid
from pathlib import Path


SAFE_PREFIX = re.compile(r"^[A-Za-z][A-Za-z0-9_]{2,30}$")


def certify(*, mysql: str, host: str, port: int, user: str, password_env: str,
            scripts: list[Path], checks: list[str], prefix: str) -> str:
    if not SAFE_PREFIX.fullmatch(prefix):
        raise ValueError("Database prefix must be 3-31 alphanumeric/underscore characters and start with a letter")
    password = os.environ.get(password_env)
    if not password:
        raise ValueError(f"Required password environment variable {password_env!r} is not set")
    database = f"{prefix}_{uuid.uuid4().hex[:12]}"
    environment = os.environ.copy()
    environment["MYSQL_PWD"] = password
    base = [mysql, "--protocol=tcp", f"--host={host}", f"--port={port}", f"--user={user}", "--batch"]

    def run(sql: bytes, selected_database: bool = False) -> None:
        command = base + ([database] if selected_database else [])
        result = subprocess.run(command, input=sql, env=environment, capture_output=True, check=False)
        if result.returncode:
            raise RuntimeError(result.stderr.decode("utf-8", errors="replace").strip())

    run(f"CREATE DATABASE `{database}`;".encode())
    try:
        for script in scripts:
            run(script.read_bytes(), selected_database=True)
        for check in checks:
            run((check.rstrip("; ") + ";").encode(), selected_database=True)
        return database
    finally:
        run(f"DROP DATABASE IF EXISTS `{database}`;".encode())
