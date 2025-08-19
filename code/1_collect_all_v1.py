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

    def collect_papers(self, year):
        """
        Collect NeurIPS papers from OpenReview for a specific year
        
        Args:
            year (int): Year of the conference (default: 2023)
        """
        try:
            # Get all submissions
            invitation = f'ICLR.cc/{year}/Conference/.*'
            papers = self.client.get_all_notes(invitation=invitation)
            self.logger.info(f"Found {len(papers)} papers")

            papers_data = [paper.to_json() for paper in papers]
            with open(os.path.join(collector.data_dir, f'iclr_{year}_all.json'), 'w') as f:
                json.dump(papers_data, f, indent=2)

            return papers
            
        except Exception as e:
            self.logger.error(f"Error collecting papers: {str(e)}")
            return []


if __name__ == '__main__':
    collector = OpenReviewCollector()
    year = 2024  # Change this to the desired year
    
    # Collect papers
    papers = collector.collect_papers(year)
    if not papers:
        sys.exit(1)
    
    # Save blind submissions to JSON
    

    