# Email Notification Setup Guide

## Overview
The CREDIT Inventory System now includes email notifications for:
- **Borrow Confirmations**: Sent when items are borrowed
- **Return Confirmations**: Sent when items are returned
- **Overdue Reminders**: Sent automatically via cron job for overdue items

## Configuration

### Step 1: Environment Variables
Create a `.env` file in the `backend` directory (or set environment variables) with the following:

```env
# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=CREDIT Inventory System
SMTP_USE_TLS=true
```

### Step 2: Gmail Setup (Example)
If using Gmail:

1. **Enable 2-Factor Authentication** on your Google account
2. **Generate an App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a password for "Mail"
   - Use this password in `SMTP_PASSWORD`

### Step 3: Other Email Providers
Examples:

**Outlook/Hotmail:**
```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USE_TLS=true
```

**Yahoo:**
```env
SMTP_HOST=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USE_TLS=true
```

**Custom SMTP:**
```env
SMTP_HOST=mail.yourdomain.com
SMTP_PORT=587
SMTP_USE_TLS=true
```

## Database Migration

### Step 1: Run Overdue Email Flag Migration
```bash
cd backend
python migrate_add_overdue_email_flag.py
```

This adds the `overdue_email_sent` column to track which transactions have received overdue reminders.

## Email Notification Features

### 1. Borrow Notifications
- **When**: Immediately after a borrow transaction is created
- **Content**: 
  - List of borrowed items (name, category, quantity)
  - Expected return date
  - Borrow reason
  - PIC name who processed it
- **Recipient**: Borrower's email address

### 2. Return Notifications
- **When**: Immediately after items are returned
- **Content**:
  - List of returned items
  - Return date and time
  - PIC name who processed it
  - Optional remarks
- **Recipient**: Borrower's email address

### 3. Overdue Reminders
- **When**: Daily at 9:00 AM (via cron job)
- **Trigger Conditions**:
  - Transaction is overdue (today > expected_return_date)
  - Transaction has remaining items (not fully returned)
  - `overdue_email_sent` flag is `False`
  - Borrower has a valid email address
- **Content**:
  - List of overdue items
  - Days overdue
  - Expected return date
- **Anti-Spam Protection**:
  - Each transaction receives only ONE overdue email
  - Flag is set to `True` after successful send
  - Weekly reset (Monday 8:00 AM) allows re-sending if items still not returned

## Scheduler Configuration

The overdue email scheduler runs automatically when the application starts:

- **Daily Check**: 9:00 AM - Checks for overdue items and sends reminders
- **Weekly Reset**: Monday 8:00 AM - Resets flags for unreturned items to allow re-sending

### Manual Trigger

You can manually trigger an overdue check via the admin endpoint:

```bash
POST /admin/email/trigger-overdue-check
```

Check scheduler status:

```bash
GET /admin/email/scheduler-status
```

## Testing

### Test Email Configuration
1. Ensure environment variables are set
2. Create a test borrow transaction with a valid borrower email
3. Check that email is sent (check borrower's inbox)

### Test Overdue Emails
1. Create a borrow transaction with expected_return_date in the past
2. Ensure `overdue_email_sent` is `False` for that transaction
3. Manually trigger: `POST /admin/email/trigger-overdue-check`
4. Check borrower's inbox for overdue reminder

## Troubleshooting

### Emails Not Sending
1. **Check Configuration**:
   - Verify all SMTP environment variables are set
   - Test SMTP credentials manually

2. **Check Logs**:
   - Look for email-related errors in application logs
   - Check for SMTP authentication errors

3. **Check Email Service Status**:
   - The service logs warnings if not configured
   - Check application startup logs

### Overdue Emails Not Sending
1. **Check Scheduler**:
   - Verify scheduler is running: `GET /admin/email/scheduler-status`
   - Check application logs for scheduler errors

2. **Check Transaction Status**:
   - Ensure transaction is overdue (expected_return_date < today)
   - Ensure `overdue_email_sent` is `False`
   - Ensure borrower has a valid email address

3. **Manual Trigger**:
   - Use `POST /admin/email/trigger-overdue-check` to test

### Email Spam Prevention
The system includes built-in spam prevention:

- **One Email Per Transaction**: Each overdue transaction sends only one email
- **Flag-Based Tracking**: `overdue_email_sent` flag prevents duplicate sends
- **Weekly Reset**: Allows re-sending only if items are still not returned after a week

## Security Notes

1. **Never commit `.env` file** to version control
2. **Use App Passwords** instead of main account passwords
3. **Restrict SMTP access** to trusted IPs if possible
4. **Monitor email sending** for unusual activity

## Production Recommendations

1. **Use Dedicated Email Service**: Consider services like SendGrid, Mailgun, or AWS SES
2. **Rate Limiting**: Implement rate limiting for email sending
3. **Email Queue**: Consider using a message queue (Redis, RabbitMQ) for high-volume scenarios
4. **Monitoring**: Set up monitoring for email delivery rates
5. **Error Handling**: Implement retry logic for failed email sends

## Support

For issues or questions:
- Check application logs for detailed error messages
- Verify SMTP configuration matches your email provider's requirements
- Test SMTP connection manually using Python's `smtplib`






