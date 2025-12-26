# Database Restructuring via Excel Upload - Risks and Warnings

## HIGH RISK OPERATION ⚠️

This feature allows restructuring the entire database by uploading a modified Excel file. This is a **DESTRUCTIVE OPERATION** with significant risks.

## Major Risks:

### 1. **Data Loss**
- If components are removed from Excel, they will be deleted from the database
- If borrow items are removed, related data will be lost
- Deleted data cannot be recovered without a backup

### 2. **Data Integrity Violations**
- Invalid foreign key references (e.g., borrow_item references non-existent component)
- Missing required fields
- Invalid data types (e.g., text in numeric fields)
- Duplicate IDs

### 3. **Partial Updates**
- If the upload fails midway, database could be left in inconsistent state
- Transaction rollback helps, but some edge cases may still cause issues

### 4. **ID Conflicts**
- If IDs are manually changed, they might conflict with existing data
- Sequential ID reassignment could break if IDs are not properly handled

### 5. **Concurrent Modifications**
- If database changes between export and import, conflicts could occur
- Data added/modified by other users will be overwritten

### 6. **Referential Integrity**
- Borrow items must reference valid components
- Components must reference valid containers
- Transactions must reference valid borrowers and users

### 7. **Borrow Relationship Integrity**
- Quantity borrowed must not exceed component quantity
- Remaining quantity (borrowed - returned) must be valid
- Component quantities must be accurate after borrow operations

## Safety Measures Implemented:

1. **Automatic Backup** - Backup is created before any changes
2. **Extensive Validation** - All data is validated before applying changes
3. **Preview Mode** - Preview changes before committing
4. **Transaction Management** - All changes in a single transaction (rollback on error)
5. **ID Mapping** - Proper mapping of old IDs to new IDs
6. **Error Reporting** - Detailed error messages for invalid data

## Recommended Workflow:

1. **Export** full database using `/database/export-full`
2. **Review** the Excel file carefully
3. **Make** necessary changes
4. **Validate** data manually before upload
5. **Preview** changes using preview endpoint
6. **Backup** database manually (additional safety)
7. **Upload** and verify results

## Best Practices:

- Always create manual backup before upload
- Test with small changes first
- Verify all relationships are intact
- Check borrow quantities match component quantities
- Ensure no missing required fields
- Validate all IDs are consistent

## Limitations:

- Cannot modify container IDs (containers are not included in restructuring)
- Cannot modify user IDs (users are not included in restructuring)
- Cannot modify borrower IDs (borrowers are referenced but not restructured)
- Component IDs will be reordered sequentially
- Deleted components in Excel will be permanently removed

