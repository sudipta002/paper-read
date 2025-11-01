import json, os

def filter_decision(list_of_ids, papers_list):
    
    list_decisions = []
    
    for paper in papers_list:
        # Get the forum ID which links reviews to original papers
        forum_id = paper.get('forum')
        invitations = paper.get('invitations', [])
        # print(f"{invitations=}")
            # Handle both string and list cases for invitations
        if isinstance(invitations, str):
            if invitations.endswith('/Official_Review') and forum_id in list_of_ids:
                list_decisions.append(paper)
        elif isinstance(invitations, list):
                # Check if any invitation ends with /Decision
            if any(isinstance(inv, str) and inv.endswith('/Official_Review') 
                      for inv in invitations) and forum_id in list_of_ids:
                list_decisions.append(paper)
    
    return list_decisions

if __name__ == '__main__':
    # # This is for 2023
    # # Load all papers data
    # input_data_path = 'data/neurips_2023_all_v2.json'
    # # Load submission data to get paper forum
    # input_submission_file_path = 'submission_data/neurips_2023_all_v2_blind_submissions.json'
    # output_file_path = 'decision_data/neurips_2023_all_v2_decision.json'

    # This is for 2024
    # Load all papers data
    input_data_path = 'data/neurips_2024_all_v2.json'
    # Load submission data to get paper forum
    input_submission_file_path = 'submission_data/neurips_2024_all_v2_blind_submissions.json'
    output_file_path = 'decision_data/neurips_2024_all_v2_decision.json'
    
    # Load input files   
    with open(input_data_path, 'r') as f:
        papers_list = json.load(f)
    
    with open(input_submission_file_path, 'r') as f:
        submission_data = json.load(f)
    
    # Extract paper IDs from submissions
    list_of_ids = [paper['forum'] for paper in submission_data]
    # print(f"{list_of_ids=}")
    print(f"Found {len(list_of_ids)} paper forums to process")
    
    # Get official reviews
    decisions = filter_decision(list_of_ids, papers_list)
    
    # Create output directory if it doesn't exist
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(os.path.dirname(current_dir), output_file_path)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Save filtered reviews
    with open(output_file, 'w') as f:
        json.dump(decisions, f, indent=2)
    
    print(f"Found {len(decisions)} decisions")
    print(f"Saved to: {output_file}")