import os
import yaml
import subprocess

DOCS_DIR = "docs"
IGNORE_DIRS = {"stylesheets", "__pycache__"}
IGNORE_FILES = {"_Sidebar.md", "index.md"}

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

def build_mkdocs_config(nav):
    with open("mkdocs.yml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    config["nav"] = [{"Home": "index.md"}] + nav

    with open("mkdocs.yml", "w", encoding="utf-8") as f:
        yaml.dump(config, f, sort_keys=False, allow_unicode=True)

    print("✅ Navigation updated in mkdocs.yml")

def git_commit_and_push():
    os.system("git add .")
    status = os.popen("git status --porcelain").read()
    if status.strip():
        os.system("git commit -m '📚 Auto-update nav and deploy to GitHub Pages'")
        os.system("git push origin main")
        print("🚀 Changes committed and pushed to GitHub.")
    else:
        print("✅ No git changes to commit.")

if __name__ == "__main__":
    print("🔍 Scanning docs folder...")
    nav = collect_docs(DOCS_DIR)
    build_mkdocs_config(nav)

    print("🚧 Deploying with mkdocs...")
    os.system("mkdocs gh-deploy")

    print("📦 Committing to GitHub...")
    git_commit_and_push()
