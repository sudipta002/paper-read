import requests
import os
from urllib.parse import urljoin
import json
import tqdm

# Function to read JSON file
def read_json_file(file_path):
    """
    Read a JSON file and return its content.
    
    Args:
        file_path (str): Path to the JSON file
    
    Returns:
        list: List of dictionaries containing the JSON data
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def download_openreview_paper(year,paper_forum_id,paper_link, output_dir):
    """
    Download a paper PDF from OpenReview given its ID
    
    Args:
        paper_id (str): Paper ID from OpenReview URL
        output_dir (str): Directory to save the downloaded PDF
    
    Returns:
        str: Path to downloaded PDF file or error message
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
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
    # Input file path of final data
    final_data_file_path = f"final_data/neurips_{year}_all_v2_final_dataset.json"
    final_data = read_json_file(final_data_file_path)
    # Get a list of tuples containing paper_forum_id and paper_link
    paper_links = [(item['forum'], item['paper_pdf_link']) for item in final_data]
    # Example paper ID from the given URL
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(os.path.dirname(current_dir), "downloaded_papers")

    # Loop through each paper link and download the paper using tqdm
    for paper_forum_id, paper_link in tqdm.tqdm(paper_links[:5], desc="Downloading papers"):
        downloaded_path = download_openreview_paper(year,paper_forum_id, paper_link, output_dir)