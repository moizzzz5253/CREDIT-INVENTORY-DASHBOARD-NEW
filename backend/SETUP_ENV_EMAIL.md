# Step-by-Step Guide: Setting Up .env File for Email

## 📋 Overview
This guide will help you create and configure the `.env` file needed for email notifications in the CREDIT Inventory System.

## 🎯 Step 1: Locate the Backend Directory

Navigate to your backend directory:
```
C:\Cursor IDE\CREDIT-INVENTORY-DASHBOARD-NEW\backend
```

## 📝 Step 2: Create the .env File

### Option A: Using File Explorer (Windows)
1. Open File Explorer
2. Navigate to: `C:\Cursor IDE\CREDIT-INVENTORY-DASHBOARD-NEW\backend`
3. Right-click in the folder → New → Text Document
4. Rename it to `.env` (make sure to remove the `.txt` extension)
   - If Windows asks about changing the extension, click "Yes"

### Option B: Using Command Line
```powershell
cd "C:\Cursor IDE\CREDIT-INVENTORY-DASHBOARD-NEW\backend"
New-Item -Path ".env" -ItemType File
```

### Option C: Using VS Code/Cursor
1. In Cursor, open the `backend` folder
2. Click "New File" (or press `Ctrl+N`)
3. Save it as `.env` (File → Save As → name it `.env`)

## ✏️ Step 3: Add Email Configuration

Open the `.env` file and add the following content:

### For Gmail (Recommended for Testing)

```env
# SMTP Configuration for Gmail
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password-here
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=CREDIT Inventory System
SMTP_USE_TLS=true
```

### For Outlook/Hotmail

```env
# SMTP Configuration for Outlook
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=your-email@outlook.com
SMTP_PASSWORD=your-password
SMTP_FROM_EMAIL=your-email@outlook.com
SMTP_FROM_NAME=CREDIT Inventory System
SMTP_USE_TLS=true
```

### For Yahoo Mail

```env
# SMTP Configuration for Yahoo
SMTP_HOST=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USER=your-email@yahoo.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@yahoo.com
SMTP_FROM_NAME=CREDIT Inventory System
SMTP_USE_TLS=true
```

## 🔐 Step 4: Get Your Email Credentials

### For Gmail (Most Common)

1. **Enable 2-Factor Authentication** (if not already enabled):
   - Go to: https://myaccount.google.com/security
   - Under "Signing in to Google", enable "2-Step Verification"

2. **Generate App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Or: Google Account → Security → 2-Step Verification → App passwords
   - Select "Mail" as the app
   - Select "Other (Custom name)" as device, enter "CREDIT Inventory"
   - Click "Generate"
   - **Copy the 16-character password** (it looks like: `abcd efgh ijkl mnop`)

3. **Use the App Password**:
   - In your `.env` file, use the app password (remove spaces)
   - Example: `SMTP_PASSWORD=abcdefghijklmnop`

### For Outlook/Hotmail

1. **Enable 2-Factor Authentication** (recommended)
2. **Generate App Password**:
   - Go to: https://account.microsoft.com/security
   - Security → Advanced security options → App passwords
   - Generate a new app password for "Mail"
   - Use this password in `.env`

### For Yahoo Mail

1. **Enable 2-Factor Authentication**
2. **Generate App Password**:
   - Go to: https://login.yahoo.com/account/security
   - Generate app password
   - Use this password in `.env`

## 📋 Step 5: Complete Example

Here's a complete example `.env` file for Gmail:

```env
# Email Configuration for CREDIT Inventory System
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=john.doe@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
SMTP_FROM_EMAIL=john.doe@gmail.com
SMTP_FROM_NAME=CREDIT Inventory System
SMTP_USE_TLS=true
```

**Important:** Replace:
- `john.doe@gmail.com` with your actual email
- `abcdefghijklmnop` with your actual app password

## ✅ Step 6: Verify Your .env File

Your `.env` file should:
- ✅ Be located in the `backend` folder
- ✅ Have no file extension (not `.env.txt`)
- ✅ Contain all 7 required variables
- ✅ Have no spaces around the `=` sign
- ✅ Use quotes only if your password contains special characters

## 🧪 Step 7: Test Your Configuration

1. **Start your application**:
   ```bash
   cd backend
   python run_dev.py
   ```

2. **Check the logs** for email service status:
   - If configured correctly: You'll see no warnings
   - If not configured: You'll see: "Email service not fully configured"

3. **Test by creating a borrow**:
   - Create a new borrow transaction with a borrower email
   - Check if email is sent (check borrower's inbox)

## ⚠️ Common Issues and Solutions

### Issue 1: "No such file or directory: .env"
**Solution**: Make sure the `.env` file is in the `backend` folder, not the root folder.

### Issue 2: "Email service not fully configured"
**Solution**: 
- Check that all variables are set
- Make sure there are no typos in variable names
- Verify SMTP_USER, SMTP_PASSWORD, and SMTP_FROM_EMAIL are not empty

### Issue 3: "SMTP Authentication failed"
**Solution**:
- For Gmail: Make sure you're using an App Password, not your regular password
- Check that 2-Factor Authentication is enabled
- Verify the password doesn't have extra spaces

### Issue 4: "Connection refused" or "Connection timeout"
**Solution**:
- Check your internet connection
- Verify SMTP_HOST and SMTP_PORT are correct
- Check if your firewall is blocking the connection
- For Gmail: Make sure "Less secure app access" is enabled (if not using App Password)

### Issue 5: File shows as ".env.txt" instead of ".env"
**Solution**:
- In File Explorer, go to View → Show → File name extensions
- Rename the file and remove `.txt` extension
- Windows will ask to confirm - click "Yes"

## 🔒 Security Best Practices

1. **Never commit `.env` to Git**:
   - The `.env` file should already be in `.gitignore`
   - Never share your `.env` file publicly

2. **Use App Passwords**:
   - Always use app-specific passwords, not your main account password
   - This limits damage if credentials are compromised

3. **Restrict Access**:
   - Only give access to trusted team members
   - Use different credentials for development and production

4. **Regular Updates**:
   - Change passwords periodically
   - Revoke old app passwords when no longer needed

## 📍 File Location Reference

Your `.env` file should be here:
```
C:\Cursor IDE\CREDIT-INVENTORY-DASHBOARD-NEW\backend\.env
```

The file structure should look like:
```
backend/
├── .env                    ← Your email config file
├── app/
├── requirements.txt
├── run_dev.py
└── ...
```

## 🎯 Quick Checklist

Before starting the application, verify:
- [ ] `.env` file exists in `backend` folder
- [ ] All 7 SMTP variables are set
- [ ] Email and password are correct
- [ ] Using App Password (for Gmail/Outlook/Yahoo)
- [ ] No typos in variable names
- [ ] File is named `.env` (not `.env.txt`)

## 💡 Need Help?

If you're still having issues:
1. Check the application logs for specific error messages
2. Verify your email provider's SMTP settings
3. Test SMTP connection manually using Python:
   ```python
   import smtplib
   server = smtplib.SMTP('smtp.gmail.com', 587)
   server.starttls()
   server.login('your-email@gmail.com', 'your-app-password')
   print("Connection successful!")
   ```

---

**Next Steps**: After setting up `.env`, restart your application and test email notifications!






