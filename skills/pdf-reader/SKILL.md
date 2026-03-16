---
name: pdf-reader
description: |
  Extract text and metadata from PDF files. Use when tasks require reading PDF invoices,
  contracts, reports, or any PDF documents. Supports PyPDF2 and pdfplumber backends.
  NOT for images or scanned PDFs (OCR required for those).
---

# PDF Reader Skill

Extract text and metadata from PDF files using PyPDF2 or pdfplumber.

## Installation

```bash
pip install PyPDF2 pdfplumber
```

## Quick Reference

### Extract Text from PDF

```bash
# Basic extraction
python AI_Employee_Vault/scripts/skills/pdf_reader.py --input document.pdf

# Create action file in vault
python AI_Employee_Vault/scripts/skills/pdf_reader.py --vault-path AI_Employee_Vault --input document.pdf

# Process all PDFs in Inbox
python AI_Employee_Vault/scripts/skills/pdf_reader.py --vault-path AI_Employee_Vault --process-all
```

### With Qwen

```bash
# Ask Qwen to read a PDF
qwen "Use the pdf-reader skill to extract text from the invoice in Needs_Action"

# Process and summarize
qwen "Read the PDF and summarize the key information (amounts, dates, parties)"
```

## Workflow: PDF Processing

1. Drop PDF in `Inbox/` or locate in `Needs_Action/`
2. Run pdf-reader skill
3. Skill creates action file with extracted text
4. Qwen processes action file
5. Move to `Done/` when complete

## Output Format

Action file created in `Needs_Action/`:

```markdown
---
type: pdf_document
original_name: invoice.pdf
size: 45678
pages: 3
extracted_at: 2026-03-14T10:30:00
status: pending
---

# PDF Document Processed

**Original File:** `invoice.pdf`
**Size:** 44.61 KB
**Pages:** 3

## Extracted Content

--- Page 1 ---
INVOICE #12345
Date: March 1, 2026
Amount: $150.00
...

## Key Information

- **Invoice Number:** #12345
- **Amount:** $150.00
- **Due Date:** March 30, 2026
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Module not found | Run `pip install PyPDF2 pdfplumber` |
| Encrypted PDF | Password-protected PDFs not supported |
| Scanned PDF | Requires OCR (not supported by this skill) |
| Large PDF (>100 pages) | Use `--no-data` flag for summary only |

## Related Skills

- `excel-reader` - Excel file extraction
- `approval-workflow` - Approve invoice payments
- `mcp-email` - Email invoice confirmations
