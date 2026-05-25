import json
from celery import shared_task
from app.services.github_service import GitHubService
from app.services.ai_service import AIService

@shared_task(name="app.tasks.review_tasks.process_pr_review")
def process_pr_review(repo_full_name: str, pr_number: int):
    try:
        github_service = GitHubService()
        ai_service = AIService()
        
        # 1. Fetch diffs
        diffs = github_service.get_pr_diff(repo_full_name, pr_number)
        if not diffs:
            github_service.post_summary_comment(
                repo_full_name, pr_number,
                "## ReviewMind AI Review Summary\n\nNo modified files found in this Pull Request."
            )
            return {"status": "success", "findings_count": 0}
        
        # 2. Process combined diffs in a single query
        raw_response = ai_service.review_pull_request(diffs)
        
        # Clean potential markdown wrappers
        clean_response = raw_response.strip()
        if clean_response.startswith("```"):
            lines = clean_response.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            clean_response = "\n".join(lines).strip()

        try:
            all_findings = json.loads(clean_response)
        except json.JSONDecodeError as je:
            print(f"Failed to parse JSON response from LLM: {je}")
            all_findings = []
        
        # 3. Aggregate findings and format summary
        summary_lines = [f"## ReviewMind AI Review Summary\n\nTotal issues found: {len(all_findings)}\n"]
        
        for finding in all_findings:
            file = finding.get("file")
            line = finding.get("line")
            severity = finding.get("severity", "Medium")
            comment = finding.get("comment", "")
            agent = finding.get("agent", "")
            
            summary_lines.append(f"- **{severity} ({agent})** in `{file}` (Line {line}): {comment}")

        # Post summary to PR
        summary_body = "\n".join(summary_lines)
        if not all_findings:
            summary_body = "## ReviewMind AI Review Summary\n\nGreat job! No significant issues detected."
            
        github_service.post_summary_comment(repo_full_name, pr_number, summary_body)
        
        return {"status": "success", "findings_count": len(all_findings)}
        
    except Exception as e:
        print(f"Error processing PR review: {e}")
        return {"status": "failed", "error": str(e)}
