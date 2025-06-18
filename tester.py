
import google.generativeai as genai
import requests
import os
#Use existing chromadb vector db to search sematnically similar text based on embeddings of the input query which is done using aipipe token
import chromadb
from chromadb.config import Settings
# Initialize the ChromaDB client
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))  # Set your GenAI API key

vision_model=genai.GenerativeModel(model_name="gemini-2.0-flash")  
# Check if the cmd is right


#Importing collection from embed module
# Ensure the chroma_db directory exists

#Why create client when collection is already imported?
  
#THe databse already exists and is persisted in the directory chroma_db

# Get the collection



#Configure the above command in script to get the embeddings of the input query
#Dont use helper
# Function to get embeddings for a query using the AIPipe API
# This function fetches embeddings for a given query using the AIPipe API.




AIPIPE_TOKEN = os.getenv('AIPIPE_TOKEN')


def get_embeddings(query):
    
    url = 'https://aipipe.org/openai/v1/embeddings'  # API endpoint for embeddings
    data = {
        "model": "text-embedding-3-small",
        "input": query
    }
    
    # Set the headers for the request
    
    headers=dict()
    headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + AIPIPE_TOKEN
}

    # Make the request to the AIPipe API
    response = requests.post(url, json=data, headers=headers)  
    
    if response.status_code == 200:
        return response.json()['data'][0]['embedding']
    else:
        raise Exception("Error fetching embeddings: " + response.text)
    
def get_response(prompt):
    #Use AIPIPE to get response for the prompt
    url = 'https://aipipe.org/openai/v1/responses' 
    
    data = {
        "model": "gpt-4.1-nano",
        "input": prompt
    }
    headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + AIPIPE_TOKEN
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()['output'][0]['content'][0]['text']
    else:
        raise Exception("Error fetching response: " + response.text)

#query=input("Enter question")
#embeddings = get_embeddings(query)
# Search the collection with the embeddings
#search_collection(embeddings, top_k=7)


# The error indicates that headers is being treated as a set instead of a dictionary.
#Done using headers=dict()


