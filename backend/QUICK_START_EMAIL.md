# Quick Start - Email Notifications

## 🚀 Quick Setup (5 minutes)

### Step 1: Run Database Migration
```bash
cd backend
python migrate_add_overdue_email_flag.py
```

### Step 2: Configure Email (Choose one)

#### Option A: Gmail (Recommended for testing)
1. Enable 2-Factor Authentication on your Google account
2. Generate App Password: Google Account → Security → 2-Step Verification → App passwords
3. Create `.env` file in `backend` directory:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password-here
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=CREDIT Inventory System
SMTP_USE_TLS=true
```

#### Option B: Other Email Providers
See `EMAIL_SETUP_GUIDE.md` for Outlook, Yahoo, or custom SMTP settings.

### Step 3: Install Dependencies
```bash
pip install email-validator apscheduler
```

Or if using requirements.txt:
```bash
pip install -r requirements.txt
```

### Step 4: Start Application
```bash
python run_dev.py
```

The email scheduler will start automatically!

## ✅ Verify It Works

### Test Borrow Email
1. Create a new borrow with borrower email
2. Check borrower's inbox

### Test Overdue Email
1. Create borrow with past return date
2. Call: `POST http://localhost:8000/admin/email/trigger-overdue-check`
3. Check borrower's inbox

## 📋 What Happens Automatically

- ✅ **Borrow emails**: Sent immediately when items are borrowed
- ✅ **Return emails**: Sent immediately when items are returned  
- ✅ **Overdue emails**: Sent daily at 9:00 AM for overdue items

## 🔧 Admin Endpoints

- `POST /admin/email/trigger-overdue-check` - Manually trigger overdue check
- `GET /admin/email/scheduler-status` - Check if scheduler is running

## ⚠️ Troubleshooting

**Emails not sending?**
- Check `.env` file exists and has correct values
- Check application logs for SMTP errors
- Verify email/password are correct

**Overdue emails not sending?**
- Check scheduler status: `GET /admin/email/scheduler-status`
- Manually trigger: `POST /admin/email/trigger-overdue-check`
- Check transaction has `overdue_email_sent = False`

## 📚 More Information

- Full setup guide: `EMAIL_SETUP_GUIDE.md`
- Implementation details: `EMAIL_NOTIFICATION_SUMMARY.md`






