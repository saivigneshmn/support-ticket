import os
import numpy as np
import pandas as pd
from together import Together
from pinecone import Pinecone
from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
import requests
from pyngrok import ngrok

# API keys and configurations
TOGETHER_API_KEY = "d4f51d8cb40a8fc1e9dc006d9aec78698c05c73f9f02433a61de6731e6c868ed"
PINECONE_API_KEY = "pcsk_2PXxbG_PWaKywf5AWfHUQdLb2q88DRUTEyZP3HjxCb79xEuvAPR1v7SWVZ1neQAJCefpZT"
ZAPIER_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/" 
# Pinecone index configuration
INDEX_NAME = "support-ticket"
INDEX_HOST = "https://support-ticket-ne8hs6h.svc.aped-4627-b74a.pinecone.io"

# Initialize Together AI and Pinecone clients
together_client = Together(api_key=TOGETHER_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(name=INDEX_NAME, host=INDEX_HOST)

# FastAPI app
app = FastAPI()

# Pydantic model for request body
class SupportTicket(BaseModel):
    subject: str
    body: str
    priority: str
    product_names: list
    email: str

# Function to generate embeddings using Together AI
def generate_embedding(text):
    response = together_client.embeddings.create(
        model="WhereIsAI/UAE-Large-V1",
        input=text,
    )
    return response.data[0].embedding

# Function to upsert support tickets into Pinecone
def upsert_support_tickets(df, num_samples=10):
    vectors = []
    for _, row in df.head(num_samples).iterrows():
        try:
            ticket_text = f"Subject: {row['subject']}\nPriority: {row['priority']}\nProducts: {', '.join(row['product_names'])}\nIssue: {row['body']}"
            embedding = generate_embedding(ticket_text)
            vectors.append({
                "id": str(row['id']),
                "values": embedding,
                "metadata": {
                    "subject": row['subject'],
                    "body": row['body'],
                    "priority": row['priority'],
                    "product_names": row['product_names'],
                    "email": row.get('email', '')
                }
            })
        except Exception as e:
            print(f"Error processing ticket {row['id']}: {str(e)}")
    
    if vectors:
        index.upsert(vectors=vectors)
        print(f"Successfully upserted {len(vectors)} tickets")

# Function to query similar tickets from Pinecone
def get_similar_tickets(issue_text, top_k=3):
    embedding = generate_embedding(issue_text)
    result = index.query(
        vector=embedding,
        top_k=top_k,
        include_metadata=True
    )
    return result["matches"]

# Function to generate a response using Together AI
def generate_response(issue_text, similar_tickets):
    context = "\n\n".join([
        f"Similar Issue {i+1}:\nSubject: {ticket['metadata']['subject']}\nPriority: {ticket['metadata']['priority']}\nProducts: {', '.join(ticket['metadata']['product_names'])}\nIssue: {ticket['metadata']['body']}"
        for i, ticket in enumerate(similar_tickets)
    ])
    
    messages = [
        {
            "role": "system",
            "content": "You are a technical support specialist. Use the similar support tickets provided to generate a helpful response."
        },
        {
            "role": "user",
            "content": f"New support ticket: {issue_text}\n\nSimilar support tickets for reference:\n{context}"
        }
    ]
    
    response = together_client.chat.completions.create(
        model="meta-llama/Meta-Llama-3-8B-Instruct-Turbo",
        messages=messages,
        max_tokens=300,
        temperature=0.7
    )
    
    return response.choices[0].message.content

# Function to send email via Zapier
def send_email_via_zapier(email, subject, body):
    payload = {
        "email": email,
        "subject": subject,
        "body": body
    }
    response = requests.post(ZAPIER_WEBHOOK_URL, json=payload)
    if response.status_code == 200:
        print("Email sent successfully via Zapier")
    else:
        print(f"Failed to send email: {response.text}")

# FastAPI endpoint to handle new support tickets
@app.post("/submit-ticket")
async def submit_ticket(ticket: SupportTicket):
    try:
        # Prepare ticket text for embedding
        ticket_text = f"Subject: {ticket.subject}\nPriority: {ticket.priority}\nProducts: {', '.join(ticket.product_names)}\nIssue: {ticket.body}"
        
        # Generate embedding and upsert into Pinecone
        embedding = generate_embedding(ticket_text)
        index.upsert(vectors=[{
            "id": str(hash(ticket_text)),  # Unique ID for the ticket
            "values": embedding,
            "metadata": {
                "subject": ticket.subject,
                "body": ticket.body,
                "priority": ticket.priority,
                "product_names": ticket.product_names,
                "email": ticket.email
            }
        }])
        
        # Query similar tickets
        similar_tickets = get_similar_tickets(ticket_text)
        
        # Generate response
        response = generate_response(ticket_text, similar_tickets)
        
        # Send email via Zapier
        send_email_via_zapier(ticket.email, "Support Ticket Response", response)
        
        return {"message": "Ticket processed successfully", "response": response}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run FastAPI server with Ngrok
if __name__ == "__main__":
    # Start Ngrok tunnel
    ngrok_tunnel = ngrok.connect(8000)
    print(f"Ngrok Tunnel URL: {ngrok_tunnel.public_url}")
    
    # Run FastAPI app
    uvicorn.run(app, host="0.0.0.0", port=8000)
