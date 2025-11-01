import json, os
def filter_blind_submissions(papers_list):
    """
    Filter papers to get only blind submissions
    
    Args:
        papers_list (list): List of paper dictionaries from OpenReview
        
    Returns:
        list: Filtered list containing only blind submissions
    """
    blind_submissions = []
    
    for paper in papers_list:
        invitation = paper.get('invitations', [])
        # Convert invitation to a dictionary if it's a string
        # Handle both string and list cases
        if isinstance(invitation, str):
            if 'submission' in invitation.lower():
                blind_submissions.append(paper)
        elif isinstance(invitation, list):
            # Check if any element in the invitation list ends with '/Submission'
            if any(isinstance(inv, str) and inv.endswith('/Submission') for inv in invitation):
                blind_submissions.append(paper)
    
    
    return blind_submissions

# Usage example:
if __name__ == '__main__':
    # This is for 2023
    # input_file_path = 'data/neurips_2023_all_v2.json'
    # output_file_path = 'processed_data/neurips_2023_all_v2_blind_submissions.json'

    # This is for 202
    input_file_path = 'data/neurips_2024_all_v2.json'
    output_file_path = 'submission_data/neurips_2024_all_v2_blind_submissions.json'
    # Load input file   
    with open(input_file_path, 'r') as f:
        papers = json.load(f)
    # Assuming you have your papers loaded in a variable called 'papers'
    blind_papers = filter_blind_submissions(papers)
    
    # Get current working directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Save filtered papers to a new JSON file
    output_file = os.path.join(os.path.dirname(current_dir), output_file_path)
    with open(output_file, 'w') as f:
        json.dump(blind_papers, f, indent=2)
    
    print(f"Found {len(blind_papers)}  submissions")