# Gmail Email Configuration Guide

## Quick Setup Steps

### Step 1: Get Gmail App Password

1. **Enable 2-Factor Authentication** (if not already enabled):
   - Go to: https://myaccount.google.com/security
   - Under "Signing in to Google", enable "2-Step Verification"

2. **Generate App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Or: Google Account → Security → 2-Step Verification → App passwords
   - Select "Mail" as the app
   - Select "Other (Custom name)" as device
   - Enter: "CREDIT Inventory System"
   - Click "Generate"
   - **Copy the 16-character password** (it looks like: `abcd efgh ijkl mnop`)

### Step 2: Update .env File

Open your `.env` file in the `backend` directory and update it with these Gmail settings:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-character-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=CREDIT Inventory System
SMTP_USE_TLS=true
```

**Important:**
- Replace `your-email@gmail.com` with your actual Gmail address
- Replace `your-16-character-app-password` with the App Password (remove spaces/dashes)
- Use the **App Password**, NOT your regular Gmail password

### Step 3: Example .env File

Here's a complete example:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=creditinventory@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
SMTP_FROM_EMAIL=creditinventory@gmail.com
SMTP_FROM_NAME=CREDIT Inventory System
SMTP_USE_TLS=true
```

### Step 4: Verify Configuration

Run the config checker:

```bash
cd backend
python check_env_config.py
```

You should see all variables marked as `[OK]`.

### Step 5: Restart Application

Restart your application for the changes to take effect.

## Troubleshooting

### "Authentication failed" Error
- Make sure you're using an **App Password**, not your regular password
- Verify 2-Factor Authentication is enabled
- Try generating a new App Password

### "Less secure app access" Error
- Gmail no longer supports "less secure apps"
- You **must** use an App Password
- Make sure 2FA is enabled first

### Can't Find App Passwords Option
- Make sure 2-Factor Authentication is enabled first
- Go to: https://myaccount.google.com/security
- Enable "2-Step Verification" before accessing App Passwords

## Gmail vs Outlook Differences

| Setting | Gmail | Outlook |
|---------|-------|---------|
| SMTP_HOST | `smtp.gmail.com` | `smtp-mail.outlook.com` |
| SMTP_PORT | `587` | `587` |
| Authentication | App Password required | Regular password (POP/IMAP enabled) |
| 2FA Required | Yes (for App Password) | Optional |

## Security Notes

- **Never share your App Password**
- **Never commit .env file to Git**
- App Passwords are safer than regular passwords
- You can revoke App Passwords anytime from Google Account settings

## Need Help?

If you encounter issues:
1. Verify App Password is correct (no spaces/dashes)
2. Check that 2FA is enabled
3. Try generating a new App Password
4. Check application logs for specific error messages






