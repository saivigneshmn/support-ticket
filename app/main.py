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
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API keys and configurations
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
ZAPIER_WEBHOOK_URL = os.getenv("ZAPIER_WEBHOOK_URL")
INDEX_NAME = os.getenv("INDEX_NAME")
INDEX_HOST = os.getenv("INDEX_HOST")

# Initialize Together AI and Pinecone clients
together_client = Together(api_key=TOGETHER_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(name=INDEX_NAME, host=INDEX_HOST)

# FastAPI app
app = FastAPI()

@app.post("/submit-ticket")
async def submit_ticket(ticket: dict):
    return {"message": "Ticket submitted successfully!", "data": ticket}

# Pydantic model for request body
class SupportTicket(BaseModel):
    subject: str
    body: str
    priority: str
    product_names: list
    email: str

# Function to generate embeddings
def generate_embedding(text):
    try:
        response = together_client.embeddings.create(
            model="WhereIsAI/UAE-Large-V1",
            input=text,
        )
        return response.data[0].embedding
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding error: {str(e)}")

# Function to upsert support tickets into Pinecone
def upsert_support_ticket(ticket: SupportTicket):
    try:
        ticket_text = f"Subject: {ticket.subject}\nPriority: {ticket.priority}\nProducts: {', '.join(ticket.product_names)}\nIssue: {ticket.body}"
        embedding = generate_embedding(ticket_text)
        
        index.upsert(vectors=[{
            "id": str(hash(ticket_text)),
            "values": embedding,
            "metadata": ticket.model_dump(),
        }])

        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pinecone upsert error: {str(e)}")

# Function to query similar tickets
def get_similar_tickets(issue_text, top_k=3):
    try:
        embedding = generate_embedding(issue_text)
        result = index.query(vector=embedding, top_k=top_k, include_metadata=True)
        return result["matches"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pinecone query error: {str(e)}")

# Function to generate response
def generate_response(issue_text, similar_tickets):
    try:
        context = "\n\n".join([
            f"Similar Issue {i+1}:\nSubject: {ticket['metadata'].get('subject', 'N/A')}\nPriority: {ticket['metadata'].get('priority', 'N/A')}\nProducts: {', '.join(ticket['metadata'].get('product_names', []))}\nIssue: {ticket['metadata'].get('body', 'N/A')}"
            for i, ticket in enumerate(similar_tickets)
        ])
        
        messages = [
            {"role": "system", "content": "You are a technical support specialist. Use the similar support tickets provided to generate a helpful response."},
            {"role": "user", "content": f"New support ticket: {issue_text}\n\nSimilar tickets:\n{context}"}
        ]
        
        response = together_client.chat.completions.create(
            model="meta-llama/Meta-Llama-3-8B-Instruct-Turbo",
            messages=messages,
            max_tokens=300,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Response generation error: {str(e)}")

# Function to send email via Zapier
def send_email_via_zapier(email, subject, body):
    try:
        payload = {"email": email, "subject": subject, "body": body}
        response = requests.post(ZAPIER_WEBHOOK_URL, json=payload)
        response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Zapier email error: {str(e)}")

# FastAPI endpoint to submit tickets
@app.post("/submit-ticket")
async def submit_ticket(ticket: SupportTicket):
    try:
        # Upsert the ticket into Pinecone
        upsert_success = upsert_support_ticket(ticket)
        if not upsert_success:
            raise HTTPException(status_code=500, detail="Failed to upsert ticket into Pinecone")

        # Query similar tickets
        similar_tickets = get_similar_tickets(ticket.body)

        # Generate AI response
        response = generate_response(ticket.body, similar_tickets)

        # Send response via Zapier
        send_email_via_zapier(ticket.email, "Support Ticket Response", response)

        return {"message": "Ticket processed successfully", "response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run FastAPI server with Ngrok
if __name__ == "__main__":
    ngrok_tunnel = ngrok.connect(8000)
    print(f"Ngrok Tunnel URL: {ngrok_tunnel.public_url}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
