import openreview
import json
import os
from datetime import datetime
import configparser
import sys
import logging

class OpenReviewCollectorV2:
    def __init__(self, conference, baseurl='https://api2.openreview.net', config_path=None):
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.conference = conference
        
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
            
            self.client = openreview.api.OpenReviewClient(
                baseurl=baseurl,
                username=username,
                password=password
            )
            
            # Verify authentication
            self.client.get_profiles()
            self.logger.info("Successfully authenticated with OpenReview API v2")
            
        except Exception as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            sys.exit(1)
            
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), f'{self.conference}_data')
        os.makedirs(self.data_dir, exist_ok=True)

    def collect_neurips_papers_all(self, year):
        
        try:
            # Get all submissions
            venue_id = f'{conference}.cc/{year}/Conference/.*'
            # venue_id = f'ICLR.cc/{year}/Conference'
            
            papers = self.client.get_all_notes(
            invitation=f'{venue_id}',
            # details='directReplies',
            sort='number:asc',
        )
            self.logger.info(f"Found {len(papers)} papers")
            return papers
            
        except Exception as e:
            self.logger.error(f"Error collecting papers: {str(e)}")
            return []


if __name__ == '__main__':
    
    year = 2024
    conference = 'ICLR'
    collector = OpenReviewCollectorV2(conference)
    # conference = 'iclr'

    
    # Collect papers
    papers = collector.collect_neurips_papers_all(year)
    if papers:
        # Save papers
        with open(os.path.join(collector.data_dir, f'{conference}_{year}_all.json'), 'w') as f:
            json.dump([paper.to_json() for paper in papers], f, indent=2)
        
        print(f"Completed! Collected:")
     
    else:
        print("No papers found")