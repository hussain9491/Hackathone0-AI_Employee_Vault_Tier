# Excel Reader Skill

> **Tier:** Silver  
> **Status:** Ready to Implement  
> **Dependencies:** openpyxl, pandas (optional)

---

## 📋 Overview

The Excel Reader skill extracts data from Excel files (.xlsx, .xls) dropped in the Inbox. This enables the AI Employee to process spreadsheets, financial reports, inventory lists, and data exports.

**Use Case:** Automatically extract data from Excel reports, budgets, and data exports for processing.

---

## 🎯 Silver Tier Requirement

This skill fulfills:
- ✅ Enhanced file processing capability (Silver tier enhancement)
- ✅ Part of the Perception layer (file content extraction)

---

## 📦 Prerequisites

```bash
pip install openpyxl pandas
```

---

## 🏗️ Implementation

### Excel Reader Script

**File:** `scripts/skills/excel_reader.py`

```python
"""
Excel Reader Skill for AI Employee

Extracts data from Excel files (.xlsx, .xls).

Usage:
    python excel_reader.py --input file.xlsx --output action.md
    python excel_reader.py --vault-path .. --process-all
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class ExcelReader:
    """Extract data from Excel files."""
    
    def __init__(self, vault_path: str = None):
        self.vault_path = Path(vault_path) if vault_path else None
        self.needs_action = self.vault_path / 'Needs_Action' if self.vault_path else None
    
    def extract_data(self, excel_path: str, include_data: bool = True) -> dict:
        """
        Extract data from Excel file.
        
        Args:
            excel_path: Path to Excel file
            include_data: Include full cell data (can be large)
            
        Returns:
            Dict with sheets, dimensions, data summary
        """
        excel_path = Path(excel_path)
        
        if not excel_path.exists():
            return {'error': f'File not found: {excel_path}'}
        
        if not OPENPYXL_AVAILABLE:
            return {'error': 'openpyxl not installed. Run: pip install openpyxl'}
        
        result = {
            'file': excel_path.name,
            'path': str(excel_path),
            'size': excel_path.stat().st_size,
            'sheets': [],
            'extracted_at': datetime.now().isoformat()
        }
        
        try:
            # Load workbook
            wb = openpyxl.load_workbook(excel_path, data_only=True)
            
            # Get sheet names
            result['sheet_names'] = wb.sheetnames
            
            # Extract data from each sheet
            for sheet_name in wb.sheetnames:
                sheet = wb[sheet_name]
                
                sheet_data = {
                    'name': sheet_name,
                    'dimensions': sheet.dimensions,
                    'max_row': sheet.max_row,
                    'max_column': sheet.max_column,
                    'headers': [],
                    'sample_rows': [],
                    'data': [] if include_data else None
                }
                
                # Get headers (first row)
                if sheet.max_row > 0:
                    headers = []
                    for cell in sheet[1]:
                        headers.append(cell.value)
                    sheet_data['headers'] = headers
                
                # Get sample rows (first 5 data rows)
                for i, row in enumerate(sheet.iter_rows(values_only=True), 1):
                    if i <= 5:
                        sheet_data['sample_rows'].append(list(row))
                    elif include_data:
                        sheet_data['data'].append(list(row))
                
                result['sheets'].append(sheet_data)
            
            return result
            
        except Exception as e:
            return {'error': str(e)}
    
    def create_action_file(self, extraction_result: dict) -> Path:
        """
        Create action file from Excel extraction.
        
        Args:
            extraction_result: Result from extract_data()
            
        Returns:
            Path to created action file
        """
        if 'error' in extraction_result:
            raise ValueError(f"Extraction error: {extraction_result['error']}")
        
        # Create filename
        safe_name = "".join(c if c.isalnum() else '_' for c in extraction_result['file'][:30])
        filename = f"EXCEL_{safe_name}.md"
        
        if self.needs_action:
            filepath = self.needs_action / filename
        else:
            filepath = Path(filename)
        
        # Create content
        content = f'''---
type: excel_document
original_name: {extraction_result['file']}
size: {extraction_result['size']}
sheets: {len(extraction_result['sheet_names'])}
extracted_at: {extraction_result['extracted_at']}
status: pending
---

# Excel Document Processed

**Original File:** `{extraction_result['file']}`  
**Size:** {self._format_size(extraction_result['size'])}  
**Sheets:** {len(extraction_result['sheet_names'])}  
**Extracted:** {extraction_result['extracted_at']}

## Sheets Overview

{self._format_sheets_overview(extraction_result)}

## Detailed Sheet Data

{self._format_sheet_details(extraction_result)}

## Suggested Actions

- [ ] Review extracted data
- [ ] Identify key information (totals, trends, anomalies)
- [ ] Take required action
- [ ] Move to /Done when complete

## Key Insights

_Add analysis, summaries, or action items here_

## Notes

_Add any additional notes here_

---
*Extracted by Excel Reader Skill*
'''
        
        filepath.write_text(content)
        return filepath
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def _format_sheets_overview(self, result: dict) -> str:
        """Format sheets overview table."""
        if not result.get('sheets'):
            return '_No sheet data available_'
        
        lines = ['| Sheet | Rows | Columns |', '|-------|------|---------|']
        
        for sheet in result['sheets']:
            lines.append(
                f"| {sheet['name']} | {sheet['max_row']} | {sheet['max_column']} |"
            )
        
        return '\n'.join(lines)
    
    def _format_sheet_details(self, result: dict) -> str:
        """Format detailed sheet data."""
        if not result.get('sheets'):
            return '_No sheet data available_'
        
        sections = []
        
        for sheet in result['sheets']:
            section = f"### {sheet['name']}\n\n"
            
            # Headers
            if sheet['headers']:
                section += f"**Headers:** {', '.join(str(h) for h in sheet['headers'][:10])}"
                if len(sheet['headers']) > 10:
                    section += "..."
                section += "\n\n"
            
            # Sample data
            if sheet['sample_rows']:
                section += "**Sample Data (first 5 rows):**\n\n"
                section += "```\n"
                for row in sheet['sample_rows']:
                    section += " | ".join(str(c) for c in row) + "\n"
                section += "```\n\n"
            
            sections.append(section)
        
        return '\n'.join(sections)
    
    def process_all_excel(self) -> list:
        """Process all Excel files in Inbox."""
        if not self.vault_path:
            raise ValueError("Vault path required for process_all")
        
        inbox = self.vault_path / 'Inbox'
        processed = []
        
        for ext in ['*.xlsx', '*.xls']:
            for excel_file in inbox.glob(ext):
                print(f"Processing: {excel_file.name}")
                
                # Extract data
                result = self.extract_data(excel_file)
                
                if 'error' not in result:
                    # Create action file
                    action_file = self.create_action_file(result)
                    processed.append({
                        'excel': excel_file.name,
                        'action_file': action_file.name
                    })
                    
                    # Copy Excel to Needs_Action
                    import shutil
                    shutil.copy2(excel_file, self.needs_action / excel_file.name)
                else:
                    print(f"  Error: {result['error']}")
        
        return processed


