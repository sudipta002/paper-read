import os
import json
import pandas as pd

# create a funtion to read json file
def read_json_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

# create a function to write json file
def write_json_file(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def extract_decision_data(decision_data):

    return [
        {
            "forum": decision["forum"],
            "soundness": decision["content"].get("soundness", "").get("value", ""),
            "presentation": decision["content"].get("presentation", "").get("value", ""),
            "contribution": decision["content"].get("contribution", "").get("value", ""),
            "strengths": decision["content"].get("strengths", "").get("value", ""),
            "weaknesses": decision["content"].get("weaknesses", "").get("value", ""),
            "questions": decision["content"].get("questions", "").get("value", ""),
            "limitations": decision["content"].get("limitations", "").get("value", ""),
            "rating": decision["content"].get("rating", "").get("value", ""),
            "confidence": decision["content"].get("confidence", "").get("value", ""),
            "code_of_conduct": decision["content"].get("code_of_conduct", "").get("value", ""),
            "flag_for_ethics_review": decision["content"].get("flag_for_ethics_review", "").get("value", ""),
            "final_rating": decision["content"].get("rating", "").get("value", "").split(":")[0] 
            if not isinstance(decision["content"].get("rating", "").get("value", ""), int)  else decision["content"].get("rating", "").get("value", ""),
        } for decision in decision_data if any(isinstance(inv, str) and inv.endswith('/Official_Review') 
                      for inv in decision["invitations"])

    ]


def get_relevant_reviews(master_data, reviews_data):
    collections = []
    for decision in master_data:
        decision_forum_id = decision.get("forum")
        decision_review = decision.get("official_comment", "")
        title_comment = ""
        for review in reviews_data:
            review_forum_id = review.get("forum")
            review_invitations = review.get("invitations", [])
            if review_forum_id == decision_forum_id and any(inv.endswith('/Official_Comment') for inv in review_invitations):
                title = review.get("content", {}).get("title", {}).get("value", "")
                comment = review.get("content", {}).get("comment", {}).get("value", "")
                title_comment = f"Title: {title}, Comment: {comment}"
        
                decision["official_comment"] = f"{title_comment}" if decision_review == "" else f"{decision_review} ; {title_comment}"
                decision_review = decision["official_comment"]
        collections.append(decision)
    return collections

def get_relevant_submissions(master_data, submission_data):
    collections = []
    for decision in master_data:
        decision_forum_id = decision.get("forum")
        for submission in submission_data:
            submission_forum_id = submission.get("forum")
            submission_invitations = submission.get("invitations", [])
            if submission_forum_id == decision_forum_id and any(inv.endswith('/Submission') for inv in submission_invitations):
                title = submission.get("content", {}).get("title", {}).get("value", "")
                abstract = submission.get("content", {}).get("abstract", {}).get("value", "")
                pdf = submission.get("content", {}).get("pdf", {}).get("value", "")
                # print(f"Title: {title}")
                decision["paper_title"] = title
                decision["paper_abstract"] = abstract
                decision["paper_pdf_link"] = pdf
                collections.append(decision)
                break
    return collections

def write_json_to_csv(file_path, data):
    for item in data:
        if 'official_comment' in item:
            # Replace newlines and multiple spaces
            comment = item['official_comment']
            comment = ' '.join(comment.split())  # Remove extra whitespace
            comment = comment.replace('"', '""')  # Escape double quotes
            comment = comment.replace(';', ',')   # Replace semicolons with commas
            item['official_comment'] = comment
    # write json data to csv file
    df = pd.DataFrame(data, columns=[
        "year",
        "forum", 
        "paper_title", 
        "paper_abstract", 
        "paper_pdf_link", 
        "soundness", 
        "presentation", 
        "contribution", 
        "strengths", 
        "weaknesses", 
        "questions", 
        "limitations", 
        "rating", 
        "confidence", 
        "code_of_conduct", 
        "flag_for_ethics_review",
        "final_rating",
        "official_comment"
    ])
    df.to_csv(file_path, 
              index=False,
              escapechar='\\',
              encoding='utf-8',
              quoting=1,  # Quote all text fields
              quotechar='"',  # Use double quotes
              )

if __name__ == "__main__":
    year = 2023
    #File paths of input files such as decisions, reviews, and submissions
    input_decisions_path = f"decision_data/neurips_{year}_all_v2_decision.json"
    input_submission_file_path = f"submission_data/neurips_{year}_all_v2_blind_submissions.json"
    input_reviews_path = f"review_data/neurips_{year}_all_v2_official_review.json"  
    final_data_file_path = f"final_data/neurips_{year}_all_v2_final_dataset.json"

    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(os.path.dirname(current_dir), final_data_file_path)

    decision_data = read_json_file(input_decisions_path)
    submission_data = read_json_file(input_submission_file_path)
    reviews_data = read_json_file(input_reviews_path)

    print(f"{len(decision_data)=}")
    print(f"{len(submission_data)=}")
    print(f"{len(reviews_data)=}")

    master_data = []
    master_data = extract_decision_data(decision_data)
    print(f"After decision : {len(master_data)=}")
    # print(f"{master_data[0]=}")
    master_data = get_relevant_reviews(master_data, reviews_data)
    print(f"After review : {len(master_data)=}")
    # print(f"{master_data[0]['forum']=}")
    # print(f"{master_data[0]['official_comment']=}")
    master_data = get_relevant_submissions(master_data, submission_data)
    print(f"After submission : {len(master_data)=}")

    # Add year to each entry
    master_data = [
        {**entry, "year": year} for entry in master_data
    ]

    # print(f"{master_data[0]=}")

    write_json_file(output_file, master_data)
    print(f"Final JSON data saved to {output_file}")
    write_json_to_csv(output_file.replace(".json", ".csv"), master_data)
    print(f"Final CSV data saved to {output_file.replace('.json', '.csv')}")