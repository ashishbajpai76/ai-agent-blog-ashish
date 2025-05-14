# commit_ashish.py
import os
import git
import re

REPO_PATH = os.getcwd()

def get_repo_info():
    """Extract GitHub username and repo name from Git config."""
    repo = git.Repo(REPO_PATH)
    origin_url = repo.remotes.origin.url

    # Handle both HTTPS and SSH GitHub URLs
    match = re.search(r'github\.com[:/](.*?)/(.*?)(\.git)?$', origin_url)
    if not match:
        raise ValueError("❌ Could not parse GitHub origin URL")

    username, repo_name = match.group(1), match.group(2)
    return username, repo_name

def clean_env_from_git():
    if os.path.exists(".env"):
        os.system("git rm --cached .env > /dev/null 2>&1")
        print("🛡️  Removed .env from Git index (if it was staged)")

def clean_venv_from_git():
    if os.path.isdir("venv"):
        os.system("git rm -r --cached venv > /dev/null 2>&1")
        print("🧹 Removed venv/ from Git index (virtual environment)")

def commit_and_push():
    try:
        repo = git.Repo(REPO_PATH)
        clean_env_from_git()
        clean_venv_from_git()

        repo.git.add(A=True)
        repo.index.commit("🚀 AI-generated post published via commit_ashish.py")
        repo.remote(name="origin").push()
        print("✅ Successfully pushed to GitHub Pages!")

        username, repo_name = get_repo_info()
        blog_url = f"https://{username}.github.io/{repo_name}/"
        print(f"\n🌐 View your blog at: {blog_url}")

    except Exception as e:
        print(f"❌ Git push failed: {str(e)}")

if __name__ == "__main__":
    commit_and_push()