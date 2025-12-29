"""
Utility module to easily access admin emails for use in other endpoints.
"""
from sqlalchemy.orm import Session
from app.database.models import Admin


def get_admin_emails(db: Session) -> dict:
    """
    Get admin emails for use in email sending processes.
    
    Args:
        db: Database session
        
    Returns:
        dict: Dictionary with 'email' and 'email2' fields (can be None)
        
    Example:
        ```python
        from app.utils.admin_emails import get_admin_emails
        
        @router.post("/some-endpoint")
        def some_endpoint(db: Session = Depends(get_db)):
            emails = get_admin_emails(db)
            primary_email = emails['email']
            secondary_email = emails['email2']
            # Use emails for sending notifications
        ```
    """
    admin = db.query(Admin).first()
    if admin is None:
        return {"email": None, "email2": None}
    return {
        "email": admin.email,
        "email2": admin.email2
    }


def get_admin_email_list(db: Session) -> list:
    """
    Get admin emails as a list (excluding None values).
    Useful for sending emails to multiple recipients.
    
    Args:
        db: Database session
        
    Returns:
        list: List of email addresses (excluding None values)
        
    Example:
        ```python
        from app.utils.admin_emails import get_admin_email_list
        
        emails = get_admin_email_list(db)
        # emails = ['admin@example.com', 'admin2@example.com']
        # Use for CC or BCC recipients
        ```
    """
    admin = db.query(Admin).first()
    if admin is None:
        return []
    
    emails = []
    if admin.email:
        emails.append(admin.email)
    if admin.email2:
        emails.append(admin.email2)
    return emails

