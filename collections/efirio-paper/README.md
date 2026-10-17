# EFIRIO Paper

Reference collection for EFIRIO Skin, built to the Alpha 0.1.0 Theme Package contract.

- Validates against `schemas/theme-package.schema.json`.
- Capability status is grounded in `schemas/capabilities.registry.json`
  (supported / unsupported / unknown) and never asserted as confirmed.

## Contents

- `package.json` — Theme Package manifest.
- `README.md` — this file.
- `placeholders/` — minimal placeholder assets (structure only; no art).

## Contract

A Theme Package is platform-agnostic data consumed by thin native runners
(iOS: SwiftUI, Android: Kotlin/Compose). This collection ships only the
data layer; runners are defined in a later milestone.
