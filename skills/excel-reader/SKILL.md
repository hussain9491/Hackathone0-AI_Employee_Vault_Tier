---
name: excel-reader
description: |
  Extract data from Excel files (.xlsx, .xls). Use when tasks require reading
  spreadsheets, financial reports, inventory lists, or data exports. Supports
  openpyxl and pandas backends.
---

# Excel Reader Skill

Extract data from Excel files using openpyxl and pandas.

## Installation

```bash
pip install openpyxl pandas
```

## Quick Reference

### Extract Data from Excel

```bash
# Basic extraction
python AI_Employee_Vault/scripts/skills/excel_reader.py --input report.xlsx

# Summary only (no full data)
python AI_Employee_Vault/scripts/skills/excel_reader.py --input report.xlsx --no-data

# Process all Excel files in Inbox
python AI_Employee_Vault/scripts/skills/excel_reader.py --vault-path AI_Employee_Vault --process-all
```

### With Qwen

```bash
# Ask Qwen to read Excel
qwen "Use the excel-reader skill to extract data from the budget spreadsheet"

# Analyze data
qwen "Read the Excel file and identify trends, totals, and anomalies"
```

## Workflow: Excel Processing

1. Drop Excel file in `Inbox/`
2. Run excel-reader skill
3. Skill creates action file with sheet data
4. Qwen processes and analyzes data
5. Move to `Done/` when complete

## Output Format

Action file created in `Needs_Action/`:

```markdown
---
type: excel_document
original_name: budget.xlsx
size: 28456
sheets: 3
extracted_at: 2026-03-14T10:30:00
status: pending
---

# Excel Document Processed

**Original File:** `budget.xlsx`
**Size:** 27.79 KB
**Sheets:** 3

## Sheets Overview

| Sheet | Rows | Columns |
|-------|------|---------|
| Income | 25 | 8 |
| Expenses | 50 | 10 |
| Summary | 10 | 5 |

## Detailed Sheet Data

### Income
**Headers:** Month, Category, Amount, Notes
**Sample Data:**
```
January | Sales | 15000 | Q1 revenue
February | Sales | 18000 | Q1 revenue
```
```

## Supported Formats

- `.xlsx` - Excel 2007+ (recommended)
- `.xls` - Excel 97-2003 (limited support)
- `.xlsm` - Excel with macros (data only)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Module not found | Run `pip install openpyxl pandas` |
| Corrupted file | Try opening in Excel first |
| Very large file | Use `--no-data` for summary only |
| Formulas showing | Skill uses `data_only=True` for calculated values |

## Related Skills

- `pdf-reader` - PDF file extraction
- `approval-workflow` - Approve budget items
- `scheduler` - Scheduled report generation
