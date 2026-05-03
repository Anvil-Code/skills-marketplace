"""
update_marketplace.py
Runs on every GitHub release. Bumps the version field in marketplace.json
so SkillsMP and other scrapers pick up the change.
Requires: GH_TOKEN as GitHub Actions secret.
"""

import json
import os
import subprocess
from datetime import datetime, timezone


MARKETPLACE_FILE = "marketplace.json"


def main():
    # Load current marketplace.json
    with open(MARKETPLACE_FILE, "r") as f:
        catalog = json.load(f)

    # Bump last_updated timestamp
    catalog["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    catalog["version"] = os.environ.get("RELEASE_TAG", catalog.get("version", "1.0.0"))

    # Write back
    with open(MARKETPLACE_FILE, "w") as f:
        json.dump(catalog, f, indent=2)
        f.write("\n")

    print(f"✅ Updated marketplace.json: version={catalog['version']}, "
          f"last_updated={catalog['last_updated']}")

    # Commit and push
    subprocess.run(["git", "config", "user.name",  "github-actions[bot]"], check=True)
    subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"], check=True)
    subprocess.run(["git", "add", MARKETPLACE_FILE], check=True)

    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        capture_output=True
    )

    if result.returncode != 0:
        subprocess.run(
            ["git", "commit", "-m", f"chore: bump marketplace version {catalog['version']}"],
            check=True
        )
        subprocess.run(
            ["git", "push", f"https://x-access-token:{os.environ['GH_TOKEN']}@github.com/anvilandcode/skills-marketplace.git"],
            check=True
        )
        print("✅ Committed and pushed marketplace.json")
    else:
        print("ℹ️  No changes to commit.")


if __name__ == "__main__":
    main()
