import sys
import os
from pathlib import Path

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from docs.doc_generator import DocGenerator

def main():
    print("Testing sequence initialized for DocGenerator...")
    gen = DocGenerator()
    code = "def authenticate(user, password):\n    if password == '12345': # DO NOT DO THIS\n        return True\n    return False"
    readme = gen.generate_readme(code, "Python", "TestProject")
    
    print("1. README output:")
    print("-" * 20)
    print(readme.strip())
    print("-" * 20)
    
    print("\n2. Generating Word Doc...")
    docx_path = gen.generate_word_doc(code, readme, "TestProject")
    print(f"Created docx at: {docx_path}")
    
    print("\n3. Generating PDF Doc...")
    pdf_path = gen.generate_pdf(code, readme, "TestProject")
    print(f"Created pdf at: {pdf_path}")
    
    print("\n4. Testing doc formatting fix...")
    res = gen.fix_document_formatting(docx_path)
    print(f"Fixed formatting result: {res}")
    
    print("\nAll Tests Complete & Successful!")

if __name__ == "__main__":
    main()
