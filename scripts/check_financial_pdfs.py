"""Check which UDC financial PDFs exist"""
import os

data_dir = "D:/udc/data"
all_pdfs = [f for f in os.listdir(data_dir) if f.endswith('.pdf')]

# Exclude non-financial PDFs
exclude_patterns = ['salary', 'labour', 'labor', 'qnds', 'curriculum', 'cooper', 'nadia', 'aventus', 'pr-middle']

financial_pdfs = []
excluded_pdfs = []

for pdf in all_pdfs:
    if any(pattern in pdf.lower() for pattern in exclude_patterns):
        excluded_pdfs.append(pdf)
    else:
        financial_pdfs.append(pdf)

print("UDC FINANCIAL PDFs:")
print("="*80)
for i, pdf in enumerate(sorted(financial_pdfs), 1):
    size = os.path.getsize(os.path.join(data_dir, pdf)) / (1024*1024)
    print(f"{i:2}. {pdf:70} ({size:.1f} MB)")

print(f"\nTotal Financial PDFs: {len(financial_pdfs)}")
print(f"\nExcluded (Non-Financial): {len(excluded_pdfs)}")
