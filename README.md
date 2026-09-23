# KiloDrive DevTools

KiloDrive DevTools is a small, brand-neutral toolkit extracted from production engineering work on KiloDrive. It helps mobile teams create store artwork, validate Flutter releases, generate Dart wire models, certify MySQL scripts in disposable databases, and keep documentation honest.

The project is MIT licensed. It contains no KiloDrive credentials, private screenshots, production endpoints, or proprietary database definitions.

## Tools

### StoreFrame

Creates deterministic App Store or Google Play marketing images from real application screenshots. It provides gradient backgrounds, headings, a generic device frame, opaque PNG output, accessibility alt text, and a SHA-256 manifest.

```bash
python examples/make_fixture.py
kd-devtools storeframe examples/storeframe.json
```

The JSON configuration controls canvas size, colors, frame dimensions, source screenshots, copy, and output location. StoreFrame never edits its source images.

### Flutter Release Gate

Runs the checks that most often differ between a developer workstation and hosted Flutter CI:

```powershell
./flutter-release-gate.ps1 -Project ../../src/client/mobile
```

It restores packages, regenerates localization, verifies formatting, runs the analyzer, and executes non-platform-golden tests. Any failing command stops the gate with a nonzero exit.

### ContractForge Dart

Generates dependency-free Dart wire models from `components.schemas` in an OpenAPI 3 document:

```bash
kd-devtools contractforge examples/openapi.json generated/api_models.dart
```

The initial release supports object schemas, required and nullable fields, references, arrays, strings, booleans, integers, and numbers. Domain adapters and business rules should remain hand-written.

### SchemaCert MySQL

Applies SQL scripts to a uniquely named disposable MySQL database, runs assertions, and drops the database even when certification fails:

```powershell
$env:MYSQL_CERT_PASSWORD = 'local-test-password'
kd-devtools schemacert schema.sql --check "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE()"
```

Passwords are accepted only through an environment variable and are passed to the MySQL client through `MYSQL_PWD`; they are never placed on the command line. Use a restricted local or CI account that can create and drop only disposable databases.

### DocsTruth

Checks required documentation, local Markdown links, and project-defined prohibited claims:

```bash
kd-devtools docstruth examples/docstruth.json
```

It deliberately skips network link checking, making results deterministic and suitable for offline CI.

## Installation

```bash
python -m venv .venv
python -m pip install -e .
kd-devtools --help
```

Python 3.11 or newer is required. StoreFrame uses Pillow; the other Python commands use the standard library. Flutter Release Gate additionally requires PowerShell, Flutter, and Dart. SchemaCert requires the MySQL command-line client.

## Development

```bash
python -m unittest discover -s tests -v
python -m compileall -q src tests
python examples/make_fixture.py
kd-devtools storeframe examples/storeframe.json
```

The tests do not require Flutter, MySQL, or network access. Live SchemaCert and Flutter checks should run in an explicitly provisioned CI job.

## Security model

- Configuration paths are confined beneath the configuration directory.
- SchemaCert generates and validates its own database name before deletion.
- Database passwords come from an environment variable.
- Provider keys, signing keys, app screenshots, and production URLs do not belong in this repository.
- Generated Dart models are transport objects, not authorization or validation policy.

## Release status

`0.1.0` is an initial public release. APIs may evolve before `1.0.0`; pin exact versions in automation.

## Contributing

Issues and pull requests are welcome. Include focused tests and avoid introducing product-specific assets or credentials. See [CONTRIBUTING.md](CONTRIBUTING.md).
