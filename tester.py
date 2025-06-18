from embed import collection
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


def search_collection(embeddings, top_k=7):
    #Code for directly querying with embeddings
    #Assume query_text has query embeddings
    # Get embeddings for the query
    # Perform the query on the collection
    results = collection.query(query_embeddings=[embeddings], n_results=top_k)
    # Extract the documents from the results
    print(results.keys())
    print("Results:", results)
    documents = results['documents'][0] if results['documents'] else []
    print(documents)
    prompt = f"""You are an expert assistant on the Tools in Data Science course of IITM BS Data Science degree. Use the following context to answer the question below. For direct questions requiring a specific answer (like for when and where type questions -- try to answer the specific date or time or place), be more detailed and make sure to answer the question with a more strong reply including the required parametric answer.
    Think step by step and answer the question in a detailed manner. If the question is about a specific date or time, provide that information clearly.
    Be precise and clear in your answers and make sure to be contextual and relative to the user's query. Give more importance to the text present in image queries if any and try to answer them.
    Context:
    {documents}

    Question:
    {query}

    Answer:"""
    response= vision_model.generate_content(prompt, generation_config={"temperature": 0.3})
    print(response.candidates[0].content.parts[0].text)

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

query=input("Enter question")
embeddings = get_embeddings(query)
# Search the collection with the embeddings
search_collection(embeddings, top_k=7)

"""Traceback (most recent call last):
  File "/Users/pranavrn/Desktop/testcase/VirtualTA/tester.py", line 74, in <module>
    embeddings = get_embeddings(query)
                 ^^^^^^^^^^^^^^^^^^^^^
  File "/Users/pranavrn/Desktop/testcase/VirtualTA/tester.py", line 64, in get_embeddings
    response = requests.post(url, json=data, headers=headers)  
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/pranavrn/opt/miniconda3/lib/python3.12/site-packages/requests/api.py", line 115, in post
    return request("post", url, data=data, json=json, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/pranavrn/opt/miniconda3/lib/python3.12/site-packages/requests/api.py", line 59, in request
    return session.request(method=method, url=url, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/pranavrn/opt/miniconda3/lib/python3.12/site-packages/requests/sessions.py", line 575, in request
    prep = self.prepare_request(req)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/pranavrn/opt/miniconda3/lib/python3.12/site-packages/requests/sessions.py", line 484, in prepare_request
    p.prepare(
  File "/Users/pranavrn/opt/miniconda3/lib/python3.12/site-packages/requests/models.py", line 368, in prepare
    self.prepare_headers(headers)
  File "/Users/pranavrn/opt/miniconda3/lib/python3.12/site-packages/requests/models.py", line 488, in prepare_headers
    for header in headers.items():
                  ^^^^^^^^^^^^^
AttributeError: 'set' object has no attribute 'items'"""
# The error indicates that headers is being treated as a set instead of a dictionary.
#Done using headers=dict()


