"""
Scheduler service for sending overdue email reminders.
Runs as a background task to check for overdue items and send notifications.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from datetime import date, datetime
from loguru import logger
import pytz

from app.database.db import SessionLocal
from app.database.models import BorrowTransaction, BorrowItem, BorrowStatus
from app.services.email_service import email_service
from app.services.arduino_service import arduino_service
from app.utils.admin_emails import get_admin_email_list

# Timezone for Kuala Lumpur (GMT+8) - same as email service
KL_TIMEZONE = pytz.timezone('Asia/Kuala_Lumpur')


class OverdueEmailScheduler:
    """Scheduler for sending overdue email reminders."""
    
    def __init__(self):
        # Configure scheduler to use Kuala Lumpur timezone (GMT+8)
        self.scheduler = BackgroundScheduler(timezone=KL_TIMEZONE)
        self.is_running = False
    
    def check_and_send_overdue_emails(self):
        """
        Check for overdue transactions and send email reminders.
        Groups all overdue items by borrower email to send one email per borrower
        (similar to how borrow system groups items in one transaction).
        """
        db: Session = SessionLocal()
        try:
            today = date.today()
            
            # Get all active/overdue transactions that haven't sent overdue email yet
            transactions = (
                db.query(BorrowTransaction)
                .filter(
                    BorrowTransaction.status != BorrowStatus.COMPLETED,
                    BorrowTransaction.overdue_email_sent == False,
                    BorrowTransaction.expected_return_date < today
                )
                .all()
            )
            
            # Group transactions by borrower email
            # Key: borrower_email, Value: {borrower_name, transactions: [], overdue_items: []}
            borrower_groups = {}
            
            for tx in transactions:
                # Skip if borrower has no email
                if not tx.borrower or not tx.borrower.email:
                    continue
                
                borrower_email = tx.borrower.email.lower()
                borrower_name = tx.borrower.name
                borrower_tp_id = tx.borrower.tp_id
                borrower_phone = tx.borrower.phone
                
                # Initialize borrower group if not exists
                if borrower_email not in borrower_groups:
                    borrower_groups[borrower_email] = {
                        'borrower_name': borrower_name,
                        'borrower_email': borrower_email,
                        'borrower_tp_id': borrower_tp_id,
                        'borrower_phone': borrower_phone,
                        'transactions': [],
                        'overdue_items': [],
                        'expected_return_dates': set(),
                        'days_overdue_list': []
                    }
                
                # Collect overdue items from this transaction
                transaction_items = []
                for item in tx.items:
                    if not item.component:
                        continue
                    
                    remaining = item.quantity_borrowed - item.quantity_returned
                    if remaining > 0:
                        transaction_items.append({
                            'component_name': item.component.name,
                            'category': item.component.category,
                            'quantity': remaining,
                            'expected_return_date': tx.expected_return_date,
                            'days_overdue': (today - tx.expected_return_date).days
                        })
                
                # Only include transaction if it has remaining items
                if transaction_items:
                    borrower_groups[borrower_email]['transactions'].append(tx)
                    borrower_groups[borrower_email]['overdue_items'].extend(transaction_items)
                    borrower_groups[borrower_email]['expected_return_dates'].add(tx.expected_return_date)
                    borrower_groups[borrower_email]['days_overdue_list'].append(
                        (today - tx.expected_return_date).days
                    )
            
            # Send one email per borrower with all their overdue items
            emails_sent = 0
            
            for borrower_email, group_data in borrower_groups.items():
                if not group_data['overdue_items']:
                    continue
                
                # Calculate earliest expected return date and maximum days overdue
                earliest_return_date = min(group_data['expected_return_dates'])
                max_days_overdue = max(group_data['days_overdue_list'])
                
                # Prepare items list (can optionally group by date)
                overdue_items = group_data['overdue_items']
                
                try:
                    success = email_service.send_overdue_notification(
                        borrower_email=borrower_email,
                        borrower_name=group_data['borrower_name'],
                        overdue_items=overdue_items,
                        expected_return_date=earliest_return_date,
                        days_overdue=max_days_overdue,
                        all_return_dates=list(group_data['expected_return_dates'])
                    )
                    
                    if success:
                        # Mark all transactions for this borrower as sent
                        for tx in group_data['transactions']:
                            tx.overdue_email_sent = True
                        
                        emails_sent += 1
                        logger.info(
                            f"Sent overdue email to {borrower_email} "
                            f"({len(group_data['transactions'])} transaction(s), "
                            f"{len(overdue_items)} item(s), {max_days_overdue} days overdue)"
                        )
                    else:
                        logger.warning(
                            f"Failed to send overdue email to {borrower_email}"
                        )
                except Exception as e:
                    logger.error(
                        f"Error sending overdue email to {borrower_email}: {e}"
                    )
            
            # Send admin notification with all overdue borrowers
            if len(borrower_groups) > 0:
                try:
                    # Get admin emails
                    admin_emails = get_admin_email_list(db)
                    
                    if admin_emails:
                        # Prepare overdue borrowers data for admin notification
                        overdue_borrowers_data = []
                        for borrower_email, group_data in borrower_groups.items():
                            if not group_data['overdue_items']:
                                continue
                            
                            # Calculate earliest expected return date and maximum days overdue
                            earliest_return_date = min(group_data['expected_return_dates'])
                            max_days_overdue = max(group_data['days_overdue_list'])
                            
                            overdue_borrowers_data.append({
                                'borrower_name': group_data['borrower_name'],
                                'borrower_email': group_data['borrower_email'],
                                'borrower_tp_id': group_data['borrower_tp_id'],
                                'borrower_phone': group_data['borrower_phone'],
                                'overdue_items': group_data['overdue_items'],
                                'earliest_return_date': earliest_return_date,
                                'max_days_overdue': max_days_overdue
                            })
                        
                        # Send admin notification
                        if overdue_borrowers_data:
                            admin_success = email_service.send_overdue_notification_to_admin(
                                overdue_borrowers=overdue_borrowers_data,
                                admin_emails=admin_emails
                            )
                            
                            if admin_success:
                                logger.info(
                                    f"Sent overdue admin notification to {len(admin_emails)} admin(s) "
                                    f"for {len(overdue_borrowers_data)} borrower(s)"
                                )
                            else:
                                logger.warning("Failed to send overdue admin notification")
                    else:
                        logger.warning("No admin emails configured. Skipping admin notification.")
                except Exception as e:
                    logger.error(f"Error sending admin overdue notification: {e}")
            
            db.commit()
            
            # Determine overall success/failure for Arduino buzzer
            # Success: if we found overdue items and successfully sent at least one email
            # Failure: if we found overdue items but failed to send emails, or if there was an error
            overall_success = False
            if len(borrower_groups) > 0:
                # We found overdue items
                if emails_sent > 0:
                    # Successfully sent at least one email
                    overall_success = True
                    logger.info(f"Overdue email check completed. Sent {emails_sent} reminder(s) to {len(borrower_groups)} borrower(s).")
                else:
                    # Found overdue items but failed to send emails
                    overall_success = False
                    logger.warning("Overdue email check completed. Found overdue items but failed to send emails.")
            else:
                # No overdue items found - this is also considered success (no action needed)
                overall_success = True
                logger.debug("Overdue email check completed. No emails to send.")
            
            # Trigger Arduino buzzer based on result
            if overall_success:
                arduino_service.trigger_success_buzzer()
            else:
                arduino_service.trigger_failure_buzzer()
                
        except Exception as e:
            logger.error(f"Error in overdue email check: {e}")
            db.rollback()
            # Trigger failure buzzer on error
            arduino_service.trigger_failure_buzzer()
        finally:
            db.close()
    
    def reset_overdue_flags_for_unreturned(self):
        """
        Reset overdue_email_sent flag for transactions that are still overdue
        but haven't been returned. This allows re-sending overdue emails.
        
        This should be called periodically to handle cases where:
        - Borrower hasn't returned items
        - Flag was set but items are still overdue
        - Need to resend reminder
        """
        db: Session = SessionLocal()
        try:
            today = date.today()
            
            # Find transactions that:
            # 1. Are overdue (expected_return_date < today)
            # 2. Have overdue_email_sent = True
            # 3. Still have remaining items (not fully returned)
            # 4. Are not COMPLETED
            transactions = (
                db.query(BorrowTransaction)
                .filter(
                    BorrowTransaction.status != BorrowStatus.COMPLETED,
                    BorrowTransaction.overdue_email_sent == True,
                    BorrowTransaction.expected_return_date < today
                )
                .all()
            )
            
            reset_count = 0
            
            for tx in transactions:
                # Check if there are still remaining items
                has_remaining = any(
                    (item.quantity_borrowed - item.quantity_returned) > 0
                    for item in tx.items
                    if item.component
                )
                
                if has_remaining:
                    # Reset flag to allow re-sending
                    tx.overdue_email_sent = False
                    reset_count += 1
                    logger.info(
                        f"Reset overdue_email_sent flag for transaction {tx.id} "
                        f"(borrower: {tx.borrower.name}) - items still not returned"
                    )
            
            db.commit()
            
            if reset_count > 0:
                logger.info(f"Reset {reset_count} overdue email flag(s) for unreturned items.")
                
        except Exception as e:
            logger.error(f"Error resetting overdue flags: {e}")
            db.rollback()
        finally:
            db.close()
    
    def start(self):
        """Start the scheduler."""
        if self.is_running:
            logger.warning("Overdue email scheduler is already running.")
            return
        
        # Schedule daily check at 12:20 PM
        self.scheduler.add_job(
            func=self.check_and_send_overdue_emails,
            trigger=CronTrigger(hour=12, minute=20),
            id='check_overdue_emails',
            name='Check and send overdue email reminders',
            replace_existing=True
        )
        
        # Schedule weekly reset of flags for unreturned items (every Monday at 8:00 AM)
        # This allows re-sending overdue emails if items are still not returned
        self.scheduler.add_job(
            func=self.reset_overdue_flags_for_unreturned,
            trigger=CronTrigger(day_of_week='mon', hour=8, minute=0),
            id='reset_overdue_flags',
            name='Reset overdue email flags for unreturned items',
            replace_existing=True
        )
        
        self.scheduler.start()
        self.is_running = True
        logger.info("Overdue email scheduler started.")
        logger.info("  - Daily overdue check: 12:20 PM (Kuala Lumpur time, GMT+8)")
        logger.info("  - Weekly flag reset: Monday 8:00 AM (Kuala Lumpur time, GMT+8)")
    
    def stop(self):
        """Stop the scheduler."""
        if not self.is_running:
            return
        
        self.scheduler.shutdown()
        self.is_running = False
        logger.info("Overdue email scheduler stopped.")
    
    def run_manual_check(self):
        """Manually trigger an overdue email check (for testing/admin use)."""
        logger.info("Running manual overdue email check...")
        self.check_and_send_overdue_emails()


# Global scheduler instance
overdue_scheduler = OverdueEmailScheduler()



