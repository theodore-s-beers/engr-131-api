from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from . import models, schemas
from .live_scorer import Score


def add_scoring_submission(
    db: Session,
    submission: schemas.ScoringSubmission,
    score: Score,
):
    assignment_title = f"{submission.term}_{submission.assignment}"

    db_assignment = (
        db.query(models.Assignment)
        .filter(models.Assignment.title == assignment_title)
        .first()
    )
    if not db_assignment:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Assignment not found in database",
        )

    db_submission = models.ScoringSubmission(
        student_email=submission.student_email,
        assignment=assignment_title,
        question=submission.question,
        max_points=score.max_points,
        points_earned=score.points_earned,
    )

    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)

    return db_submission
