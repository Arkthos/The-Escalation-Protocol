import os
import yaml

DOCS_DIR = "docs"
IGNORE_DIRS = {"stylesheets", "__pycache__","images"}
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

if __name__ == "__main__":
    nav = collect_docs(DOCS_DIR)
    build_mkdocs_config(nav)
    os.system("mkdocs build")
    os.system("git add .")
    os.system('git commit -m "Auto-update nav and build site"')
    os.system("git push origin main")
