from github import Github
import base64
import os
import sys

print(os.getcwd())
# --- Configuration ---
GITHUB_TOKEN = sys.argv[1]  # Your GitHub PAT
REPO_NAME = "fahadk/gh-issue-template-poc" # Format: username/repo
LOCAL_FILE_PATH = "gh-issue-template-poc/issue_template.md" 
REPO_FILE_PATH = "gh-issue-template-poc/issue_template.md" 
BRANCH = "new"
COMMIT_MESSAGE = "This is commit message"

# --- Authenticate with GitHub ---
git = Github(GITHUB_TOKEN)
repo = git.get_repo(REPO_NAME)

# --- Read local file content ---
with open(LOCAL_FILE_PATH, 'rb') as f:
    local_content = f.read()

# --- Fetch current content and SHA from GitHub ---
try:
    repo_file = repo.get_contents(REPO_FILE_PATH, ref=BRANCH)
    remote_content = base64.b64decode(repo_file.content)

    if remote_content == local_content:
        print("No changes — local and remote file are identical.")
    else:
        print("Changes detected — committing new content.")

        # Commit the new content
        repo.update_file(
            path=REPO_FILE_PATH,
            message=COMMIT_MESSAGE,
            content=local_content,
            sha=repo_file.sha,
            branch=BRANCH
        )
        print(f"Committed changes to `{REPO_FILE_PATH}` on branch `{BRANCH}`.")

except Exception as e:
    # File might not exist — create it
    print(f"ℹ️ File not found on GitHub. Creating it.")
    repo.create_file(
        path=REPO_FILE_PATH,
        message=COMMIT_MESSAGE,
        content=local_content,
        branch=BRANCH
    )
    print(f"Created and committed `{REPO_FILE_PATH}` to `{BRANCH}`.")

# print("This is a test script to check the signed commit feature of GitHub API.")