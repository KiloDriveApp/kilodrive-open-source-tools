# Security policy

## Supported versions

Security fixes are applied to the latest released version. Before version 1.0, users should pin an exact version and review release notes before upgrading.

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability. Use GitHub's private vulnerability reporting feature on this repository. Include the affected command and version, reproduction steps using synthetic data, impact, and any suggested mitigation.

Do not include production credentials, private keys, access tokens, personal data, private screenshots, or proprietary schemas in a report.

Maintainers will acknowledge a complete report as soon as practical, assess severity, coordinate a correction, and publish sanitized remediation information after a fix is available.

## Security boundaries

- SchemaCert is intended for disposable databases and a restricted database account.
- StoreFrame reads only configuration-local source paths.
- DocsTruth performs deterministic local link checks and does not fetch remote content.
- ContractForge generates transport models; generated code is not an authorization boundary.
- Flutter Release Gate executes the Flutter and Dart tools available in the caller's environment.
