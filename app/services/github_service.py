from github import Github
from app.core.config import settings

class GitHubService:
    def __init__(self):
        # We will use PAT for simplicity in the MVP.
        if not settings.GITHUB_PAT:
            raise ValueError("GITHUB_PAT is not set.")
        self.g = Github(settings.GITHUB_PAT)

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
