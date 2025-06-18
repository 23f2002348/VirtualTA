from test_embed import collection
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


def search_collection(query, top_k=7):
    #Code for directly querying with embeddings
    #Assume query_text has query embeddings
    # Get embeddings for the query
    # Perform the query on the collection
    links = []
    results = collection.query(query_texts=query, n_results=top_k)
    # Extract the documents from the results

    print(results.keys())
    print(results['metadatas'][0])
    documents = results['documents'][0] if results['documents'] else []
    for meta in results['metadatas'][0]:
        text=""
        url = meta.get('url', "")
        if 'url' in meta:
            text=documents[results['metadatas'][0].index(meta)] if documents else ""
        if url!="":  
            links.append({
                      "url": url,
                      "text": text
                    })
    
    
    
    prompt = f"""You are an expert assistant on the Tools in Data Science course of IITM BS Data Science degree. Use the following context to answer the question below. For direct questions requiring a specific answer (like for when and where type questions -- try to answer the specific date or time or place), be more detailed and make sure to answer the question with a more strong reply including the required parametric answer.
    Think step by step and answer the question in a detailed manner. If the question is about a specific date or time, provide that information clearly.
    Be detailed and clear in your answers and make sure to be contextual and relative to the user's query. Give more importance to the text present in image queries if any and try to answer them.
    
    Context:
    {documents}

    Question:
    {query}

    Answer:"""
    response= vision_model.generate_content(prompt, generation_config={"temperature": 0.3})
    print(response.candidates[0].content.parts[0].text)
    print(links)
    return {
        "answer": response.candidates[0].content.parts[0].text,
        "links": links,
        "documents": documents
    }

def jina(query):
    k=search_collection(query, top_k=7)
    return k

#Configure the above command in script to get the embeddings of the input query
#Dont use helper
# Function to get embeddings for a query using the AIPipe API
# This function fetches embeddings for a given query using the AIPipe API.


#embeddings = get_embeddings(query)
# Search the collection with the embeddings





