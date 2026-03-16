# PDF Reader Skill

> **Tier:** Silver  
> **Status:** Ready to Implement  
> **Dependencies:** PyPDF2 or pdfplumber

---

## 📋 Overview

The PDF Reader skill extracts text and metadata from PDF files dropped in the Inbox. This enables the AI Employee to process invoices, contracts, reports, and other PDF documents.

**Use Case:** Automatically extract text from PDF invoices, contracts, and reports for processing.

---

## 🎯 Silver Tier Requirement

This skill fulfills:
- ✅ Enhanced file processing capability (Silver tier enhancement)
- ✅ Part of the Perception layer (file content extraction)

---

## 📦 Prerequisites

```bash
pip install PyPDF2 pdfplumber
```

---

## 🏗️ Implementation

### PDF Reader Script

**File:** `scripts/skills/pdf_reader.py`

```python
"""
PDF Reader Skill for AI Employee

Extracts text and metadata from PDF files.

Usage:
    python pdf_reader.py --input file.pdf --output action.md
    python pdf_reader.py --vault-path .. --process-all
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    from PyPDF2 import PdfReader
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False


class PDFReader:
    """Extract text and metadata from PDFs."""
    
    def __init__(self, vault_path: str = None):
        self.vault_path = Path(vault_path) if vault_path else None
        self.needs_action = self.vault_path / 'Needs_Action' if self.vault_path else None
    
    def extract_text(self, pdf_path: str, method: str = 'pdfplumber') -> dict:
        """
        Extract text from PDF.
        
        Args:
            pdf_path: Path to PDF file
            method: 'pdfplumber' or 'pypdf2'
            
        Returns:
            Dict with text, metadata, page_count
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            return {'error': f'File not found: {pdf_path}'}
        
        result = {
            'file': pdf_path.name,
            'path': str(pdf_path),
            'size': pdf_path.stat().st_size,
            'pages': 0,
            'text': '',
            'metadata': {},
            'extracted_at': datetime.now().isoformat()
        }
        
        try:
            if method == 'pdfplumber' and PDFPLUMBER_AVAILABLE:
                return self._extract_with_pdfplumber(pdf_path, result)
            elif PYPDF2_AVAILABLE:
                return self._extract_with_pypdf2(pdf_path, result)
            else:
                return {'error': 'No PDF library available. Install pdfplumber or PyPDF2.'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def _extract_with_pdfplumber(self, pdf_path: Path, result: dict) -> dict:
        """Extract using pdfplumber (better for tables)."""
        with pdfplumber.open(pdf_path) as pdf:
            result['pages'] = len(pdf.pages)
            result['metadata'] = pdf.metadata or {}
            
            text_pages = []
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ''
                text_pages.append(f"--- Page {i+1} ---\n{text}")
            
            result['text'] = '\n\n'.join(text_pages)
        
        return result
    
    def _extract_with_pypdf2(self, pdf_path: Path, result: dict) -> dict:
        """Extract using PyPDF2."""
        reader = PdfReader(pdf_path)
        result['pages'] = len(reader.pages)
        result['metadata'] = reader.metadata or {}
        
        text_pages = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ''
            text_pages.append(f"--- Page {i+1} ---\n{text}")
        
        result['text'] = '\n\n'.join(text_pages)
        return result
    
    def create_action_file(self, extraction_result: dict) -> Path:
        """
        Create action file from PDF extraction.
        
        Args:
            extraction_result: Result from extract_text()
            
        Returns:
            Path to created action file
        """
        if 'error' in extraction_result:
            raise ValueError(f"Extraction error: {extraction_result['error']}")
        
        # Create filename
        safe_name = "".join(c if c.isalnum() else '_' for c in extraction_result['file'][:30])
        filename = f"PDF_{safe_name}.md"
        
        if self.needs_action:
            filepath = self.needs_action / filename
        else:
            filepath = Path(filename)
        
        # Create content
        content = f'''---
type: pdf_document
original_name: {extraction_result['file']}
size: {extraction_result['size']}
pages: {extraction_result['pages']}
extracted_at: {extraction_result['extracted_at']}
status: pending
---

# PDF Document Processed

**Original File:** `{extraction_result['file']}`  
**Size:** {self._format_size(extraction_result['size'])}  
**Pages:** {extraction_result['pages']}  
**Extracted:** {extraction_result['extracted_at']}

## Metadata

{self._format_metadata(extraction_result.get('metadata', {}))}

## Extracted Content

{extraction_result['text'][:10000]}{'...' if len(extraction_result['text']) > 10000 else ''}

## Suggested Actions

- [ ] Review extracted content
- [ ] Identify key information (dates, amounts, names)
- [ ] Take required action
- [ ] Move to /Done when complete

## Key Information

_Add extracted dates, amounts, parties, etc._

## Notes

_Add any additional notes here_

---
*Extracted by PDF Reader Skill*
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
    
    def _format_metadata(self, metadata: dict) -> str:
        """Format PDF metadata."""
        if not metadata:
            return '_No metadata available_'
        
        lines = []
        for key, value in metadata.items():
            clean_key = key.replace('/', '').replace('_', ' ').title()
            if value:
                lines.append(f"- **{clean_key}:** {value}")
        
        return '\n'.join(lines) if lines else '_No metadata available_'
    
    def process_all_pdfs(self) -> list:
        """Process all PDFs in Inbox."""
        if not self.vault_path:
            raise ValueError("Vault path required for process_all")
        
        inbox = self.vault_path / 'Inbox'
        processed = []
        
        for pdf_file in inbox.glob('*.pdf'):
            print(f"Processing: {pdf_file.name}")
            
            # Extract text
            result = self.extract_text(pdf_file)
            
            if 'error' not in result:
                # Create action file
                action_file = self.create_action_file(result)
                processed.append({
                    'pdf': pdf_file.name,
                    'action_file': action_file.name
                })
                
                # Move PDF to Needs_Action
                import shutil
                shutil.copy2(pdf_file, self.needs_action / pdf_file.name)
            else:
                print(f"  Error: {result['error']}")
        
        return processed


def main():
    parser = argparse.ArgumentParser(description='PDF Reader Skill')
    parser.add_argument('--vault-path', help='Path to Obsidian vault')
    parser.add_argument('--input', help='Input PDF file')
    parser.add_argument('--output', help='Output action file (optional)')
    parser.add_argument('--process-all', action='store_true', help='Process all PDFs in Inbox')
    parser.add_argument('--method', default='pdfplumber', choices=['pdfplumber', 'pypdf2'])
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("📄 PDF READER SKILL")
    print("=" * 60)
    
    reader = PDFReader(args.vault_path)
    
    if args.process_all and args.vault_path:
        results = reader.process_all_pdfs()
        print(f"\n✅ Processed {len(results)} PDFs:")
        for r in results:
            print(f"   {r['pdf']} → {r['action_file']}")
    
    elif args.input:
        result = reader.extract_text(args.input, args.method)
        
        if 'error' in result:
            print(f"\n❌ Error: {result['error']}")
        else:
            print(f"\n✅ Extracted from {result['file']}:")
            print(f"   Pages: {result['pages']}")
            print(f"   Size: {reader._format_size(result['size'])}")
            print(f"\n📄 First 500 chars:\n{result['text'][:500]}...")
            
            if args.output or args.vault_path:
                action_file = reader.create_action_file(result)
                print(f"\n📁 Action file created: {action_file}")


if __name__ == '__main__':
    main()
```

