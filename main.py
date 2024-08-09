import requests
import time
import random
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API URLs and models from environment variables
API_URLS = [os.getenv(f"API_URL_{i}") for i in range(1, 61)]
MODELS = [os.getenv(f"MODEL_{i}") for i in range(1, 61)]

def ask_question(api_url, model, question):
    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful, respectful, and honest assistant. Always answer accurately, while being safe."},
            {"role": "user", "content": question}
        ],
        "model": model
    }
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response content: {response.content}")
    except Exception as err:
        print(f"Other error occurred: {err}")
    
    return None

def save_response_to_file(response, folder, index):
    try:
        # Extract the assistant's answer from the response
        answer = response['choices'][0]['message']['content']
        filename = os.path.join(folder, f"response_{index}.txt")
        with open(filename, 'w') as file:
            file.write(answer)
        print(f"Response saved to {filename}")
    except Exception as e:
        print(f"Failed to save response to file: {e}")

def read_random_question(filename):
    try:
        with open(filename, 'r') as file:
            questions = file.readlines()
            question = random.choice(questions).strip()
        return question
    except Exception as e:
        print(f"Failed to read questions from file: {e}")
        return None

def extract_question_from_response(response):
    try:
        # Assuming the response is a paragraph or sentence, extract the last sentence to form a new question
        answer = response['choices'][0]['message']['content']
        sentences = answer.split('.')
        if len(sentences) > 1:
            new_question = sentences[-2].strip() + '?'  # Use the second last sentence as the new question
        else:
            new_question = sentences[0].strip() + '?'
        return new_question
    except Exception as e:
        print(f"Failed to extract question from response: {e}")
        return None

def save_individual_question_to_file(question, folder, index):
    try:
        filename = os.path.join(folder, f"generated_question_{index}.txt")
        with open(filename, 'w') as file:
            file.write(question)
        print(f"Individual question saved to {filename}")
    except Exception as e:
        print(f"Failed to save individual question to file: {e}")

if __name__ == "__main__":
    # Create a directory based on the current timestamp inside 'logs'
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    log_folder = "logs"
    os.makedirs(os.path.join(log_folder, timestamp), exist_ok=True)
    timestamp_folder = os.path.join(log_folder, timestamp)
    
    i = 0
    for index, (api_url, model) in enumerate(zip(API_URLS, MODELS), start=1):
        print(f"Request to API #{index}")
        question = read_random_question("questions.txt")
        if question:
            response = ask_question(api_url, model, question)
            if response:
                save_response_to_file(response, timestamp_folder, i + 1)
                # Get the next question from the response
                question = extract_question_from_response(response)
                if not question:
                    print("Failed to extract a new question from the response. Exiting loop.")
                    break
                i += 1
                save_individual_question_to_file(question, timestamp_folder, i)
            else:
                print(f"Failed to get a response in iteration {i}.")
                break
            delay = random.randint(200, 600)  # Random time between 100 to 1500 seconds (adjustable)
            print(f"Sleeping for {delay} seconds before the next API call.")
            time.sleep(delay)
        else:
            print("No valid question found. Exiting.")
            break
