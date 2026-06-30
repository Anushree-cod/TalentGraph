import pdfplumber


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts raw text from a PDF resume.
    
    Args:
        pdf_path: Path to the PDF file.
    
    Returns:
        Extracted text as a single string.
    """
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


# Quick test (only runs when this file is executed directly)
if __name__ == "__main__":
    sample_path = "datasets/sample_resumes/Resume.pdf"
    extracted_text = extract_text_from_pdf(sample_path)
    print(extracted_text)