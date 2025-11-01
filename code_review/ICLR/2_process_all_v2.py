import openreview
import json
import os
from datetime import datetime
import configparser
import sys
import logging
from operator import itemgetter

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
                invitations = paper.get('invitations', [])
                # Handle both string and list cases for invitations
                
                if isinstance(invitations, list):
                    if any(isinstance(inv, str) and 
                        (inv.endswith('/Official_Review')) 
                        for inv in invitations):
                        list_decisions.append(paper)
            
            

            # Keep only those papers that have highest mdate
            # Sort the papers by mdate in descending order
            
            newlist = sorted(list_decisions, key=itemgetter('mdate'), reverse=True)
            new_list_decisions = []
            for paper in newlist:
                if paper.get('forum') not in [p.get('forum') for p in new_list_decisions]:
                    new_list_decisions.append(paper)
            
            list_decisions = new_list_decisions
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
                invitations = paper.get('invitations', [])
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
                invitations = paper.get('invitations', [])
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
            decision_invitations = paper.get('invitations', "")
            entry['forum'] = decision_forum_id
            if isinstance(decision_invitations, list):
                # Check if any invitation ends with /Decision
                if any(isinstance(inv, str) and inv.endswith('/Official_Review') for inv in decision_invitations):
                        entry["forum"]= decision_forum_id
                        entry["soundness"]= paper["content"].get("soundness", "").get("value", "")
                        entry["presentation"]= paper["content"].get("presentation", "").get("value", "")
                        entry["contribution"]= paper["content"].get("contribution", "").get("value", "")
                        entry["strengths"]= paper["content"].get("strengths", "").get("value", "")
                        entry["weaknesses"]= paper["content"].get("weaknesses", "").get("value", "")
                        entry["questions"]= paper["content"].get("questions", "").get("value", "")
                        entry["limitations"]= paper["content"].get("limitations", {}).get("value", "")
                        entry["rating"]= paper["content"].get("rating", "").get("value", "")
                        entry["confidence"]= paper["content"].get("confidence", "").get("value", "")
                        entry["code_of_conduct"]= paper["content"].get("code_of_conduct", "").get("value", "")
                        entry["flag_for_ethics_review"]= paper["content"].get("flag_for_ethics_review", "").get("value", "")
                        entry["final_rating"]= paper["content"].get("rating", "").get("value", "").split(":")[0] if not isinstance(paper["content"].get("rating", "").get("value", ""), int)  else paper["content"].get("rating", "").get("value", "")
                        
            decision_review = ""
            title_comment = ""
            for review in review_papers:
                review_forum_id = review.get("forum")
                review_invitations = review.get("invitations", "")
                if review_forum_id == decision_forum_id:
                        # print(f"Review forum ID: {review_forum_id}")
                        title = review.get("content", {}).get("title", {}).get("value", "")
                        comment = review.get("content", {}).get("comment", {}).get("value", "")
                        title_comment = f"Title: {title}, Comment: {comment}"
                
                        entry["official_comment"] = f"{title_comment}" if decision_review == "" else f"{decision_review} ; {title_comment}"
                        decision_review = entry["official_comment"]
            
            for submission in submission_papers:
                submission_forum_id = submission.get("forum")
                submission_invitations = submission.get("invitations", [])
                if submission_forum_id == decision_forum_id and isinstance(submission_invitations, list):
                    if any(isinstance(inv, str) and 
                        (inv.endswith('Submission')) 
                        for inv in submission_invitations):
                        title = submission.get("content", {}).get("title", "").get("value", "")
                        abstract = submission.get("content", {}).get("abstract", "").get("value", "")
                        pdf = submission.get("content", {}).get("pdf", "").get("value", "")
                        # print(f"Title: {title}")
                        entry["paper_title"] = title
                        entry["paper_abstract"] = abstract
                        entry["paper_pdf_link"] = pdf
                        break
            
            final_collection.append(entry)
            # print(entry)
            # break
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
    year = 2024  # Change this to the desired year
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
    

    

    