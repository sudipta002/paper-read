import json
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams
import re
import os

def extract_paper_sections(pdf_path):
    # Extract text from PDF
    text = extract_text(pdf_path, laparams=LAParams())
    
    # Initialize dictionary for paper sections
    paper_data = {
        "title": "",
        "abstract": "",
        "introduction": "",
        "methodology": "",
        "results": "",
        "conclusion": "",
        "references": []
    }
    
    # Split text into sections (basic approach)
    sections = text.split('\n\n')
    
    # Simple rules to identify sections
    for section in sections:
        section = section.strip()
        section_lower = section.lower()
        
        if section_lower.startswith('abstract'):
            paper_data['abstract'] = section
        elif section_lower.startswith('introduction'):
            paper_data['introduction'] = section
        elif section_lower.startswith('method') or section_lower.startswith('methodology'):
            paper_data['methodology'] = section
        elif section_lower.startswith('result'):
            paper_data['results'] = section
        elif section_lower.startswith('conclusion'):
            paper_data['conclusion'] = section
        elif section_lower.startswith('references'):
            # Extract references
            refs = section.split('\n')[1:]  # Skip the "References" header
            paper_data['references'] = [ref.strip() for ref in refs if ref.strip()]
        elif not paper_data['title'] and len(section.split()) < 20:
            # Assume first short section is title
            paper_data['title'] = section

    return paper_data

def convert_pdf_to_json(pdf_path, output_json_path):
    # Extract paper data
    paper_data = extract_paper_sections(pdf_path)
    
    # Save to JSON file
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(paper_data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    year = 2023

    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(os.path.dirname(current_dir), "downloaded_papers")
    # list of all pdf files in the directory that start with the year
    pdf_files = [f for f in os.listdir(input_dir) if f.endswith('.pdf') and f.startswith(str(year))]
    output_dir = os.path.join(os.path.dirname(current_dir), "json_papers")
    os.makedirs(output_dir, exist_ok=True)
    # Convert each PDF to JSON  
    for pdf_file in pdf_files:
        pdf_path = os.path.join(input_dir, pdf_file)
        json_file_name = os.path.splitext(pdf_file)[0] + '.json'
        output_json_path = os.path.join(output_dir, json_file_name)
        convert_pdf_to_json(pdf_path, output_json_path)
        print(f"Converted {pdf_file} to {json_file_name}")
        # Check if the JSON file was created successfully
        if os.path.exists(output_json_path):
            print(f"Successfully created {json_file_name}")
        else:
            print(f"Failed to create {json_file_name}")
