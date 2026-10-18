import json
import os
import urllib.request
from datetime import datetime, timezone

USERNAME = "koolkap"
README_FILE = "README.md"

START = "<!-- ACTIVITY_START -->"
END = "<!-- ACTIVITY_END -->"


def get_recent_activity():
    url = (
        f"https://api.github.com/users/{USERNAME}/events/public"
        "?per_page=100"
    )

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "GitHub-Profile-Updater",
        },
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def format_activity(events):
    lines = []

    for event in events:
        event_type = event.get("type", "")
        repo = event.get("repo", {}).get("name", "")
        payload = event.get("payload", {})
        created_at = event.get("created_at", "")

        if not repo:
            continue

        if event_type == "PushEvent":
            commits = payload.get("commits", [])
            count = payload.get("size", len(commits))
            message = f"Pushed {count} commit(s)"

            if commits:
                commit_message = (
                    commits[-1].get("message", "")
                    .splitlines()[0]
                )
                if commit_message:
                    message += f": {commit_message}"

        elif event_type == "CreateEvent":
            message = "Created a branch, tag, or repository"

        elif event_type == "PullRequestEvent":
            action = payload.get("action", "updated")
            message = f"Pull request {action}"

        elif event_type == "IssuesEvent":
            action = payload.get("action", "updated")
            message = f"Issue {action}"

        elif event_type == "ReleaseEvent":
            message = "Published a release"

        else:
            continue

        date = created_at[:10] if created_at else "Recently"
        repo_url = f"https://github.com/{repo}"

        lines.append(
            f"- **{date}** — {message} in "
            f"[`{repo}`]({repo_url})"
        )

        if len(lines) >= 10:
            break

    if not lines:
        lines.append("No recent public coding activity found.")

    return "\n".join(lines)


def main():
    with open(README_FILE, "r", encoding="utf-8") as file:
        readme = file.read()

    if START not in readme or END not in readme:
        raise ValueError(
            "README.md must contain ACTIVITY_START and ACTIVITY_END markers."
        )

    events = get_recent_activity()
    activity = format_activity(events)

    updated_section = f"{START}\n{activity}\n{END}"

    start_index = readme.index(START)
    end_index = readme.index(END) + len(END)

    updated_readme = (
        readme[:start_index]
        + updated_section
        + readme[end_index:]
    )

    if updated_readme != readme:
        with open(README_FILE, "w", encoding="utf-8") as file:
            file.write(updated_readme)

        print("Profile README updated.")
    else:
        print("No profile changes needed.")


if __name__ == "__main__":
    main()