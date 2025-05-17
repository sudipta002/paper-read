import requests
import os
from urllib.parse import urljoin
import json
import tqdm

# Function to read JSON file
def read_json_file(file_path):
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def download_openreview_paper(year,paper_forum_id,paper_link, output_dir):
   
    try:  
        # Construct the PDF URL
        base_url = "https://openreview.net"
        pdf_url = urljoin(base_url, paper_link)
        
        # Send GET request to download the PDF
        response = requests.get(pdf_url, allow_redirects=True)
        response.raise_for_status()  # Raise exception for 4XX/5XX status codes
        
        paper_name = paper_link.split("/")[-1]
        # Save the PDF
        output_path = os.path.join(output_dir, f"{year}_{paper_forum_id}_{paper_name}")
        with open(output_path, 'wb') as f:
            f.write(response.content)
            
        print(f"Successfully downloaded paper to: {output_path}")
        return output_path
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading paper: {str(e)}")
        return None

if __name__ == "__main__":
    year = 2023
    conference = "neurips"

    pp_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"Parent directory: {pp_dir}")

    # Input file path of final data
    data_file_path = f"final_dataset/{conference}_{year}_all_final_dataset.json"
    input_file_path = os.path.join(pp_dir, data_file_path)
    print(f"Input file path: {input_file_path}")
    final_data = read_json_file(input_file_path)
    print(f"Number of papers in the dataset: {len(final_data)}")
    # Get a list of tuples containing paper_forum_id and paper_link
    paper_links = [(item['forum'], item['paper_pdf_link']) for item in final_data]
    # Example paper ID from the given URL
    
    output_path = f"pdf_dataset/{conference}/{year}"
    output_dir = os.path.join(pp_dir, output_path)
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")
    list_of_files = os.listdir(output_dir)
    print(f"List of files in output directory: {len(list_of_files)}")
    output_paper_ids = [paper_id.split("_")[1] for paper_id in list_of_files]
    # print(f"List of paper IDs in output directory: {output_paper_ids}")

    # Loop through each paper link and download the paper using tqdm
    for paper_forum_id, paper_link in tqdm.tqdm(paper_links[:5], desc="Downloading papers"):
        if paper_forum_id not in output_paper_ids:
            downloaded_path = download_openreview_paper(year,paper_forum_id, paper_link, output_dir)

    list_of_files = os.listdir(output_dir)
    print(f"List of files in output directory: {len(list_of_files)}")