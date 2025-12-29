# Batch Return Implementation Plan

## Current System
- **Single Return**: One component at a time
- **Email**: One email per component return
- **Flow**: Click return → Fill form → Submit → Email sent immediately

## Problem
- If returning 10 components, user must click return 10 times
- 10 separate emails sent (spam)

## Solution: Batch Return System

### Backend Changes

#### 1. New Batch Return Endpoint
**Endpoint**: `POST /returns/batch`

**Request Body**:
```json
{
  "pic_name": "John Doe",
  "items": [
    {
      "transaction_id": 1,
      "component_id": 5,
      "quantity": 3,
      "remarks": "Optional remarks for this item"
    },
    {
      "transaction_id": 1,
      "component_id": 7,
      "quantity": 2,
      "remarks": "Another item"
    }
  ]
}
```

**Logic**:
- Process all items in one transaction
- Create ReturnEvent for each item
- Update quantities
- Check if transactions are completed
- Send ONE email with all returned items grouped by borrower

#### 2. Keep Single Return Endpoint (for backward compatibility)
- Keep existing `POST /returns/` endpoint
- Can be used for single returns or migrated to use batch internally

#### 3. Email Service Update
- Update `send_return_notification()` to handle multiple items
- Group items by borrower (if multiple borrowers in batch)
- Show all items in one email per borrower

### Frontend Changes

#### 1. Return Modal Enhancement
**Current**: Single component form
**New**: Multi-component form with "Add More Items" functionality

**Features**:
- Initial item (from clicked return button)
- "Add Another Item" button
- Item selector dropdown (showing borrower's other borrowed items)
- Each item row has:
  - Component name (read-only)
  - Quantity input (with "Return All" checkbox)
  - Remarks input
  - Remove button
- Shared PIC field (applies to all items)
- Submit button processes all items at once

#### 2. UI Flow
1. User clicks "Return" on Component A
2. Modal opens with Component A pre-filled
3. User can:
   - Fill PIC, quantity, remarks for Component A
   - Click "Add Another Item"
   - Select Component B from dropdown
   - Fill quantity and remarks for Component B
   - Repeat for more components
4. Click "Return All" → Sends batch request
5. ONE email sent with all items

### Data Structure

#### Batch Return Schema
```python
class ReturnItemCreate(BaseModel):
    transaction_id: int
    component_id: int
    quantity: int
    remarks: Optional[str] = None

class BatchReturnCreate(BaseModel):
    pic_name: str
    items: List[ReturnItemCreate]
```

### Email Grouping Logic

**Group by Borrower**:
- If batch contains items from same borrower → ONE email
- If batch contains items from different borrowers → ONE email per borrower
- All items in email grouped together (same as overdue system)

### Implementation Steps

1. ✅ Create batch return schema
2. ✅ Create batch return endpoint
3. ✅ Update email service to handle multiple items
4. ✅ Update frontend return modal
5. ✅ Add "Add Another Item" functionality
6. ✅ Update API call to use batch endpoint
7. ✅ Test with multiple items

### Backward Compatibility

- Keep single return endpoint working
- Frontend can use either:
  - Single return for quick returns
  - Batch return for multiple items

### Benefits

- ✅ One email per borrower (no spam)
- ✅ Faster workflow (return multiple items at once)
- ✅ Better UX (add items to batch)
- ✅ Same PIC for all items (unless different borrower)




