from github import Github, Auth
from app.core.config import settings
from app.services.github_app_auth import get_installation_token, is_github_app_configured


class GitHubService:
    def __init__(self, installation_id: int = None):
        """
        Initialize GitHub client.
        
        Priority:
        1. If installation_id provided and GitHub App configured → use App token
        2. Else if GITHUB_PAT is set → use PAT (local dev / self-hosted)
        3. Else → raise error
        """
        if installation_id and is_github_app_configured():
            # GitHub App mode — generate token for this installation
            token = get_installation_token(installation_id)
            self.g = Github(auth=Auth.Token(token))
            self.mode = "github_app"
        elif settings.GITHUB_PAT:
            # PAT mode — for local dev or self-hosted
            self.g = Github(auth=Auth.Token(settings.GITHUB_PAT))
            self.mode = "pat"
        else:
            raise ValueError("Either GITHUB_PAT or GitHub App credentials must be configured.")

    def get_pr_diff(self, repo_full_name: str, pr_number: int) -> list[tuple[str, str]]:
        """
        Fetches the diff for a pull request.
        Returns a list of tuples: (filename, diff_content)
        """
        repo = self.g.get_repo(repo_full_name)
        pr = repo.get_pull(pr_number)
        
        files = pr.get_files()
        
        diffs = []
        for file in files:
            if file.patch:
                diffs.append((file.filename, file.patch))
                
        return diffs
        
    def post_inline_comment(self, repo_full_name: str, pr_number: int, commit_id: str, path: str, position: int, body: str):
        repo = self.g.get_repo(repo_full_name)
        pr = repo.get_pull(pr_number)
        
        pr.create_review_comment(body, commit_id, path, position)
        
    def post_summary_comment(self, repo_full_name: str, pr_number: int, body: str):
        repo = self.g.get_repo(repo_full_name)
        pr = repo.get_pull(pr_number)
        
        pr.create_issue_comment(body)
