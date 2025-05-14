# commit_ashish.py
import os
import git

REPO_PATH = os.getcwd()
POSTS_PATH = os.path.join(REPO_PATH, "_posts")

def clean_env_from_git():
    """Make sure .env is not being tracked."""
    if os.path.exists(".env"):
        try:
            os.system("git rm --cached .env > /dev/null 2>&1")
            print("🛡️  Removed .env from Git index (if it was staged)")
        except Exception as e:
            print(f"⚠️  Could not remove .env: {str(e)}")

def commit_and_push():
    try:
        repo = git.Repo(REPO_PATH)
        clean_env_from_git()
        repo.git.add(A=True)
        repo.index.commit("🚀 AI-generated post published via commit_ashish.py")
        repo.remote(name="origin").push()
        print("✅ Successfully pushed to GitHub Pages!")
    except Exception as e:
        print(f"❌ Git push failed: {str(e)}")

if __name__ == "__main__":
    commit_and_push()