import json
import hmac
import hashlib
import sys
import traceback
import threading

from fastapi import APIRouter, Request, HTTPException
from app.core.config import settings
from app.services.github_service import GitHubService
from app.services.ai_service import AIService

router = APIRouter()

# Ensure stdout can handle all characters on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def verify_signature(payload_body, secret_token, signature_header):
    if not signature_header:
        raise HTTPException(status_code=403, detail="x-hub-signature-256 header is missing!")
    
    hash_object = hmac.new(secret_token.encode('utf-8'), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    
    if not hmac.compare_digest(expected_signature, signature_header):
        raise HTTPException(status_code=403, detail="Request signatures didn't match!")


def format_review_comment(review_data: dict) -> str:
    """
    Formats the structured AI review into a polished GitHub Markdown comment.
    """
    issues = review_data.get("issues", [])
    enhancements = review_data.get("enhancements", [])
    summary = review_data.get("summary", {})
    overall_risk = summary.get("overall_risk", "Unknown")
    verdict = summary.get("verdict", "")

    # Risk level emoji/badge mapping
    risk_badges = {
        "Critical": "🔴 Critical",
        "High": "🟠 High",
        "Medium": "🟡 Medium",
        "Low": "🟢 Low",
        "Unknown": "⚪ Unknown"
    }

    severity_icons = {
        "Critical": "🔴",
        "High": "🟠",
        "Medium": "🟡",
        "Low": "🟢"
    }

    category_icons = {
        "Security": "🔒",
        "Performance": "⚡",
        "Architecture": "🏗️",
        "Bug": "🐛"
    }

    # ── Header ──
    lines = []
    lines.append("# 🤖 ReviewMind AI Code Review")
    lines.append("")
    lines.append(f"> **Overall Risk Level:** {risk_badges.get(overall_risk, overall_risk)}")
    lines.append(f"> **Verdict:** {verdict}")
    lines.append("")

    # ── Summary Stats ──
    if issues:
        severity_counts = {}
        category_counts = {}
        for issue in issues:
            sev = issue.get("severity", "Medium")
            cat = issue.get("category", "General")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
            category_counts[cat] = category_counts.get(cat, 0) + 1

        lines.append("---")
        lines.append("")
        lines.append("## 📊 Summary")
        lines.append("")
        lines.append(f"**Total Issues Found:** {len(issues)}")
        lines.append("")

        # Severity breakdown in a single line
        sev_parts = []
        for sev in ["Critical", "High", "Medium", "Low"]:
            count = severity_counts.get(sev, 0)
            if count > 0:
                sev_parts.append(f"{severity_icons[sev]} {sev}: **{count}**")
        lines.append(" | ".join(sev_parts))
        lines.append("")

        # ── Issues Table ──
        lines.append("---")
        lines.append("")
        lines.append("## 🔍 Issues Found")
        lines.append("")
        lines.append("| # | Severity | Category | File | Line | Issue |")
        lines.append("|---|----------|----------|------|------|-------|")

        for idx, issue in enumerate(issues, 1):
            sev = issue.get("severity", "Medium")
            cat = issue.get("category", "General")
            file = issue.get("file", "")
            line_num = issue.get("line", "")
            title = issue.get("title", "")
            sev_display = f"{severity_icons.get(sev, '')} {sev}"
            cat_display = f"{category_icons.get(cat, '')} {cat}"
            lines.append(f"| {idx} | {sev_display} | {cat_display} | `{file}` | {line_num} | {title} |")

        lines.append("")

        # ── Future Enhancements (moved above major bugs) ──
        if enhancements:
            priority_icons = {
                "Strongly Recommended": "🔵",
                "Recommended": "🟣",
                "Nice-to-have": "⚪"
            }

            lines.append("---")
            lines.append("")
            lines.append("## 🚀 Future Enhancements")
            lines.append("")
            lines.append("| # | Priority | File | Enhancement | Description |")
            lines.append("|---|----------|------|-------------|-------------|")

            for idx, enh in enumerate(enhancements, 1):
                priority = enh.get("priority", "Nice-to-have")
                file = enh.get("file", "")
                title = enh.get("title", "")
                desc = enh.get("description", "")
                icon = priority_icons.get(priority, "")
                lines.append(f"| {idx} | {icon} {priority} | `{file}` | {title} | {desc} |")

            lines.append("")

        # ── Major Bugs & How to Fix Them (Critical + High only) ──
        major_issues = [i for i in issues if i.get("severity") in ["Critical", "High"]]
        if major_issues:
            lines.append("---")
            lines.append("")
            lines.append("## 🛠️ Major Bugs & How to Fix Them")
            lines.append("")

            for idx, issue in enumerate(major_issues, 1):
                sev = issue.get("severity", "High")
                cat = issue.get("category", "General")
                file = issue.get("file", "")
                line_num = issue.get("line", "")
                title = issue.get("title", "")
                desc = issue.get("description", "")
                suggestion = issue.get("suggestion", "")

                lines.append(f"### {idx}. {severity_icons.get(sev, '')} {title}")
                lines.append(f"**File:** `{file}` | **Line:** {line_num} | **Category:** {category_icons.get(cat, '')} {cat}")
                lines.append("")
                lines.append(f"> {desc}")
                lines.append("")
                if suggestion:
                    lines.append(f"**💡 Fix:** {suggestion}")
                    lines.append("")

    else:
        lines.append("---")
        lines.append("")
        lines.append("## ✅ No Issues Found")
        lines.append("")
        lines.append("Great job! No significant issues were detected in this Pull Request.")
        lines.append("")

        # Still show enhancements even if no issues
        if enhancements:
            priority_icons = {
                "Strongly Recommended": "🔵",
                "Recommended": "🟣",
                "Nice-to-have": "⚪"
            }

            lines.append("---")
            lines.append("")
            lines.append("## 🚀 Future Enhancements")
            lines.append("")
            lines.append("| # | Priority | File | Enhancement | Description |")
            lines.append("|---|----------|------|-------------|-------------|")

            for idx, enh in enumerate(enhancements, 1):
                priority = enh.get("priority", "Nice-to-have")
                file = enh.get("file", "")
                title = enh.get("title", "")
                desc = enh.get("description", "")
                icon = priority_icons.get(priority, "")
                lines.append(f"| {idx} | {icon} {priority} | `{file}` | {title} | {desc} |")

            lines.append("")

    # ── Footer ──
    lines.append("---")
    lines.append("")
    lines.append("<sub>Powered by <b>ReviewMind AI</b> | Automated code review using Gemini</sub>")

    return "\n".join(lines)


def run_review(repo_full_name: str, pr_number: int):
    """
    Runs the full AI review pipeline directly:
    1. Fetch PR diff from GitHub
    2. Send to Gemini for analysis
    3. Format and post review comment back to the PR
    """
    print(f"[Review] Starting review for {repo_full_name} PR#{pr_number}", flush=True)
    try:
        github_service = GitHubService()
        ai_service = AIService()

        # 1. Fetch diffs
        diffs = github_service.get_pr_diff(repo_full_name, pr_number)
        if not diffs:
            github_service.post_summary_comment(
                repo_full_name, pr_number,
                "# 🤖 ReviewMind AI Code Review\n\n> No modified files found in this Pull Request.\n\n---\n<sub>Powered by <b>ReviewMind AI</b></sub>"
            )
            print(f"[Review] No diffs found for {repo_full_name} PR#{pr_number}", flush=True)
            return

        print(f"[Review] Found {len(diffs)} file(s) with changes. Sending to Gemini...", flush=True)

        # 2. Send to Gemini AI for review
        raw_response = ai_service.review_pull_request(diffs)

        # Clean potential markdown wrappers
        clean_response = raw_response.strip()
        if clean_response.startswith("```"):
            resp_lines = clean_response.splitlines()
            if resp_lines[0].startswith("```"):
                resp_lines = resp_lines[1:]
            if resp_lines and resp_lines[-1].startswith("```"):
                resp_lines = resp_lines[:-1]
            clean_response = "\n".join(resp_lines).strip()

        try:
            review_data = json.loads(clean_response)
        except json.JSONDecodeError as je:
            print(f"[Review] Failed to parse JSON from Gemini: {je}", flush=True)
            print(f"[Review] Raw response: {clean_response[:500]}", flush=True)
            review_data = {"issues": [], "enhancements": [], "summary": {"overall_risk": "Unknown", "verdict": "Could not parse AI response."}}

        # 3. Format and post the review comment
        comment_body = format_review_comment(review_data)
        github_service.post_summary_comment(repo_full_name, pr_number, comment_body)

        issue_count = len(review_data.get("issues", []))
        enh_count = len(review_data.get("enhancements", []))
        print(f"[Review] SUCCESS - Posted review ({issue_count} issues, {enh_count} enhancements) to {repo_full_name} PR#{pr_number}", flush=True)

    except Exception as e:
        print(f"[Review] FAILED - Error reviewing {repo_full_name} PR#{pr_number}: {e}", flush=True)
        traceback.print_exc()


@router.post("")
async def github_webhook(request: Request):
    # Verify GitHub Webhook signature
    signature = request.headers.get("x-hub-signature-256")
    body = await request.body()
    
    if settings.GITHUB_WEBHOOK_SECRET:
        verify_signature(body, settings.GITHUB_WEBHOOK_SECRET, signature)
        
    payload = await request.json()
    
    # We only care about pull request opened, synchronize, or reopened events
    if "pull_request" in payload and payload.get("action") in ["opened", "synchronize", "reopened"]:
        pr_number = payload["pull_request"]["number"]
        repo_full_name = payload["repository"]["full_name"]
        
        # Run review in a separate thread — fully independent of request lifecycle
        print(f"[Webhook] Received PR event for {repo_full_name} PR#{pr_number} (action={payload['action']})", flush=True)
        thread = threading.Thread(target=run_review, args=(repo_full_name, pr_number), daemon=True)
        thread.start()
        return {"status": "Review started"}
        
    return {"status": "Event ignored"}
