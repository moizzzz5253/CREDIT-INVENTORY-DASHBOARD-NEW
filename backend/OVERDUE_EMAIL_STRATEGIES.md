# Overdue Email Grouping Strategies

## Current Problem
- System sends **ONE email per transaction**
- If a borrower has 10 separate transactions (even on same date), they receive 10 emails
- This is inconvenient and spammy

## Current System Analysis
- **Borrow System**: All items in ONE transaction → ONE email ✅ (works well)
- **Overdue System**: Each transaction → Separate email ❌ (problematic)

## Strategy Options

### Strategy 1: Group by Borrower Email Only ⭐ RECOMMENDED
**Concept:**
- Collect ALL overdue transactions for each unique borrower email
- Send ONE email per borrower containing ALL their overdue items
- Similar to how borrow system groups items in one transaction

**Implementation:**
1. Query all overdue transactions (same as current)
2. Group transactions by `borrower.email`
3. For each borrower:
   - Collect ALL overdue items from ALL their transactions
   - Calculate the earliest expected return date (or show all dates)
   - Send ONE email with complete list
   - Mark ALL their transactions as `overdue_email_sent = True`

**Pros:**
- ✅ Simple and clean
- ✅ One email per borrower (like borrow system)
- ✅ Easy to implement
- ✅ No database schema changes needed

**Cons:**
- ⚠️ If borrower has items due on different dates, all shown in one email
- ⚠️ Need to handle multiple expected return dates in email template

**Email Template Changes:**
- Show all overdue items in one table
- Can group items by expected return date (optional)
- Show earliest days_overdue or range

---

### Strategy 2: Group by Borrower Email + Expected Return Date
**Concept:**
- Group by borrower email AND expected return date
- Send one email per borrower per expected return date
- If borrower has items due on Dec 26 and Dec 27, they get 2 emails (one per date)

**Implementation:**
1. Query all overdue transactions
2. Group by `(borrower.email, expected_return_date)`
3. For each group:
   - Collect all items from transactions matching that borrower+date
   - Send ONE email
   - Mark those transactions as sent

**Pros:**
- ✅ Keeps items with same due date together
- ✅ Clearer email content (one date per email)
- ✅ No schema changes

**Cons:**
- ⚠️ Borrower might still get multiple emails if they have different due dates
- ⚠️ More complex grouping logic

---

### Strategy 3: Group by Borrower, Show Date-Sectioned Items
**Concept:**
- Group by borrower email only
- In email template, organize items by expected return date (sections)
- One email per borrower, but items grouped by date within email

**Implementation:**
1. Group by borrower email
2. Organize items by expected_return_date
3. Email template has sections:
   - "Items due on Dec 26, 2024 (2 days overdue):"
   - "Items due on Dec 27, 2024 (1 day overdue):"

**Pros:**
- ✅ One email per borrower
- ✅ Items organized by date
- ✅ Clear and comprehensive

**Cons:**
- ⚠️ More complex email template
- ⚠️ Longer emails if many dates

---

### Strategy 4: Database Column Approach (User's Suggestion)
**Concept:**
- Add columns: `borrower_email` and `expected_return_date` to track email sending
- Query by email + date combination
- One email per (email, date) combination

**Implementation:**
1. Add tracking columns (or use existing structure differently)
2. Query overdue items grouped by email + date
3. Track which (email, date) combinations have been emailed

**Pros:**
- ✅ Explicit tracking per email+date
- ✅ Can query directly from database

**Cons:**
- ❌ Requires schema changes
- ❌ More complex
- ❌ Not necessary - can do in application code
- ❌ Data redundancy (email already in borrower table)

---

## Recommendation: Strategy 1 (Group by Borrower Email Only)

**Why:**
1. **Simplest**: Matches how borrow system works (one email per borrower)
2. **User-friendly**: One email per person, not per transaction
3. **No schema changes**: Uses existing structure
4. **Easy to implement**: Just change grouping logic
5. **Flexible email template**: Can show items grouped by date if needed

**Implementation Plan:**
1. Modify `check_and_send_overdue_emails()` to:
   - Group transactions by `borrower.email`
   - Collect all overdue items per borrower
   - Send one email per borrower
   - Mark all their transactions as sent

2. Update email template to handle:
   - Multiple expected return dates (show earliest or all)
   - Multiple transactions' items
   - Clear organization of items

3. Update `send_overdue_notification()` to accept:
   - List of items (can be from multiple transactions)
   - Multiple expected return dates (or earliest date)
   - Days overdue (earliest or range)

---

## Alternative: Strategy 3 (If you want date sections in email)

If you prefer to see items organized by date within one email, we can use Strategy 3 which combines Strategy 1's simplicity with better organization.

---

## Decision Needed

Please choose:
- **Option A**: Strategy 1 - Simple grouping by borrower (one email, all items)
- **Option B**: Strategy 3 - Group by borrower with date sections in email
- **Option C**: Strategy 2 - Separate emails per borrower per date

**Recommendation: Option A (Strategy 1)** - Simplest and most user-friendly.




