# Fixing Outlook SMTP Authentication Error

## Error Message
```
SMTP error sending email: (535, b'5.7.139 Authentication unsuccessful, basic authentication is disabled.')
```

## Problem
Outlook/Office 365 has disabled basic authentication for many accounts. You need to use either:
1. **App Password** (if 2FA is enabled) - **RECOMMENDED**
2. **Enable SMTP AUTH** in your Outlook account settings
3. **Use OAuth2** (more complex)

## Solution 1: Use App Password (Easiest)

### Step 1: Enable 2-Factor Authentication
1. Go to: https://account.microsoft.com/security
2. Sign in with your Outlook account
3. Enable "Two-step verification" if not already enabled

### Step 2: Generate App Password
1. Go to: https://account.microsoft.com/security
2. Click on "Advanced security options"
3. Click "App passwords" (under "Two-step verification")
4. Click "Create a new app password"
5. Name it "CREDIT Inventory System"
6. Click "Generate"
7. **Copy the 16-character password** (it will look like: `abcd-efgh-ijkl-mnop`)

### Step 3: Update .env File
Replace your `SMTP_PASSWORD` with the App Password (remove the dashes):

```env
SMTP_PASSWORD=abcdefghijklmnop
```

**Important**: Use the App Password, NOT your regular Outlook password!

## Solution 2: Enable SMTP AUTH in Outlook (If Available)

Some Outlook accounts allow enabling SMTP AUTH:

1. Go to: https://outlook.office.com/mail/
2. Click Settings (gear icon) → View all Outlook settings
3. Go to Mail → Sync email
4. Look for "SMTP AUTH" or "Authenticated SMTP" option
5. Enable it if available

**Note**: This option may not be available for all accounts, especially newer ones.

## Solution 3: Check Account Type

### Personal Outlook Account (@outlook.com, @hotmail.com)
- Use App Password (Solution 1)
- SMTP settings:
  ```
  SMTP_HOST=smtp-mail.outlook.com
  SMTP_PORT=587
  SMTP_USE_TLS=true
  ```

### Office 365 / Microsoft 365 Account (@company.com)
- May require admin to enable SMTP AUTH
- Or use App Password if 2FA is enabled
- SMTP settings:
  ```
  SMTP_HOST=smtp.office365.com
  SMTP_PORT=587
  SMTP_USE_TLS=true
  ```

## Solution 4: Alternative - Use Gmail Instead

If Outlook continues to cause issues, you can switch to Gmail:

### Update .env for Gmail:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=CREDIT Inventory System
SMTP_USE_TLS=true
```

### Get Gmail App Password:
1. Go to: https://myaccount.google.com/apppasswords
2. Generate app password
3. Use the 16-character password in `.env`

## Quick Fix Steps

1. **Try App Password first** (Solution 1) - This works for most Outlook accounts
2. **If that doesn't work**, check if you can enable SMTP AUTH (Solution 2)
3. **If still failing**, consider switching to Gmail (Solution 4)

## Testing After Fix

After updating your `.env` file:

1. Restart your application
2. Run the config checker:
   ```bash
   python check_env_config.py
   ```
3. Test by creating a borrow transaction
4. Check logs for "Email sent successfully" message

## Common Issues

### "Still getting authentication error after using App Password"
- Make sure you removed dashes from the App Password
- Verify 2FA is enabled on your account
- Try regenerating the App Password

### "Can't find App Passwords option"
- Make sure 2-Factor Authentication is enabled first
- Some accounts may not have this option (use Solution 4 instead)

### "App Password doesn't work"
- Double-check you're using the App Password, not your regular password
- Make sure there are no extra spaces
- Try generating a new App Password

## Need More Help?

If none of these solutions work:
1. Check your Outlook account type (personal vs. business)
2. Contact your IT admin if it's a business account
3. Consider using a dedicated email service (SendGrid, Mailgun, etc.)