---

## 🚀 Usage

### Process Single PDF

```bash
cd AI_Employee_Vault/scripts

# Extract text from PDF
python skills/pdf_reader.py --input /path/to/invoice.pdf

# Create action file in vault
python skills/pdf_reader.py --vault-path .. --input /path/to/invoice.pdf
```

### Process All PDFs in Inbox

```bash
# Drop PDFs in Inbox, then run:
python skills/pdf_reader.py --vault-path .. --process-all
```

### With Qwen

```bash
qwen "Use the PDF reader skill to extract text from the invoice in Needs_Action"
```

---

## 📁 Example Output

```markdown
---
type: pdf_document
original_name: invoice_march_2026.pdf
size: 45678
pages: 3
extracted_at: 2026-03-14T10:30:00
status: pending
---

# PDF Document Processed

**Original File:** `invoice_march_2026.pdf`  
**Size:** 44.61 KB  
**Pages:** 3  
**Extracted:** 2026-03-14T10:30:00

## Metadata

- **Title:** Invoice #12345
- **Author:** Electric Company
- **Creation Date:** March 1, 2026

## Extracted Content

--- Page 1 ---
INVOICE #12345
Date: March 1, 2026
Due: March 30, 2026

Bill To:
Your Company Name
123 Main Street

--- Page 2 ---
Services Rendered:
- Electricity (Feb 2026): $150.00
- Service Fee: $5.00
Total: $155.00

--- Page 3 ---
Payment Instructions...

## Suggested Actions

- [ ] Review extracted content
- [ ] Identify key information (dates, amounts, names)
- [ ] Create payment approval request
- [ ] Move to /Done when complete

## Key Information

- **Invoice Number:** #12345
- **Amount:** $155.00
- **Due Date:** March 30, 2026
- **Vendor:** Electric Company

---
*Extracted by PDF Reader Skill*
```

---

## 🔗 Related Skills

| Skill | Purpose |
|-------|---------|
| `excel_reader_skill.md` | Excel file extraction |
| `approval_workflow_skill.md` | Approve invoice payments |
| `mcp_email_skill.md` | Email invoice confirmations |

---

*Skill Version: 1.0*  
*Last Updated: 2026-03-14*  
*Silver Tier Component*