def main():
    parser = argparse.ArgumentParser(description='Excel Reader Skill')
    parser.add_argument('--vault-path', help='Path to Obsidian vault')
    parser.add_argument('--input', help='Input Excel file')
    parser.add_argument('--output', help='Output action file (optional)')
    parser.add_argument('--process-all', action='store_true', help='Process all Excel in Inbox')
    parser.add_argument('--no-data', action='store_true', help='Exclude full data (summary only)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("📊 EXCEL READER SKILL")
    print("=" * 60)
    
    reader = ExcelReader(args.vault_path)
    
    if args.process_all and args.vault_path:
        results = reader.process_all_excel()
        print(f"\n✅ Processed {len(results)} Excel files:")
        for r in results:
            print(f"   {r['excel']} → {r['action_file']}")
    
    elif args.input:
        result = reader.extract_data(args.input, include_data=not args.no_data)
        
        if 'error' in result:
            print(f"\n❌ Error: {result['error']}")
        else:
            print(f"\n✅ Extracted from {result['file']}:")
            print(f"   Sheets: {', '.join(result['sheet_names'])}")
            print(f"   Size: {reader._format_size(result['size'])}")
            
            for sheet in result.get('sheets', [])[:2]:
                print(f"\n📄 Sheet: {sheet['name']}")
                print(f"   Dimensions: {sheet['dimensions']}")
                print(f"   Headers: {sheet['headers'][:5]}...")
            
            if args.output or args.vault_path:
                action_file = reader.create_action_file(result)
                print(f"\n📁 Action file created: {action_file}")


if __name__ == '__main__':
    main()
```

---

## 🚀 Usage

### Process Single Excel File

```bash
cd AI_Employee_Vault/scripts

# Extract data from Excel
python skills/excel_reader.py --input /path/to/report.xlsx

# Create action file in vault
python skills/excel_reader.py --vault-path .. --input /path/to/report.xlsx
```

### Process All Excel Files

```bash
# Drop Excel files in Inbox, then run:
python skills/excel_reader.py --vault-path .. --process-all
```

### With Qwen

```bash
qwen "Use the Excel reader skill to extract data from the budget spreadsheet"
```

---

## 📁 Example Output

```markdown
---
type: excel_document
original_name: budget_2026.xlsx
size: 28456
sheets: 3
extracted_at: 2026-03-14T10:30:00
status: pending
---

# Excel Document Processed

**Original File:** `budget_2026.xlsx`  
**Size:** 27.79 KB  
**Sheets:** 3  
**Extracted:** 2026-03-14T10:30:00

## Sheets Overview

| Sheet | Rows | Columns |
|-------|------|---------|
| Income | 25 | 8 |
| Expenses | 50 | 10 |
| Summary | 10 | 5 |

## Detailed Sheet Data

### Income

**Headers:** Month, Category, Amount, Notes, Status, Approved By, Date, ID

**Sample Data (first 5 rows):**

```
January | Sales | 15000 | Q1 revenue | Approved | John | 2026-01-15 | 001
January | Services | 5000 | Consulting | Approved | Jane | 2026-01-20 | 002
February | Sales | 18000 | Q1 revenue | Approved | John | 2026-02-15 | 003
```

### Expenses

**Headers:** Date, Category, Vendor, Amount, Payment Method, Receipt, Notes, Approved, Paid Date, ID

**Sample Data (first 5 rows):**

```
2026-01-05 | Utilities | Electric Co | 150 | Bank Transfer | Yes | Office | Yes | 2026-01-10 | E001
```

## Suggested Actions

- [ ] Review extracted data
- [ ] Identify budget variances
- [ ] Flag unusual expenses
- [ ] Move to /Done when complete

## Key Insights

- Total Income (Q1): $XX,XXX
- Total Expenses (Q1): $XX,XXX
- Net: $XX,XXX
- Largest expense category: Utilities

---
*Extracted by Excel Reader Skill*
```

---

## 🔗 Related Skills

| Skill | Purpose |
|-------|---------|
| `pdf_reader_skill.md` | PDF file extraction |
| `approval_workflow_skill.md` | Approve budget items |
| `scheduler_skill.md` | Scheduled report generation |

---

*Skill Version: 1.0*  
*Last Updated: 2026-03-14*  
*Silver Tier Component*
