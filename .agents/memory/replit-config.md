---
name: Validated Replit config
description: How this workspace handles protected .replit configuration changes.
---

Changes to `.replit` must be made by writing the complete intended TOML to a temporary file and passing it through the workspace's schema-validation replacement flow. Direct edits are rejected.

**Why:** The project editor protects `.replit` and normal file edits fail, while workflow configuration can also add managed workflow blocks to the file.

**How to apply:** Preserve existing configuration, include the full final TOML in the temporary file, validate and replace it, then inspect the resulting `.replit` before finishing.