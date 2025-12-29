"""
Script to check if .env file is properly configured for email.
Run this to verify your email configuration before starting the application.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

print("=" * 60)
print("Email Configuration Checker")
print("=" * 60)
print()

# Check if .env file exists
if not env_path.exists():
    print("[ERROR] .env file not found!")
    print(f"   Expected location: {env_path}")
    print()
    print("   Please create a .env file in the backend directory.")
    print("   See SETUP_ENV_EMAIL.md for instructions.")
    exit(1)
else:
    print(f"[OK] .env file found at: {env_path}")
    print()

# Check each required variable
required_vars = {
    "SMTP_HOST": os.getenv("SMTP_HOST"),
    "SMTP_PORT": os.getenv("SMTP_PORT"),
    "SMTP_USER": os.getenv("SMTP_USER"),
    "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD"),
    "SMTP_FROM_EMAIL": os.getenv("SMTP_FROM_EMAIL"),
    "SMTP_FROM_NAME": os.getenv("SMTP_FROM_NAME"),
    "SMTP_USE_TLS": os.getenv("SMTP_USE_TLS"),
}

print("Checking environment variables:")
print("-" * 60)

all_ok = True
for var_name, var_value in required_vars.items():
    if var_value:
        # Mask password for security
        display_value = "***" if "PASSWORD" in var_name else var_value
        print(f"[OK]  {var_name:20} = {display_value}")
    else:
        print(f"[MISSING] {var_name:20} = (not set or empty)")
        all_ok = False

print("-" * 60)
print()

# Check if email is configured
if all_ok:
    print("[OK] All email configuration variables are set!")
    print()
    print("Email service should work correctly.")
    print("You can now start your application.")
else:
    print("[ERROR] Some email configuration variables are missing or empty.")
    print()
    print("Please check your .env file and ensure all variables are set:")
    print("  - SMTP_HOST")
    print("  - SMTP_PORT")
    print("  - SMTP_USER")
    print("  - SMTP_PASSWORD")
    print("  - SMTP_FROM_EMAIL")
    print("  - SMTP_FROM_NAME")
    print("  - SMTP_USE_TLS")
    print()
    print("See SETUP_ENV_EMAIL.md for detailed instructions.")

print()
print("=" * 60)

