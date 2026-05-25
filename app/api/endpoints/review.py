from fastapi import APIRouter

router = APIRouter()

@router.post("/start")
def trigger_manual_review(repo: str, pr_number: int):
    from app.tasks.review_tasks import process_pr_review
    process_pr_review.delay(repo, pr_number)
    return {"status": "Review task queued"}
    
@router.get("/status/{id}")
def get_review_status(id: str):
    return {"status": "pending", "task_id": id}
