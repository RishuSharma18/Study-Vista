import pandas as pd
from db.session import SessionLocal
from db.models import StudyLog


def get_user_logs(user_id):
    """Fetch all study logs for a user, returning a DataFrame with log IDs."""
    session = SessionLocal()
    try:
        logs = session.query(StudyLog).filter_by(user_id=user_id).all()
        data = [
            {
                "id": log.id,
                "date": log.date,
                "subject": log.subject,
                "study_hours": log.study_hours,
                "focus_level": log.focus_level,
                "notes": log.notes or "",
            }
            for log in logs
        ]
        return pd.DataFrame(data)
    finally:
        session.close()


def delete_study_log(log_id):
    """Delete a study log by ID."""
    session = SessionLocal()
    try:
        log = session.query(StudyLog).filter_by(id=log_id).first()
        if log:
            session.delete(log)
            session.commit()
            return True
        return False
    finally:
        session.close()


def update_study_log(log_id, date=None, subject=None, study_hours=None, focus_level=None, notes=None):
    """Update an existing study log."""
    session = SessionLocal()
    try:
        log = session.query(StudyLog).filter_by(id=log_id).first()
        if not log:
            return False
        if date is not None:
            log.date = date
        if subject is not None:
            log.subject = subject
        if study_hours is not None:
            log.study_hours = study_hours
        if focus_level is not None:
            log.focus_level = focus_level
        if notes is not None:
            log.notes = notes
        session.commit()
        return True
    finally:
        session.close()
