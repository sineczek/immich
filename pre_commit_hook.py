# It’s a Git pre-commit hook that scans Docker Compose files for hardcoded sensitive values like 
# passwords or API keys and prevents commits if any are found. 
# It ensures that secrets are kept in environment variables or .env files, helping maintain 
# secure configuration practices.

#!/usr/bin/env python3
import os
import sys
import re

SENSITIVE_KEYWORDS = ("PASSWORD", "PASS", "SECRET", "TOKEN", "KEY", "API_KEY")

violations = []

env_line = re.compile(
    r"^\s*(?:-?\s*)([A-Za-z0-9_]+)\s*[:=]\s*(.+)$",
    re.IGNORECASE,
)

for root, _, files in os.walk("."):
    for file in files:
        if not re.match(r"docker-compose.*\.ya?ml$", file, re.IGNORECASE):
            continue
        path = os.path.join(root, file)
        with open(path, "r") as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                m = env_line.match(line)
                if not m:
                    continue
                key, value = m.groups()
                key = key.strip()
                value = value.strip()

                if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1].strip()

                if value.startswith("${") or (value.startswith("/") and "passwd" in value.lower()):
                    continue

                if any(word.upper() in key.upper() for word in SENSITIVE_KEYWORDS):
                    if not key.lower().endswith("_configuration"):
                        violations.append(f"{path}:{i}: {key}={value}")

if violations:
    print("❌ Commit blocked: Hardcoded sensitive values found in docker-compose.yaml:")
    for v in violations:
        print(v)
    sys.exit(1)
else:
    print("✅ docker-compose.yaml files are clean. Safe to commit.")
