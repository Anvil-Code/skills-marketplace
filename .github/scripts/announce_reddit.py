"""
announce_reddit.py
Runs on every GitHub release. Posts to target subreddits automatically.
Requires: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD
as GitHub Actions secrets.
"""

import os
import praw
import sys
import time

# ── Config ─────────────────────────────────────────────────────────────────
SUBREDDITS = [
    {
        "name": "ClaudeAI",
        "flair": None,
        "post_type": "link",          # link post with URL
    },
    {
        "name": "ChatGPTPromptEngineering",
        "flair": None,
        "post_type": "link",
    },
    {
        "name": "SideProject",
        "flair": None,
        "post_type": "self",          # text post — SideProject prefers self posts
    },
]

GUMROAD_URL = "https://gumroad.com/anvilandcode"
GITHUB_URL  = "https://github.com/anvilandcode/skills-marketplace"

# ── Helpers ─────────────────────────────────────────────────────────────────
def build_title(release_name: str, release_tag: str) -> str:
    """Build a title that doesn't read like an ad."""
    return f"[Anvil & Code] {release_name} — production-grade Claude skill for builders"


def build_self_text(release_name: str, release_body: str, release_url: str) -> str:
    """Build the post body for self posts."""
    return f"""Just shipped: **{release_name}**

{release_body}

---

**Free skills** (install instantly):
- `skill-validator` — audit any SKILL.md, scored report with exact fixes
- `description-optimizer` — rewrite description fields for max trigger reliability

Install the full catalog in Claude Code:
```
/plugin marketplace add https://github.com/anvilandcode/skills-marketplace
```

**Engineer's Edition** (all 12 skills): {GUMROAD_URL}

GitHub: {GITHUB_URL}

---
*Anvil & Code — build once, ship reliably.*
"""


def post_to_subreddit(reddit, sub_config: dict, title: str, release_url: str,
                       release_name: str, release_body: str) -> None:
    subreddit = reddit.subreddit(sub_config["name"])

    try:
        if sub_config["post_type"] == "link":
            submission = subreddit.submit(
                title=title,
                url=release_url,
                flair_id=sub_config.get("flair"),
            )
        else:
            submission = subreddit.submit(
                title=title,
                selftext=build_self_text(release_name, release_body, release_url),
                flair_id=sub_config.get("flair"),
            )
        print(f"✅ Posted to r/{sub_config['name']}: {submission.url}")
    except Exception as e:
        # Don't fail the entire workflow for one subreddit
        print(f"⚠️  Failed to post to r/{sub_config['name']}: {e}", file=sys.stderr)


# ── Main ────────────────────────────────────────────────────────────────────
def main():
    # Pull from environment (set as GitHub Actions secrets)
    client_id     = os.environ["REDDIT_CLIENT_ID"]
    client_secret = os.environ["REDDIT_CLIENT_SECRET"]
    username      = os.environ["REDDIT_USERNAME"]
    password      = os.environ["REDDIT_PASSWORD"]
    release_tag   = os.environ.get("RELEASE_TAG", "v1.0")
    release_name  = os.environ.get("RELEASE_NAME", "New Skill Release")
    release_body  = os.environ.get("RELEASE_BODY", "")
    release_url   = os.environ.get("RELEASE_URL", GUMROAD_URL)

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        username=username,
        password=password,
        user_agent=f"AnvilAndCode/1.0 release-announcer (by u/{username})",
    )

    title = build_title(release_name, release_tag)

    for sub_config in SUBREDDITS:
        post_to_subreddit(
            reddit=reddit,
            sub_config=sub_config,
            title=title,
            release_url=release_url,
            release_name=release_name,
            release_body=release_body,
        )
        time.sleep(2)   # brief pause between posts — Reddit rate limiting

    print("Done.")


if __name__ == "__main__":
    main()
