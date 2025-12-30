"""
Email service for sending notifications to borrowers.
Handles borrow confirmations, return confirmations, and overdue reminders.
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
from datetime import date, datetime
from loguru import logger
import pytz


# Timezone for Kuala Lumpur (GMT+8)
KL_TIMEZONE = pytz.timezone('Asia/Kuala_Lumpur')


def convert_to_kl_time(dt: datetime) -> datetime:
    """Convert UTC datetime to Kuala Lumpur time (GMT+8)."""
    if dt is None:
        return None
    
    # If datetime is naive (no timezone), assume it's UTC
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    
    # Convert to Kuala Lumpur timezone
    return dt.astimezone(KL_TIMEZONE)


def format_datetime_kl(dt: datetime, date_format: str = '%B %d, %Y at %I:%M %p') -> str:
    """Format datetime in Kuala Lumpur timezone."""
    if dt is None:
        return "N/A"
    
    kl_dt = convert_to_kl_time(dt)
    return kl_dt.strftime(date_format)


class EmailConfig:
    """Email configuration from environment variables."""
    
    @classmethod
    def get_smtp_host(cls) -> str:
        return os.getenv("SMTP_HOST", "smtp.gmail.com")
    
    @classmethod
    def get_smtp_port(cls) -> int:
        return int(os.getenv("SMTP_PORT", "587"))
    
    @classmethod
    def get_smtp_user(cls) -> str:
        return os.getenv("SMTP_USER", "")
    
    @classmethod
    def get_smtp_password(cls) -> str:
        return os.getenv("SMTP_PASSWORD", "")
    
    @classmethod
    def get_smtp_from_email(cls) -> str:
        return os.getenv("SMTP_FROM_EMAIL", "")
    
    @classmethod
    def get_smtp_from_name(cls) -> str:
        return os.getenv("SMTP_FROM_NAME", "CREDIT Inventory System")
    
    @classmethod
    def get_smtp_use_tls(cls) -> bool:
        return os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    
    @classmethod
    def is_configured(cls) -> bool:
        """Check if email is properly configured."""
        return bool(cls.get_smtp_user() and cls.get_smtp_password() and cls.get_smtp_from_email())


class EmailService:
    """Service for sending emails to borrowers."""
    
    def __init__(self):
        self.config = EmailConfig()
        if not self.config.is_configured():
            logger.warning("Email service not fully configured. Emails will not be sent.")
    
    def _create_message(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> MIMEMultipart:
        """Create an email message."""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{self.config.get_smtp_from_name()} <{self.config.get_smtp_from_email()}>"
        msg['To'] = to_email
        
        # Add text and HTML parts
        if text_body:
            text_part = MIMEText(text_body, 'plain')
            msg.attach(text_part)
        
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)
        
        return msg
    
    def _send_email(self, to_email: str, subject: str, html_body: str, text_body: Optional[str] = None) -> bool:
        """Send an email using SMTP."""
        if not self.config.is_configured():
            logger.warning(f"Email not configured. Would send to {to_email}: {subject}")
            return False
        
        if not to_email or not to_email.strip():
            logger.warning(f"Invalid email address: {to_email}")
            return False
        
        try:
            msg = self._create_message(to_email, subject, html_body, text_body)
            
            # Create SMTP connection with timeout
            server = smtplib.SMTP(self.config.get_smtp_host(), self.config.get_smtp_port(), timeout=30)
            
            try:
                # Enable debug if needed (set to 1 for verbose output)
                # server.set_debuglevel(0)
                
                # Start TLS if required
                if self.config.get_smtp_use_tls():
                    server.starttls()
                
                # Login with credentials
                server.login(self.config.get_smtp_user(), self.config.get_smtp_password())
                
                # Send the message
                server.send_message(msg)
                
                logger.info(f"Email sent successfully to {to_email}: {subject}")
                return True
                
            finally:
                # Always close the connection
                server.quit()
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication error sending email to {to_email}: {e}")
            logger.error("Please check:")
            logger.error("  1. Your email and password are correct")
            logger.error("  2. For Outlook: Make sure POP/IMAP is enabled and you're using your account password")
            logger.error("  3. For Gmail: Use an App Password, not your regular password")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending email to {to_email}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {e}")
            return False
    
    def send_borrow_notification(
        self,
        borrower_email: str,
        borrower_name: str,
        items: List[Dict[str, any]],
        expected_return_date: date,
        reason: str,
        borrowed_at: datetime,
        pic_name: str
    ) -> bool:
        """Send email notification when items are borrowed."""
        subject = "Items Borrowed - CREDIT Inventory System"
        
        # Build items list HTML
        items_html = ""
        for item in items:
            is_controlled = item.get('is_controlled', False)
            controlled_status = "Yes" if is_controlled else "No"
            controlled_style = 'color: #FF9800; font-weight: bold;' if is_controlled else 'color: #666;'
            items_html += f"""
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">{item['component_name']}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{item['category']}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{item['quantity']}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center; {controlled_style}">{controlled_status}</td>
            </tr>
            """
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 20px; }}
                .info-box {{ background-color: white; padding: 15px; margin: 10px 0; border-left: 4px solid #4CAF50; }}
                table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                th {{ background-color: #4CAF50; color: white; padding: 10px; text-align: left; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Items Borrowed Successfully</h2>
                </div>
                <div class="content">
                    <p>Dear {borrower_name},</p>
                    <p>This email confirms that you have borrowed the following items from the CREDIT Inventory System:</p>
                    
                    <table>
                        <thead>
                            <tr>
                                <th>Component Name</th>
                                <th>Category</th>
                                <th>Quantity</th>
                                <th>Controlled</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items_html}
                        </tbody>
                    </table>
                    
                    <div class="info-box">
                        <p><strong>Borrow Details:</strong></p>
                        <ul>
                            <li><strong>Expected Return Date:</strong> {expected_return_date.strftime('%B %d, %Y')}</li>
                            <li><strong>Borrowed At:</strong> {format_datetime_kl(borrowed_at)}</li>
                            <li><strong>Reason:</strong> {reason}</li>
                            <li><strong>Processed By:</strong> {pic_name}</li>
                        </ul>
                    </div>
                    
                    <p><strong>Important:</strong> Please ensure all items are returned by the expected return date to avoid overdue notifications.</p>
                    
                    <p>Thank you for using the CREDIT Inventory System.</p>
                    <p style="margin-top: 20px; padding: 15px; background-color: #f0f0f0; border-left: 4px solid #4CAF50; border-radius: 4px;">
                        <strong>Important Notice:</strong><br>
                        This is an automated, non-replyable email from the CREDIT Inventory Management System.<br>
                        For any inquiries or issues, please visit the CREDIT Centre at Level 4, Block A, Engineering Labs.<br>
                        This email serves as an official record and may be used for verification purposes.<br>
                        <span style="color: #d32f2f; font-weight: bold;">This email will never request personal or financial information. If you receive such requests, please report to CREDIT Centre immediately.</span>
                    </p>
                </div>
                <div class="footer">
                    <p style="font-size: 11px; color: #999;">CREDIT Inventory Management System - Automated Notification</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
Items Borrowed - CREDIT Inventory System

Dear {borrower_name},

This email confirms that you have borrowed the following items:

{chr(10).join([f"- {item['component_name']} ({item['category']}): {item['quantity']} - Controlled: {'Yes' if item.get('is_controlled', False) else 'No'}" for item in items])}

Borrow Details:
- Expected Return Date: {expected_return_date.strftime('%B %d, %Y')}
- Borrowed At: {format_datetime_kl(borrowed_at)}
- Reason: {reason}
- Processed By: {pic_name}

Important: Please ensure all items are returned by the expected return date.

Thank you for using the CREDIT Inventory System.

---
IMPORTANT NOTICE:
This is an automated, non-replyable email from the CREDIT Inventory Management System.
For any inquiries or issues, please visit the CREDIT Centre at Level 4, Block A, Engineering Labs.
This email serves as an official record and may be used for verification purposes.
This email will never request personal or financial information. If you receive such requests, please report to CREDIT Centre immediately.
        """
        
        return self._send_email(borrower_email, subject, html_body, text_body)
    
    def send_return_notification(
        self,
        borrower_email: str,
        borrower_name: str,
        returned_items: List[Dict[str, any]],
        returned_at: datetime,
        returned_by: str,
        remarks: Optional[str] = None
    ) -> bool:
        """Send email notification when items are returned."""
        subject = "Items Returned - CREDIT Inventory System"
        
        # Build items list HTML with optional remarks per item
        items_html = ""
        for item in returned_items:
            item_remarks = item.get('remarks', None)
            remarks_cell = f'<td style="padding: 8px; border: 1px solid #ddd; font-size: 0.9em; color: #666;">{item_remarks}</td>' if item_remarks else '<td style="padding: 8px; border: 1px solid #ddd; color: #999;">-</td>'
            
            items_html += f"""
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">{item['component_name']}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{item['category']}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{item['quantity']}</td>
                {remarks_cell}
            </tr>
            """
        
        # Show general remarks if provided (for backward compatibility)
        remarks_section = f"""
        <div class="info-box">
            <p><strong>General Remarks:</strong> {remarks}</p>
        </div>
        """ if remarks and not any(item.get('remarks') for item in returned_items) else ""
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2196F3; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 20px; }}
                .info-box {{ background-color: white; padding: 15px; margin: 10px 0; border-left: 4px solid #2196F3; }}
                table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                th {{ background-color: #2196F3; color: white; padding: 10px; text-align: left; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Items Returned Successfully</h2>
                </div>
                <div class="content">
                    <p>Dear {borrower_name},</p>
                    <p>This email confirms that you have returned the following items to the CREDIT Inventory System:</p>
                    
                    <table>
                        <thead>
                            <tr>
                                <th>Component Name</th>
                                <th>Category</th>
                                <th>Quantity Returned</th>
                                <th>Remarks</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items_html}
                        </tbody>
                    </table>
                    
                    <div class="info-box">
                        <p><strong>Return Details:</strong></p>
                        <ul>
                            <li><strong>Returned At:</strong> {format_datetime_kl(returned_at)}</li>
                            <li><strong>Processed By:</strong> {returned_by}</li>
                        </ul>
                    </div>
                    {remarks_section}
                    <p>Thank you for returning the items on time.</p>
                </div>
                <div class="footer">
                    <p><strong>Important Notice:</strong></p>
                    <p>This is an automated, non-replyable email from the CREDIT Inventory Management System.</p>
                    <p>For any inquiries or issues, please visit the CREDIT Centre at Level 4, Block A, Engineering Labs.</p>
                    <p>This email serves as an official record and may be used for verification purposes.</p>
                    <p style="margin-top: 15px; font-size: 11px; color: #999;">This email will never request personal or financial information. If you receive such requests, please report to CREDIT Centre immediately.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Build text body with remarks
        text_items = []
        for item in returned_items:
            item_text = f"- {item['component_name']} ({item['category']}): {item['quantity']}"
            if item.get('remarks'):
                item_text += f" - Remarks: {item['remarks']}"
            text_items.append(item_text)
        
        text_body = f"""
Items Returned - CREDIT Inventory System

Dear {borrower_name},

This email confirms that you have returned the following items:

{chr(10).join(text_items)}

Return Details:
- Returned At: {format_datetime_kl(returned_at)}
- Processed By: {returned_by}
{f"- Remarks: {remarks}" if remarks else ""}

Thank you for returning the items on time.

---
IMPORTANT NOTICE:
This is an automated, non-replyable email from the CREDIT Inventory Management System.
For any inquiries or issues, please visit the CREDIT Centre at Level 4, Block A, Engineering Labs.
This email serves as an official record and may be used for verification purposes.
This email will never request personal or financial information. If you receive such requests, please report to CREDIT Centre immediately.
        """
        
        return self._send_email(borrower_email, subject, html_body, text_body)
    
    def send_overdue_notification(
        self,
        borrower_email: str,
        borrower_name: str,
        overdue_items: List[Dict[str, any]],
        expected_return_date: date,
        days_overdue: int,
        all_return_dates: Optional[List[date]] = None
    ) -> bool:
        """
        Send email notification for overdue items.
        Can handle items from multiple transactions with different expected return dates.
        """
        subject = f"⚠️ Overdue Items Reminder - {days_overdue} Day{'s' if days_overdue != 1 else ''} Overdue"
        
        # Group items by expected return date if multiple dates exist
        if all_return_dates and len(all_return_dates) > 1:
            # Multiple dates - organize by date
            items_by_date = {}
            for item in overdue_items:
                item_date = item.get('expected_return_date', expected_return_date)
                if item_date not in items_by_date:
                    items_by_date[item_date] = []
                items_by_date[item_date].append(item)
            
            # Build HTML with date sections
            items_html = ""
            for return_date in sorted(items_by_date.keys()):
                date_items = items_by_date[return_date]
                date_days_overdue = (date.today() - return_date).days
                items_html += f"""
                <tr>
                    <td colspan="3" style="padding: 10px; background-color: #f5f5f5; font-weight: bold; border: 1px solid #ddd;">
                        Items due on {return_date.strftime('%B %d, %Y')} ({date_days_overdue} day{'s' if date_days_overdue != 1 else ''} overdue)
                    </td>
                </tr>
                """
                for item in date_items:
                    items_html += f"""
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;">{item['component_name']}</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{item['category']}</td>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{item['quantity']}</td>
                    </tr>
                    """
        else:
            # Single date - simple list
            items_html = ""
            for item in overdue_items:
                items_html += f"""
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;">{item['component_name']}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{item['category']}</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{item['quantity']}</td>
                </tr>
                """
        
        # Build intro message
        if all_return_dates and len(all_return_dates) > 1:
            intro_message = f'<p>You have <strong>{len(overdue_items)} overdue item{"s" if len(overdue_items) != 1 else ""}</strong> that need to be returned:</p>'
        else:
            intro_message = f'<p>The following items were due to be returned on <strong>{expected_return_date.strftime("%B %d, %Y")}</strong> and are now overdue:</p>'
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #f44336; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 20px; }}
                .warning-box {{ background-color: #fff3cd; border: 2px solid #ffc107; padding: 15px; margin: 15px 0; border-radius: 5px; }}
                .info-box {{ background-color: white; padding: 15px; margin: 10px 0; border-left: 4px solid #f44336; }}
                table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                th {{ background-color: #f44336; color: white; padding: 10px; text-align: left; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>⚠️ Overdue Items Reminder</h2>
                </div>
                <div class="content">
                    <div class="warning-box">
                        <h3 style="margin-top: 0; color: #856404;">Action Required</h3>
                        <p>You have items that are <strong>{days_overdue} day{'s' if days_overdue != 1 else ''} overdue</strong>.</p>
                    </div>
                    
                    <p>Dear {borrower_name},</p>
                    {intro_message}
                    
                    <table>
                        <thead>
                            <tr>
                                <th>Component Name</th>
                                <th>Category</th>
                                <th>Quantity</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items_html}
                        </tbody>
                    </table>
                    
                    <div class="info-box">
                        <p><strong>Please return these items as soon as possible.</strong></p>
                    </div>
                    
                    <p>Thank you for your attention to this matter.</p>
                    <p style="margin-top: 20px; padding: 15px; background-color: #fff3cd; border-left: 4px solid #f44336; border-radius: 4px;">
                        <strong>Important Notice:</strong><br>
                        This is an automated, non-replyable email from the CREDIT Inventory Management System.<br>
                        For any inquiries or issues, please visit the CREDIT Centre at Level 4, Block A, Engineering Labs.<br>
                        This email serves as an official record and may be used for verification purposes.<br>
                        <span style="color: #d32f2f; font-weight: bold;">This email will never request personal or financial information. If you receive such requests, please report to CREDIT Centre immediately.</span>
                    </p>
                </div>
                <div class="footer">
                    <p style="font-size: 11px; color: #999;">CREDIT Inventory Management System - Automated Notification</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Build text body
        if all_return_dates and len(all_return_dates) > 1:
            # Multiple dates - group by date
            text_items = []
            items_by_date = {}
            for item in overdue_items:
                item_date = item.get('expected_return_date', expected_return_date)
                if item_date not in items_by_date:
                    items_by_date[item_date] = []
                items_by_date[item_date].append(item)
            
            for return_date in sorted(items_by_date.keys()):
                date_items = items_by_date[return_date]
                date_days_overdue = (date.today() - return_date).days
                text_items.append(f"\nItems due on {return_date.strftime('%B %d, %Y')} ({date_days_overdue} day{'s' if date_days_overdue != 1 else ''} overdue):")
                for item in date_items:
                    text_items.append(f"  - {item['component_name']} ({item['category']}): {item['quantity']}")
            
            items_text = "\n".join(text_items)
        else:
            items_text = "\n".join([f"- {item['component_name']} ({item['category']}): {item['quantity']}" for item in overdue_items])
        
        text_body = f"""
Overdue Items Reminder - {days_overdue} Day{'s' if days_overdue != 1 else ''} Overdue

Dear {borrower_name},

You have {len(overdue_items)} overdue item{'s' if len(overdue_items) != 1 else ''} that need to be returned.

{items_text}

Please return these items as soon as possible.

Thank you for your attention to this matter.

---
IMPORTANT NOTICE:
This is an automated, non-replyable email from the CREDIT Inventory Management System.
For any inquiries or issues, please visit the CREDIT Centre at Level 4, Block A, Engineering Labs.
This email serves as an official record and may be used for verification purposes.
This email will never request personal or financial information. If you receive such requests, please report to CREDIT Centre immediately.
        """
        
        return self._send_email(borrower_email, subject, html_body, text_body)
    
    def send_overdue_notification_to_admin(
        self,
        overdue_borrowers: List[Dict[str, any]],
        admin_emails: Optional[List[str]] = None
    ) -> bool:
        """
        Send overdue notification to admin emails.
        Includes all overdue borrowers with their details and component information.
        
        Args:
            overdue_borrowers: List of dictionaries containing borrower and overdue item information
            admin_emails: List of admin email addresses
        """
        if not admin_emails:
            logger.warning("No admin emails provided for overdue notification")
            return False
        
        if not overdue_borrowers:
            return False
        
        subject = f"⚠️ Admin Alert: {len(overdue_borrowers)} Borrower{'s' if len(overdue_borrowers) != 1 else ''} with Overdue Items"
        
        # Build borrowers HTML table
        borrowers_html = ""
        for borrower_data in overdue_borrowers:
            borrower_name = borrower_data.get('borrower_name', 'N/A')
            borrower_email = borrower_data.get('borrower_email', 'N/A')
            borrower_tp_id = borrower_data.get('borrower_tp_id', 'N/A')
            borrower_phone = borrower_data.get('borrower_phone', 'N/A')
            overdue_items = borrower_data.get('overdue_items', [])
            max_days_overdue = borrower_data.get('max_days_overdue', 0)
            earliest_return_date = borrower_data.get('earliest_return_date')
            
            # Build items list for this borrower
            items_html = ""
            for item in overdue_items:
                items_html += f"""
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;">{item['component_name']}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{item['category']}</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{item['quantity']}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{item.get('expected_return_date', earliest_return_date).strftime('%B %d, %Y') if earliest_return_date else 'N/A'}</td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{item.get('days_overdue', 0)}</td>
                </tr>
                """
            
            borrowers_html += f"""
            <div style="margin-bottom: 30px; border: 2px solid #f44336; border-radius: 5px; padding: 15px; background-color: #fff;">
                <h3 style="color: #f44336; margin-top: 0;">Borrower: {borrower_name}</h3>
                <div style="background-color: #f9f9f9; padding: 10px; margin-bottom: 15px; border-left: 4px solid #f44336;">
                    <p style="margin: 5px 0;"><strong>Email:</strong> {borrower_email}</p>
                    <p style="margin: 5px 0;"><strong>TP ID:</strong> {borrower_tp_id}</p>
                    <p style="margin: 5px 0;"><strong>Phone:</strong> {borrower_phone}</p>
                    <p style="margin: 5px 0;"><strong>Days Overdue:</strong> {max_days_overdue} day{'s' if max_days_overdue != 1 else ''}</p>
                </div>
                <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
                    <thead>
                        <tr>
                            <th style="background-color: #f44336; color: white; padding: 10px; text-align: left; border: 1px solid #ddd;">Component Name</th>
                            <th style="background-color: #f44336; color: white; padding: 10px; text-align: left; border: 1px solid #ddd;">Category</th>
                            <th style="background-color: #f44336; color: white; padding: 10px; text-align: center; border: 1px solid #ddd;">Quantity</th>
                            <th style="background-color: #f44336; color: white; padding: 10px; text-align: left; border: 1px solid #ddd;">Expected Return Date</th>
                            <th style="background-color: #f44336; color: white; padding: 10px; text-align: center; border: 1px solid #ddd;">Days Overdue</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                    </tbody>
                </table>
            </div>
            """
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #f44336; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 20px; }}
                .warning-box {{ background-color: #fff3cd; border: 2px solid #ffc107; padding: 15px; margin: 15px 0; border-radius: 5px; }}
                .info-box {{ background-color: white; padding: 15px; margin: 10px 0; border-left: 4px solid #f44336; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>⚠️ Overdue Items - Admin Notification</h2>
                </div>
                <div class="content">
                    <div class="warning-box">
                        <h3 style="margin-top: 0; color: #856404;">Action Required</h3>
                        <p>There are <strong>{len(overdue_borrowers)} borrower{'s' if len(overdue_borrowers) != 1 else ''}</strong> with overdue items that require attention.</p>
                    </div>
                    
                    <p>Dear Admin,</p>
                    <p>The following borrowers have overdue items that need to be returned:</p>
                    
                    {borrowers_html}
                    
                    <div class="info-box">
                        <p><strong>Please follow up with these borrowers to ensure items are returned promptly.</strong></p>
                    </div>
                    
                    <p style="margin-top: 20px; padding: 15px; background-color: #fff3cd; border-left: 4px solid #f44336; border-radius: 4px;">
                        <strong>Important Notice:</strong><br>
                        This is an automated, non-replyable email from the CREDIT Inventory Management System.<br>
                        For any inquiries or issues, please visit the CREDIT Centre at Level 4, Block A, Engineering Labs.<br>
                        This email serves as an official record and may be used for verification purposes.
                    </p>
                </div>
                <div class="footer">
                    <p style="font-size: 11px; color: #999;">CREDIT Inventory Management System - Automated Notification</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Build text body
        text_borrowers = []
        for borrower_data in overdue_borrowers:
            borrower_name = borrower_data.get('borrower_name', 'N/A')
            borrower_email = borrower_data.get('borrower_email', 'N/A')
            borrower_tp_id = borrower_data.get('borrower_tp_id', 'N/A')
            borrower_phone = borrower_data.get('borrower_phone', 'N/A')
            overdue_items = borrower_data.get('overdue_items', [])
            max_days_overdue = borrower_data.get('max_days_overdue', 0)
            earliest_return_date = borrower_data.get('earliest_return_date')
            
            text_borrowers.append(f"\n{'='*60}")
            text_borrowers.append(f"Borrower: {borrower_name}")
            text_borrowers.append(f"Email: {borrower_email}")
            text_borrowers.append(f"TP ID: {borrower_tp_id}")
            text_borrowers.append(f"Phone: {borrower_phone}")
            text_borrowers.append(f"Days Overdue: {max_days_overdue} day{'s' if max_days_overdue != 1 else ''}")
            text_borrowers.append(f"\nOverdue Items:")
            for item in overdue_items:
                return_date_str = item.get('expected_return_date', earliest_return_date).strftime('%B %d, %Y') if earliest_return_date else 'N/A'
                text_borrowers.append(f"  - {item['component_name']} ({item['category']}): {item['quantity']} - Due: {return_date_str} - {item.get('days_overdue', 0)} days overdue")
        
        text_body = f"""
Overdue Items - Admin Notification

There are {len(overdue_borrowers)} borrower{'s' if len(overdue_borrowers) != 1 else ''} with overdue items that require attention.

{chr(10).join(text_borrowers)}

Please follow up with these borrowers to ensure items are returned promptly.

---
IMPORTANT NOTICE:
This is an automated, non-replyable email from the CREDIT Inventory Management System.
For any inquiries or issues, please visit the CREDIT Centre at Level 4, Block A, Engineering Labs.
This email serves as an official record and may be used for verification purposes.
        """
        
        success_count = self._send_email_to_multiple_recipients(admin_emails, subject, html_body, text_body)
        return success_count > 0
    
    def _send_email_to_multiple_recipients(
        self, 
        recipient_emails: List[str], 
        subject: str, 
        html_body: str, 
        text_body: Optional[str] = None
    ) -> int:
        """
        Send the same email content to multiple recipients.
        Returns the number of successfully sent emails.
        """
        success_count = 0
        for email in recipient_emails:
            if self._send_email(email, subject, html_body, text_body):
                success_count += 1
        return success_count
    
    def send_component_added_notification(
        self,
        component_name: str,
        category: str,
        quantity: int,
        date_added: datetime,
        remarks: Optional[str] = None,
        admin_emails: Optional[List[str]] = None
    ) -> bool:
        """
        Send notification when a controlled component is added.
        Sends separate emails to each admin email address.
        """
        if not admin_emails:
            logger.warning("No admin emails provided for component added notification")
            return False
        
        subject = f"New Controlled Component Added - {component_name}"
        date_added_str = format_datetime_kl(date_added, '%B %d, %Y at %I:%M %p')
        
        remarks_section = ""
        remarks_text = ""
        if remarks:
            remarks_section = f"""
            <div class="info-box">
                <p><strong>Remarks:</strong> {remarks}</p>
            </div>
            """
            remarks_text = f"\nRemarks: {remarks}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 20px; }}
                .info-box {{ background-color: white; padding: 15px; margin: 10px 0; border-left: 4px solid #4CAF50; }}
                table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                th {{ background-color: #4CAF50; color: white; padding: 10px; text-align: left; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>New Controlled Component Added</h2>
                </div>
                <div class="content">
                    <p>A new controlled component has been added to the CREDIT Inventory System:</p>
                    
                    <div class="info-box">
                        <p><strong>Component Details:</strong></p>
                        <ul>
                            <li><strong>Name:</strong> {component_name}</li>
                            <li><strong>Category:</strong> {category}</li>
                            <li><strong>Quantity:</strong> {quantity}</li>
                            <li><strong>Date Added:</strong> {date_added_str}</li>
                        </ul>
                    </div>
                    {remarks_section}
                    
                    <p style="margin-top: 20px; padding: 15px; background-color: #f0f0f0; border-left: 4px solid #4CAF50; border-radius: 4px;">
                        <strong>Important Notice:</strong><br>
                        This is an automated, non-replyable email from the CREDIT Inventory Management System.<br>
                        For any inquiries or issues, please visit the CREDIT Centre at Level 4, Block A, Engineering Labs.<br>
                        This email serves as an official record and may be used for verification purposes.
                    </p>
                </div>
                <div class="footer">
                    <p style="font-size: 11px; color: #999;">CREDIT Inventory Management System - Automated Notification</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
New Controlled Component Added - CREDIT Inventory System

A new controlled component has been added to the CREDIT Inventory System:

Component Details:
- Name: {component_name}
- Category: {category}
- Quantity: {quantity}
- Date Added: {date_added_str}{remarks_text}

---
IMPORTANT NOTICE:
This is an automated, non-replyable email from the CREDIT Inventory Management System.
For any inquiries or issues, please visit the CREDIT Centre at Level 4, Block A, Engineering Labs.
This email serves as an official record and may be used for verification purposes.
        """
        
        success_count = self._send_email_to_multiple_recipients(admin_emails, subject, html_body, text_body)
        return success_count > 0
    
    def send_component_deleted_notification(
        self,
        component_name: str,
        category: str,
        quantity: int,
        deletion_reason: str,
        deleted_at: datetime,
        admin_emails: Optional[List[str]] = None
    ) -> bool:
        """
        Send notification when a component is deleted.
        Sends separate emails to each admin email address.
        """
        if not admin_emails:
            logger.warning("No admin emails provided for component deleted notification")
            return False
        
        subject = f"Component Deleted - {component_name}"
        deleted_at_str = format_datetime_kl(deleted_at, '%B %d, %Y at %I:%M %p')
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #f44336; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 20px; }}
                .info-box {{ background-color: white; padding: 15px; margin: 10px 0; border-left: 4px solid #f44336; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Component Deleted</h2>
                </div>
                <div class="content">
                    <p>A component has been deleted from the CREDIT Inventory System:</p>
                    
                    <div class="info-box">
                        <p><strong>Component Details:</strong></p>
                        <ul>
                            <li><strong>Name:</strong> {component_name}</li>
                            <li><strong>Category:</strong> {category}</li>
                            <li><strong>Quantity:</strong> {quantity}</li>
                            <li><strong>Deleted At:</strong> {deleted_at_str}</li>
                            <li><strong>Deletion Reason:</strong> {deletion_reason}</li>
                        </ul>
                    </div>
                    
                    <p style="margin-top: 20px; padding: 15px; background-color: #fff3cd; border-left: 4px solid #f44336; border-radius: 4px;">
                        <strong>Important Notice:</strong><br>
                        This is an automated, non-replyable email from the CREDIT Inventory Management System.<br>
                        For any inquiries or issues, please visit the CREDIT Centre at Level 4, Block A, Engineering Labs.<br>
                        This email serves as an official record and may be used for verification purposes.
                    </p>
                </div>
                <div class="footer">
                    <p style="font-size: 11px; color: #999;">CREDIT Inventory Management System - Automated Notification</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
Component Deleted - CREDIT Inventory System

A component has been deleted from the CREDIT Inventory System:

Component Details:
- Name: {component_name}
- Category: {category}
- Quantity: {quantity}
- Deleted At: {deleted_at_str}
- Deletion Reason: {deletion_reason}

---
IMPORTANT NOTICE:
This is an automated, non-replyable email from the CREDIT Inventory Management System.
For any inquiries or issues, please visit the CREDIT Centre at Level 4, Block A, Engineering Labs.
This email serves as an official record and may be used for verification purposes.
        """
        
        success_count = self._send_email_to_multiple_recipients(admin_emails, subject, html_body, text_body)
        return success_count > 0
    
    def send_controlled_component_modified_notification(
        self,
        component_name: str,
        category: str,
        changes: List[Dict[str, any]],
        modified_at: datetime,
        admin_emails: Optional[List[str]] = None
    ) -> bool:
        """
        Send notification when a controlled component is modified.
        Sends separate emails to each admin email address.
        
        Args:
            component_name: Name of the component
            category: Category of the component
            changes: List of dictionaries with 'field_name', 'old_value', 'new_value'
            modified_at: Timestamp of modification
            admin_emails: List of admin email addresses
        """
        if not admin_emails:
            logger.warning("No admin emails provided for controlled component modified notification")
            return False
        
        if not changes:
            return False
        
        subject = f"Controlled Component Modified - {component_name}"
        modified_at_str = format_datetime_kl(modified_at, '%B %d, %Y at %I:%M %p')
        
        # Build changes table HTML
        changes_html = ""
        for change in changes:
            field_name = change.get('field_name', 'Unknown')
            old_value = change.get('old_value', 'None')
            new_value = change.get('new_value', 'None')
            
            # Format values for display
            old_display = str(old_value) if old_value is not None else "None"
            new_display = str(new_value) if new_value is not None else "None"
            
            changes_html += f"""
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">{field_name}</td>
                <td style="padding: 8px; border: 1px solid #ddd; color: #666;">{old_display}</td>
                <td style="padding: 8px; border: 1px solid #ddd; color: #2196F3; font-weight: bold;">{new_display}</td>
            </tr>
            """
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 700px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #FF9800; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 20px; }}
                .info-box {{ background-color: white; padding: 15px; margin: 10px 0; border-left: 4px solid #FF9800; }}
                table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                th {{ background-color: #FF9800; color: white; padding: 10px; text-align: left; }}
                td {{ padding: 8px; border: 1px solid #ddd; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Controlled Component Modified</h2>
                </div>
                <div class="content">
                    <p>A controlled component has been modified in the CREDIT Inventory System:</p>
                    
                    <div class="info-box">
                        <p><strong>Component Details:</strong></p>
                        <ul>
                            <li><strong>Name:</strong> {component_name}</li>
                            <li><strong>Category:</strong> {category}</li>
                            <li><strong>Modified At:</strong> {modified_at_str}</li>
                        </ul>
                    </div>
                    
                    <h3 style="margin-top: 20px; color: #FF9800;">Changes Made:</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Field</th>
                                <th>Old Value</th>
                                <th>New Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            {changes_html}
                        </tbody>
                    </table>
                    
                    <p style="margin-top: 20px; padding: 15px; background-color: #fff3cd; border-left: 4px solid #FF9800; border-radius: 4px;">
                        <strong>Important Notice:</strong><br>
                        This is an automated, non-replyable email from the CREDIT Inventory Management System.<br>
                        For any inquiries or issues, please visit the CREDIT Centre at Level 4, Block A, Engineering Labs.<br>
                        This email serves as an official record and may be used for verification purposes.
                    </p>
                </div>
                <div class="footer">
                    <p style="font-size: 11px; color: #999;">CREDIT Inventory Management System - Automated Notification</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Build text body
        text_changes = []
        for change in changes:
            field_name = change.get('field_name', 'Unknown')
            old_value = change.get('old_value', 'None')
            new_value = change.get('new_value', 'None')
            old_display = str(old_value) if old_value is not None else "None"
            new_display = str(new_value) if new_value is not None else "None"
            text_changes.append(f"- {field_name}: {old_display} → {new_display}")
        
        text_body = f"""
Controlled Component Modified - CREDIT Inventory System

A controlled component has been modified in the CREDIT Inventory System:

Component Details:
- Name: {component_name}
- Category: {category}
- Modified At: {modified_at_str}

Changes Made:
{chr(10).join(text_changes)}

---
IMPORTANT NOTICE:
This is an automated, non-replyable email from the CREDIT Inventory Management System.
For any inquiries or issues, please visit the CREDIT Centre at Level 4, Block A, Engineering Labs.
This email serves as an official record and may be used for verification purposes.
        """
        
        success_count = self._send_email_to_multiple_recipients(admin_emails, subject, html_body, text_body)
        return success_count > 0
    
    def send_controlled_components_batch_summary(
        self,
        components: List[Dict[str, any]],
        admin_emails: Optional[List[str]] = None
    ) -> bool:
        """
        Send summary email when controlled components are added in batch (e.g., Excel import).
        Sends separate emails to each admin email address.
        """
        if not admin_emails:
            logger.warning("No admin emails provided for batch component summary notification")
            return False
        
        if not components:
            return False
        
        subject = f"Batch Import: {len(components)} Controlled Component{'s' if len(components) != 1 else ''} Added"
        
        # Build components list HTML
        components_html = ""
        for comp in components:
            remarks_cell = f'<td style="padding: 8px; border: 1px solid #ddd; font-size: 0.9em; color: #666;">{comp.get("remarks", "-")}</td>' if comp.get("remarks") else '<td style="padding: 8px; border: 1px solid #ddd; color: #999;">-</td>'
            
            components_html += f"""
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">{comp.get("name", "N/A")}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{comp.get("category", "N/A")}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{comp.get("quantity", 0)}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{format_datetime_kl(comp.get("date_added"), '%B %d, %Y at %I:%M %p')}</td>
                {remarks_cell}
            </tr>
            """
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 700px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 20px; }}
                .info-box {{ background-color: white; padding: 15px; margin: 10px 0; border-left: 4px solid #4CAF50; }}
                table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                th {{ background-color: #4CAF50; color: white; padding: 10px; text-align: left; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Batch Import: Controlled Components Added</h2>
                </div>
                <div class="content">
                    <p>The following controlled components have been added to the CREDIT Inventory System via batch import:</p>
                    
                    <table>
                        <thead>
                            <tr>
                                <th>Component Name</th>
                                <th>Category</th>
                                <th>Quantity</th>
                                <th>Date Added</th>
                                <th>Remarks</th>
                            </tr>
                        </thead>
                        <tbody>
                            {components_html}
                        </tbody>
                    </table>
                    
                    <div class="info-box">
                        <p><strong>Total Components Added:</strong> {len(components)}</p>
                    </div>
                    
                    <p style="margin-top: 20px; padding: 15px; background-color: #f0f0f0; border-left: 4px solid #4CAF50; border-radius: 4px;">
                        <strong>Important Notice:</strong><br>
                        This is an automated, non-replyable email from the CREDIT Inventory Management System.<br>
                        For any inquiries or issues, please visit the CREDIT Centre at Level 4, Block A, Engineering Labs.<br>
                        This email serves as an official record and may be used for verification purposes.
                    </p>
                </div>
                <div class="footer">
                    <p style="font-size: 11px; color: #999;">CREDIT Inventory Management System - Automated Notification</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Build text body
        text_items = []
        for comp in components:
            item_text = f"- {comp.get('name', 'N/A')} ({comp.get('category', 'N/A')}): {comp.get('quantity', 0)}"
            if comp.get('remarks'):
                item_text += f" - Remarks: {comp.get('remarks')}"
            text_items.append(item_text)
        
        text_body = f"""
Batch Import: {len(components)} Controlled Component{'s' if len(components) != 1 else ''} Added - CREDIT Inventory System

The following controlled components have been added to the CREDIT Inventory System via batch import:

{chr(10).join(text_items)}

Total Components Added: {len(components)}

---
IMPORTANT NOTICE:
This is an automated, non-replyable email from the CREDIT Inventory Management System.
For any inquiries or issues, please visit the CREDIT Centre at Level 4, Block A, Engineering Labs.
This email serves as an official record and may be used for verification purposes.
        """
        
        success_count = self._send_email_to_multiple_recipients(admin_emails, subject, html_body, text_body)
        return success_count > 0
    
    def send_borrow_notification_to_admin(
        self,
        borrower_name: str,
        borrower_email: str,
        borrower_tp_id: str,
        borrower_phone: str,
        items: List[Dict[str, any]],
        expected_return_date: date,
        reason: str,
        borrowed_at: datetime,
        pic_name: str,
        admin_emails: Optional[List[str]] = None
    ) -> bool:
        """
        Send admin notification when items are borrowed.
        Same structure as borrower email but includes borrower information.
        Sends separate emails to each admin email address.
        """
        if not admin_emails:
            logger.warning("No admin emails provided for admin borrow notification")
            return False
        
        subject = "Admin Notification: Items Borrowed - CREDIT Inventory System"
        
        # Build items list HTML
        items_html = ""
        for item in items:
            is_controlled = item.get('is_controlled', False)
            controlled_status = "Yes" if is_controlled else "No"
            controlled_style = 'color: #FF9800; font-weight: bold;' if is_controlled else 'color: #666;'
            items_html += f"""
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">{item['component_name']}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{item['category']}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{item['quantity']}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center; {controlled_style}">{controlled_status}</td>
            </tr>
            """
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 20px; }}
                .info-box {{ background-color: white; padding: 15px; margin: 10px 0; border-left: 4px solid #4CAF50; }}
                table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                th {{ background-color: #4CAF50; color: white; padding: 10px; text-align: left; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Items Borrowed - Admin Notification</h2>
                </div>
                <div class="content">
                    <p>The following items have been borrowed from the CREDIT Inventory System:</p>
                    
                    <table>
                        <thead>
                            <tr>
                                <th>Component Name</th>
                                <th>Category</th>
                                <th>Quantity</th>
                                <th>Controlled</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items_html}
                        </tbody>
                    </table>
                    
                    <div class="info-box">
                        <p><strong>Borrower Information:</strong></p>
                        <ul>
                            <li><strong>Name:</strong> {borrower_name}</li>
                            <li><strong>Email:</strong> {borrower_email}</li>
                            <li><strong>TP ID:</strong> {borrower_tp_id}</li>
                            <li><strong>Phone:</strong> {borrower_phone}</li>
                        </ul>
                    </div>
                    
                    <div class="info-box">
                        <p><strong>Borrow Details:</strong></p>
                        <ul>
                            <li><strong>Expected Return Date:</strong> {expected_return_date.strftime('%B %d, %Y')}</li>
                            <li><strong>Borrowed At:</strong> {format_datetime_kl(borrowed_at)}</li>
                            <li><strong>Reason:</strong> {reason}</li>
                            <li><strong>Processed By:</strong> {pic_name}</li>
                        </ul>
                    </div>
                    
                    <p style="margin-top: 20px; padding: 15px; background-color: #f0f0f0; border-left: 4px solid #4CAF50; border-radius: 4px;">
                        <strong>Important Notice:</strong><br>
                        This is an automated, non-replyable email from the CREDIT Inventory Management System.<br>
                        For any inquiries or issues, please visit the CREDIT Centre at Level 4, Block A, Engineering Labs.<br>
                        This email serves as an official record and may be used for verification purposes.
                    </p>
                </div>
                <div class="footer">
                    <p style="font-size: 11px; color: #999;">CREDIT Inventory Management System - Automated Notification</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
Admin Notification: Items Borrowed - CREDIT Inventory System

The following items have been borrowed from the CREDIT Inventory System:

{chr(10).join([f"- {item['component_name']} ({item['category']}): {item['quantity']} - Controlled: {'Yes' if item.get('is_controlled', False) else 'No'}" for item in items])}

Borrower Information:
- Name: {borrower_name}
- Email: {borrower_email}
- TP ID: {borrower_tp_id}
- Phone: {borrower_phone}

Borrow Details:
- Expected Return Date: {expected_return_date.strftime('%B %d, %Y')}
- Borrowed At: {format_datetime_kl(borrowed_at)}
- Reason: {reason}
- Processed By: {pic_name}

---
IMPORTANT NOTICE:
This is an automated, non-replyable email from the CREDIT Inventory Management System.
For any inquiries or issues, please visit the CREDIT Centre at Level 4, Block A, Engineering Labs.
This email serves as an official record and may be used for verification purposes.
        """
        
        success_count = self._send_email_to_multiple_recipients(admin_emails, subject, html_body, text_body)
        return success_count > 0
    
    def send_return_notification_to_admin(
        self,
        borrower_name: str,
        borrower_email: str,
        borrower_tp_id: str,
        borrower_phone: str,
        returned_items: List[Dict[str, any]],
        returned_at: datetime,
        returned_by: str,
        remarks: Optional[str] = None,
        admin_emails: Optional[List[str]] = None
    ) -> bool:
        """
        Send admin notification when items are returned.
        Same structure as borrower email but includes borrower information.
        Sends separate emails to each admin email address.
        """
        if not admin_emails:
            logger.warning("No admin emails provided for admin return notification")
            return False
        
        subject = "Admin Notification: Items Returned - CREDIT Inventory System"
        
        # Build items list HTML with optional remarks per item
        items_html = ""
        for item in returned_items:
            item_remarks = item.get('remarks', None)
            remarks_cell = f'<td style="padding: 8px; border: 1px solid #ddd; font-size: 0.9em; color: #666;">{item_remarks}</td>' if item_remarks else '<td style="padding: 8px; border: 1px solid #ddd; color: #999;">-</td>'
            
            items_html += f"""
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">{item['component_name']}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{item['category']}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{item['quantity']}</td>
                {remarks_cell}
            </tr>
            """
        
        # Show general remarks if provided (for backward compatibility)
        remarks_section = f"""
        <div class="info-box">
            <p><strong>General Remarks:</strong> {remarks}</p>
        </div>
        """ if remarks and not any(item.get('remarks') for item in returned_items) else ""
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2196F3; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 20px; }}
                .info-box {{ background-color: white; padding: 15px; margin: 10px 0; border-left: 4px solid #2196F3; }}
                table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                th {{ background-color: #2196F3; color: white; padding: 10px; text-align: left; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Items Returned - Admin Notification</h2>
                </div>
                <div class="content">
                    <p>The following items have been returned to the CREDIT Inventory System:</p>
                    
                    <table>
                        <thead>
                            <tr>
                                <th>Component Name</th>
                                <th>Category</th>
                                <th>Quantity Returned</th>
                                <th>Remarks</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items_html}
                        </tbody>
                    </table>
                    
                    <div class="info-box">
                        <p><strong>Borrower Information:</strong></p>
                        <ul>
                            <li><strong>Name:</strong> {borrower_name}</li>
                            <li><strong>Email:</strong> {borrower_email}</li>
                            <li><strong>TP ID:</strong> {borrower_tp_id}</li>
                            <li><strong>Phone:</strong> {borrower_phone}</li>
                        </ul>
                    </div>
                    
                    <div class="info-box">
                        <p><strong>Return Details:</strong></p>
                        <ul>
                            <li><strong>Returned At:</strong> {format_datetime_kl(returned_at)}</li>
                            <li><strong>Processed By:</strong> {returned_by}</li>
                        </ul>
                    </div>
                    {remarks_section}
                </div>
                <div class="footer">
                    <p><strong>Important Notice:</strong></p>
                    <p>This is an automated, non-replyable email from the CREDIT Inventory Management System.</p>
                    <p>For any inquiries or issues, please visit the CREDIT Centre at Level 4, Block A, Engineering Labs.</p>
                    <p>This email serves as an official record and may be used for verification purposes.</p>
                    <p style="margin-top: 15px; font-size: 11px; color: #999;">This email will never request personal or financial information. If you receive such requests, please report to CREDIT Centre immediately.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Build text body with remarks
        text_items = []
        for item in returned_items:
            item_text = f"- {item['component_name']} ({item['category']}): {item['quantity']}"
            if item.get('remarks'):
                item_text += f" - Remarks: {item['remarks']}"
            text_items.append(item_text)
        
        text_body = f"""
Admin Notification: Items Returned - CREDIT Inventory System

The following items have been returned to the CREDIT Inventory System:

{chr(10).join(text_items)}

Borrower Information:
- Name: {borrower_name}
- Email: {borrower_email}
- TP ID: {borrower_tp_id}
- Phone: {borrower_phone}

Return Details:
- Returned At: {format_datetime_kl(returned_at)}
- Processed By: {returned_by}
{f"- Remarks: {remarks}" if remarks else ""}

---
IMPORTANT NOTICE:
This is an automated, non-replyable email from the CREDIT Inventory Management System.
For any inquiries or issues, please visit the CREDIT Centre at Level 4, Block A, Engineering Labs.
This email serves as an official record and may be used for verification purposes.
        """
        
        success_count = self._send_email_to_multiple_recipients(admin_emails, subject, html_body, text_body)
        return success_count > 0


# Global email service instance
email_service = EmailService()

