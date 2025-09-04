import logging
from pathlib import Path
import pdfplumber
from bs4 import BeautifulSoup

def parse(raw_file_path: str, output_path: str):
    """
    Parses a raw document (PDF or HTML) to extract plain text.

    This functional implementation uses pdfplumber for PDFs and BeautifulSoup
    for HTML files to extract their text content.

    Args:
        raw_file_path (str): The path to the raw input file.
        output_path (str): The path to save the extracted plain text.
    """
    logging.info(f"Parsing file '{raw_file_path}'...")

    try:
        input_path = Path(raw_file_path)
        file_type = input_path.suffix.lower()
        parsed_text = ""

        if file_type == '.pdf':
            logging.info("Detected PDF file. Parsing with pdfplumber.")
            with pdfplumber.open(input_path) as pdf:
                all_text = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        all_text.append(text)
                parsed_text = "\n".join(all_text)
            if not parsed_text:
                logging.warning(f"pdfplumber extracted no text from '{raw_file_path}'. The PDF might be image-based.")
                # Future enhancement: Fallback to OCR (pytesseract) here.
                parsed_text = "No text could be extracted. The PDF may only contain images."

        elif file_type == '.html':
            logging.info("Detected HTML file. Parsing with BeautifulSoup.")
            with open(input_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'lxml')
                # A simple way to get all text. A more sophisticated approach might
                # target specific elements like forms, labels, and inputs.
                parsed_text = soup.get_text(separator='\n', strip=True)

        else:
            logging.warning(f"Unrecognized file type '{file_type}' for parsing. Skipping.")
            parsed_text = f"Unsupported file type: {file_type}"

        # Write the extracted text to the output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(parsed_text)

        logging.info(f"Successfully parsed text and saved to '{output_path}'.")

    except FileNotFoundError:
        logging.error(f"Raw file not found at '{raw_file_path}'.")
        raise
    except Exception as e:
        logging.error(f"Failed to parse file '{raw_file_path}'. Error: {e}", exc_info=True)
        raise
