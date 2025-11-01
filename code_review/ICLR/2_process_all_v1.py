import openreview
import json
import os
from datetime import datetime
import configparser
import sys
import logging

class OpenReviewCollector:
    def __init__(self, baseurl='https://api.openreview.net', config_path=None):
        """
        Initialize OpenReview collector with authentication
        
        Args:
            baseurl (str): OpenReview API base URL
            config_path (str): Path to config file containing credentials
        """
        # Try to authenticate using config file
        try:
            if config_path is None:
                config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.ini')
            
            if not os.path.exists(config_path):
                raise FileNotFoundError(f"Config file not found at {config_path}")
                
            config = configparser.ConfigParser()
            config.read(config_path)
            
            username = config['OpenReview']['username']
            password = config['OpenReview']['password']
            
            self.client = openreview.Client(
                baseurl=baseurl,
                username=username,
                password=password
            )
            
            # Verify authentication
            self.client.get_profile()
            print("Successfully authenticated with OpenReview")
            
        except Exception as e:
            print(f"Authentication failed: {str(e)}")
            sys.exit(1)
            
        # Set data directory path relative to script location and create it
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'iclr_data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def collect_decision_papers(self, year, all_data):
        list_decisions = []
        try:
            for paper in all_data:
                invitations = paper.get('invitation', [])
                # Handle both string and list cases for invitations
                if isinstance(invitations, str):
                    if invitations.endswith('/Decision') or invitations.endswith('/Decision'):
                        list_decisions.append(paper)
                elif isinstance(invitations, list):
                    if any(isinstance(inv, str) and 
                        (inv.endswith('/Decision') or inv.endswith('/Decision')) 
                        for inv in invitations):
                        list_decisions.append(paper)

            self.write_json_file(os.path.join(self.data_dir, f'iclr_{year}_all_decision.json'), list_decisions)
            return list_decisions
                
        except Exception as e:
            self.logger.error(f"Error collecting papers: {str(e)}")
            return []
        
    def collect_review_papers(self, year, all_data, list_of_forums):
        official_reviews = []
    
        for paper in all_data:
            # Get the forum ID which links reviews to original papers
            forum_id = paper.get('forum')
            if forum_id in list_of_forums:
                invitations = paper.get('invitation', [])
                # Handle both string and list cases for invitations
                if isinstance(invitations, str):
                    if invitations.endswith('/Official_Comment'):
                        official_reviews.append(paper)
                elif isinstance(invitations, list):
                    if any(isinstance(inv, str) and 
                        (inv.endswith('/Official_Comment')) 
                        for inv in invitations):
                        official_reviews.append(paper)
        
        self.write_json_file(os.path.join(self.data_dir, f'iclr_{year}_all_reviews.json'), official_reviews)
        
        return official_reviews
    def collect_submission_papers(self, year, all_data, list_of_forums):
        submission_papers = []
    
        for paper in all_data:
            # Get the forum ID which links reviews to original papers
            forum_id = paper.get('forum')
            if forum_id in list_of_forums:
                invitations = paper.get('invitation', [])
                # Handle both string and list cases for invitations
                if isinstance(invitations, str):
                    if invitations.endswith('Submission'):
                        submission_papers.append(paper)
                elif isinstance(invitations, list):
                    if any(isinstance(inv, str) and 
                        (inv.endswith('Submission')) 
                        for inv in invitations):
                        submission_papers.append(paper)
        
        self.write_json_file(os.path.join(self.data_dir, f'iclr_{year}_all_submission.json'), submission_papers)
        return submission_papers
    
    def extract_paper_data(self, year, decision_papers, review_papers, submission_papers):  
        final_collection = []
        for paper in decision_papers:
            entry = {}
            decision_forum_id = paper.get('forum')
            entry['forum'] = decision_forum_id
            if paper.get('content') is not None:
                content = paper.get('content')
            
                content["decision_title"] = content.pop("title") if "title" in content else ""
                entry = {**entry, **content}
            
            decision_review = paper.get("official_comment", "")
            title_comment = ""
            for review in review_papers:
                review_forum_id = review.get("forum")
                review_invitations = review.get("invitation", "")
                if review_forum_id == decision_forum_id and review_invitations.endswith('Official_Comment') :
                    title = review.get("content", {}).get("title", "")
                    comment = review.get("content", {}).get("comment", "")
                    title_comment = f"Title: {title}, Comment: {comment}"
            
                    entry["official_comment"] = f"{title_comment}" if decision_review == "" else f"{decision_review} ; {title_comment}"
                    decision_review = entry["official_comment"]
            
            for submission in submission_papers:
                submission_forum_id = submission.get("forum")
                submission_invitations = submission.get("invitation", [])
                if submission_forum_id == decision_forum_id and submission_invitations.endswith('Submission'):
                    title = submission.get("content", {}).get("title", "")
                    abstract = submission.get("content", {}).get("abstract", "")
                    pdf = submission.get("content", {}).get("pdf", "")
                    # print(f"Title: {title}")
                    entry["paper_title"] = title
                    entry["paper_abstract"] = abstract
                    entry["paper_pdf_link"] = pdf
                    break
            
            final_collection.append(entry)
        # Write the final collection to a JSON file
        self.write_json_file(os.path.join(self.data_dir, f'iclr_{year}_all_v1_final_dataset.json'), final_collection)

        return final_collection

    def read_json_file(self, file_path):
       
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            self.logger.error(f"Error reading JSON file: {str(e)}")
            return None
    
    def write_json_file(self, file_path, data):
        
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            # self.logger.info(f"Data written to {file_path}")
        except Exception as e:
            self.logger.error(f"Error writing JSON file: {str(e)}")
        
if __name__ == '__main__':
    collector = OpenReviewCollector()
    year = 2023  # Change this to the desired year
    input_all_file_path = os.path.join(collector.data_dir, f'iclr_{year}_all.json')

    all_data = collector.read_json_file(input_all_file_path)
    print(f"Number of papers in all data: {len(all_data)}")
    
    decision_papers = collector.collect_decision_papers(year, all_data)
    print(f"Number of decision papers: {len(decision_papers)}")

    list_of_forums = [paper['forum'] for paper in decision_papers]
    print(f"Number of unique forums in decision papers: {len(set(list_of_forums))}")
    
    review_papers = collector.collect_review_papers(year, all_data, list_of_forums)
    print(f"Number of review papers: {len(review_papers)}")

    # submission_papers = [paper for paper in all_data if paper['forum'] in list_of_forums and paper ['invitation'] == f'ICLR.cc/{year}/Conference/-/Blind_Submission']
    submission_papers = collector.collect_submission_papers(year, all_data, list_of_forums)
    collector.write_json_file(os.path.join(collector.data_dir, f'iclr_{year}_all_submission.json'), submission_papers)  
    print(f"Number of submission papers: {len(submission_papers)}")

    # Extract and save the metadata of the papers
    final_collection = collector.extract_paper_data(year, decision_papers, review_papers, submission_papers)
    print(f"Number of final collection papers: {len(final_collection)}")
    

    

    