from google import genai
from google.genai import types
from app.core.config import settings

class AIService:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            # Use Google AI Studio Client (no GCP billing/Vertex AI setup required)
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
            self.model_name = "gemini-2.5-flash"
        else:
            # Use Vertex AI Client
            if not settings.GCP_PROJECT_ID:
                raise ValueError("GCP_PROJECT_ID or GEMINI_API_KEY must be set.")
            self.client = genai.Client(
                vertexai=True,
                project=settings.GCP_PROJECT_ID,
                location=settings.GCP_LOCATION
            )
            self.model_name = "gemini-2.5-flash"

    def _get_agent_prompt(self, agent_type: str) -> str:
        base_prompt = (
            "You are an expert AI code reviewer. Your task is to review the following Git diff "
            "and identify any issues based on your specialization. "
            "Output your findings strictly as a JSON list of objects, each containing: "
            "'file' (str), 'line' (int), 'severity' (Low/Medium/High/Critical), and 'comment' (str).\n"
            "If there are no issues, output an empty list [].\n\n"
        )
        
        prompts = {
            "security": "Focus ONLY on Security vulnerabilities (SQL injection, XSS, insecure auth, secret leakage, etc).",
            "performance": "Focus ONLY on Performance issues (blocking calls, redundant loops, inefficient DB queries).",
            "architecture": "Focus ONLY on Architecture and Maintainability (code smells, missing error handling).",
            "bug": "Focus ONLY on logical bugs and incorrect behaviors."
        }
        
        return base_prompt + prompts.get(agent_type, "Provide a general code review.")

    def review_code_chunk(self, agent_type: str, diff_content: str) -> str:
        prompt = self._get_agent_prompt(agent_type)
        final_prompt = f"{prompt}\n\nHere is the diff:\n```diff\n{diff_content}\n```"
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=final_prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json"
            )
        )
        return response.text

    def review_pull_request(self, diffs: list[tuple[str, str]]) -> str:
        """
        Processes all file diffs in a single query to Gemini.
        Returns structured JSON with issues and future enhancements.
        """
        formatted_diffs = []
        for filename, patch in diffs:
            formatted_diffs.append(f"--- File: {filename} ---\n{patch}\n")
        combined_diff = "\n".join(formatted_diffs)

        prompt = (
            "You are ReviewMind, an expert AI code reviewer. "
            "Analyze the following Git diffs thoroughly across these categories:\n\n"
            "**Issues to detect:**\n"
            "1. Security: SQL injection, XSS, insecure auth, secret leakage, SSRF, path traversal, etc.\n"
            "2. Performance: blocking calls, redundant loops, memory leaks, inefficient queries.\n"
            "3. Architecture: code smells, missing error handling, poor abstractions, maintainability.\n"
            "4. Bug: logical errors, incorrect behaviors, race conditions, edge cases.\n\n"
            "**Future Enhancements to suggest:**\n"
            "Also suggest actionable improvements that go beyond fixing issues - "
            "things like adding input validation, implementing caching, using design patterns, "
            "adding logging/monitoring, improving testability, or adopting best practices.\n\n"
            "Output your response strictly adhering to the JSON schema specified."
        )

        final_prompt = f"{prompt}\n\nHere are the diffs:\n{combined_diff}"

        # Enforce JSON output schema
        schema = {
            "type": "object",
            "properties": {
                "issues": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "file": {"type": "string"},
                            "line": {"type": "integer"},
                            "severity": {
                                "type": "string",
                                "enum": ["Low", "Medium", "High", "Critical"]
                            },
                            "category": {
                                "type": "string",
                                "enum": ["Security", "Performance", "Architecture", "Bug"]
                            },
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "suggestion": {"type": "string"}
                        },
                        "required": ["file", "line", "severity", "category", "title", "description", "suggestion"]
                    }
                },
                "enhancements": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "file": {"type": "string"},
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "priority": {
                                "type": "string",
                                "enum": ["Nice-to-have", "Recommended", "Strongly Recommended"]
                            }
                        },
                        "required": ["file", "title", "description", "priority"]
                    }
                },
                "summary": {
                    "type": "object",
                    "properties": {
                        "overall_risk": {
                            "type": "string",
                            "enum": ["Low", "Medium", "High", "Critical"]
                        },
                        "verdict": {"type": "string"}
                    },
                    "required": ["overall_risk", "verdict"]
                }
            },
            "required": ["issues", "enhancements", "summary"]
        }

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=final_prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json",
                response_schema=schema
            )
        )
        
        return response.text
