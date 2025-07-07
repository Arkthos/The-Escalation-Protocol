import os
import yaml
import subprocess

DOCS_DIR = "docs"
IGNORE_DIRS = {"stylesheets", "__pycache__", "images"}
IGNORE_FILES = {"_Sidebar.md", "index.md"}

# Priority nav order (custom)
PRIORITY_ORDER = [
    "Defender for Endpoint",
    "Support Tips and Tools",
    "Derecho informático"
]

def collect_docs(path):
    tree = []
    entries = sorted(os.listdir(path), key=str.casefold)

    for entry in entries:
        full_path = os.path.join(path, entry)
        if os.path.isdir(full_path) and entry not in IGNORE_DIRS:
            children = collect_docs(full_path)
            if children:
                tree.append({entry: children})
        elif entry.endswith(".md") and entry not in IGNORE_FILES:
            rel_path = os.path.relpath(full_path, DOCS_DIR).replace("\\", "/")
            label = os.path.splitext(entry)[0].replace("-", " ").replace("_", " ").title()
            tree.append({label: rel_path})
    return tree

def sort_nav(nav):
    prioritized = []
    remaining = []

    for item in nav:
        section = list(item.keys())[0]
        if section in PRIORITY_ORDER:
            prioritized.append((PRIORITY_ORDER.index(section), item))
        else:
            remaining.append(item)

    prioritized.sort(key=lambda x: x[0])
    remaining.sort(key=lambda x: list(x.keys())[0].lower())
    return [i[1] for i in prioritized] + remaining

def build_mkdocs_config(nav):
    config_path = "mkdocs.yml"

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    new_nav = [{"Home": "index.md"}] + sort_nav(nav)
    config["nav"] = new_nav

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, sort_keys=False, allow_unicode=True)

    print("✅ mkdocs.yml navigation updated.")

def git_commit_and_push():
    # Check if anything changed
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if result.stdout.strip() == "":
        print("⚠️  No changes to commit.")
        return

    print("📦 Committing and pushing changes...")
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Auto-update: nav, content, or metadata"], check=False)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("✅ Changes pushed to main. GitHub Pages will redeploy shortly.")

if __name__ == "__main__":
    print("📁 Collecting docs and rebuilding nav...")
    nav = collect_docs(DOCS_DIR)

    build_mkdocs_config(nav)
    git_commit_and_push()