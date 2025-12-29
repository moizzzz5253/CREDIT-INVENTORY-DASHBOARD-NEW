from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.database.models import Admin
from app.schemas.admin import (
    AdminVerifyPassword,
    AdminInfo,
    AdminUpdate,
    AdminVerifyResponse
)
from app.core.security import (
    verify_password,
    hash_password,
    DEFAULT_ADMIN_PASSWORD
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


def get_or_create_admin(db: Session) -> Admin:
    """Get the admin record, creating it if it doesn't exist."""
    admin = db.query(Admin).first()
    if admin is None:
        # Create a new admin record
        admin = Admin()
        db.add(admin)
        db.commit()
        db.refresh(admin)
    return admin


@router.post("/verify-password", response_model=AdminVerifyResponse)
def verify_admin_password(
    credentials: AdminVerifyPassword,
    db: Session = Depends(get_db)
):
    """
    Verify the admin password.
    For first-time use, checks against hardcoded password.
    After password is set, checks against hashed password in database.
    """
    admin = get_or_create_admin(db)
    
    # Trim password to handle any accidental whitespace
    password = credentials.password.strip() if credentials.password else ""
    
    if not password:
        return AdminVerifyResponse(
            success=False,
            message="Password cannot be empty"
        )
    
    # Check if using default password or custom password
    if admin.password_hash is None or admin.password_hash == "":
        # Using hardcoded password
        if password == DEFAULT_ADMIN_PASSWORD:
            return AdminVerifyResponse(
                success=True,
                message="Password verified successfully"
            )
        else:
            return AdminVerifyResponse(
                success=False,
                message="Invalid password"
            )
    else:
        # Using custom password
        try:
            is_valid = verify_password(password, admin.password_hash)
            if is_valid:
                return AdminVerifyResponse(
                    success=True,
                    message="Password verified successfully"
                )
            else:
                return AdminVerifyResponse(
                    success=False,
                    message="Invalid password"
                )
        except Exception as e:
            # Log the error for debugging
            print(f"Password verification error: {str(e)}")
            print(f"Password hash exists: {admin.password_hash is not None}")
            print(f"Password hash length: {len(admin.password_hash) if admin.password_hash else 0}")
            return AdminVerifyResponse(
                success=False,
                message=f"Error verifying password: {str(e)}"
            )


@router.get("/info", response_model=AdminInfo)
def get_admin_info(db: Session = Depends(get_db)):
    """Get admin information (without password)."""
    admin = get_or_create_admin(db)
    return AdminInfo(
        name=admin.name,
        email=admin.email,
        email2=admin.email2,
        phone=admin.phone,
        has_custom_password=admin.password_hash is not None
    )


@router.get("/emails")
def get_admin_emails_endpoint(db: Session = Depends(get_db)):
    """
    Get admin emails for use in email sending processes.
    Returns both email and email2 fields.
    """
    from app.utils.admin_emails import get_admin_emails
    return get_admin_emails(db)


@router.get("/debug-password")
def debug_password_info(db: Session = Depends(get_db)):
    """
    Debug endpoint to check password hash status.
    WARNING: This is for debugging only. Remove in production.
    """
    admin = get_or_create_admin(db)
    
    debug_info = {
        "has_password_hash": admin.password_hash is not None,
        "password_hash_length": len(admin.password_hash) if admin.password_hash else 0,
        "password_hash_preview": admin.password_hash[:30] + "..." if admin.password_hash else None,
        "using_default_password": admin.password_hash is None or admin.password_hash == "",
    }
    
    # Test common passwords
    if admin.password_hash:
        from app.core.security import verify_password
        test_passwords = ["credit123", "123456", "admin123"]
        debug_info["test_results"] = {
            pwd: verify_password(pwd, admin.password_hash) 
            for pwd in test_passwords
        }
    
    return debug_info


@router.post("/reset-password")
def reset_password_to_default(db: Session = Depends(get_db)):
    """
    Reset password to use default hardcoded password.
    WARNING: This clears the custom password. Use only for debugging.
    """
    admin = get_or_create_admin(db)
    admin.password_hash = None
    db.commit()
    return {
        "success": True,
        "message": "Password reset to default (admin123)",
        "using_default": True
    }


@router.put("/update", response_model=AdminInfo)
def update_admin_info(
    update_data: AdminUpdate,
    db: Session = Depends(get_db)
):
    """
    Update admin information.
    Can update name, email, phone, and/or password.
    """
    admin = get_or_create_admin(db)
    
    # Update fields if provided
    if update_data.name is not None:
        admin.name = update_data.name
    if update_data.email is not None:
        admin.email = update_data.email
    if update_data.email2 is not None:
        admin.email2 = update_data.email2
    if update_data.phone is not None:
        admin.phone = update_data.phone
    if update_data.new_password is not None:
        # Trim and validate password
        new_password = update_data.new_password.strip() if update_data.new_password else ""
        
        if not new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password cannot be empty"
            )
        if len(new_password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long"
            )
        # Validate password length (bcrypt has 72-byte limit)
        password_bytes = new_password.encode('utf-8')
        if len(password_bytes) > 72:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password cannot exceed 72 bytes in length"
            )
        try:
            # Hash the new password
            hashed = hash_password(new_password)
            admin.password_hash = hashed
            
            # Verify the hash works immediately (for debugging)
            from app.core.security import verify_password
            test_verify = verify_password(new_password, hashed)
            print(f"Password hashed successfully. Hash length: {len(hashed)}")
            print(f"Immediate verification test: {test_verify}")
            
            if not test_verify:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Password hash verification failed immediately after hashing"
                )
        except ValueError as e:
            # Handle bcrypt errors
            error_msg = str(e)
            if "72 bytes" in error_msg or "longer than 72" in error_msg.lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Password cannot exceed 72 bytes in length"
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error hashing password: {error_msg}"
            )
        except Exception as e:
            print(f"Unexpected error hashing password: {type(e).__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error hashing password: {str(e)}"
            )
    
    db.commit()
    db.refresh(admin)
    
    return AdminInfo(
        name=admin.name,
        email=admin.email,
        email2=admin.email2,
        phone=admin.phone,
        has_custom_password=admin.password_hash is not None
    )

