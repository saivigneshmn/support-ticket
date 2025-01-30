---

# **Automated Support Ticket Resolution System**

This project is designed to automate the resolution of customer support tickets using advanced NLP techniques, vector databases, and integrations with third-party tools like Pinecone and Zapier. The system retrieves similar past issues, generates personalized responses, and integrates with email systems for seamless communication.

---

## **Project Structure**

### **Root Directory**
- **`app/`**: Contains the main pipeline notebook for the support ticket system. ( NOT YET UPDATED! )
  - `Final_Pipeline_Support_ticket_draft_.ipynb`: The primary notebook for the support ticket pipeline, including Pinecone integration and Zapier email automation.
    
- **`data/`**: Contains datasets used for training and testing the system.
  - `helpdesk_customer_multi_lang_tickets.csv`: Multilingual customer support tickets.
  - `helpdesk_customer_tickets (1).csv`: Customer support tickets dataset.
  - `train-00000-of-00001-a5a7c6e4bb30b016.parquet`: Training data in Parquet format.
    
- **`rough/`**: Contains exploratory work and drafts for various components of the project.
  - `Analysis/`: Exploratory data analysis (EDA) notebooks and scripts.
  - `Automated Response/`: Drafts and experiments for automated response generation.
  - `Integrations/`: Integration scripts and experiments with third-party tools.
  - `Issue Prevention Dashboard/`: Work on dashboards for issue prevention.
  - `Project_Submission_P2 (Automated Response)/`: Submission-ready files for the automated response component.
  - `Project_Submission_P2 (Data Analysis)/`: Submission-ready files for the data analysis component.
  - `Real Time Escalation/`: Work on real-time escalation systems.
  - `Sentiment Analysis/`: Sentiment analysis experiments and notebooks.
- **`README.md`**: This file, providing an overview of the project.

---


![ticket](https://github.com/user-attachments/assets/d167bdc6-392e-4b37-8e44-f5d38deee258)


## **Features**

1. **Automated Ticket Resolution**:
   - Retrieves similar past issues using vector embeddings and Pinecone.
   - Generates personalized responses using OpenAI's GPT models.

2. **Email Integration**:
   - Integrates with Zapier and ngrok for automated email responses.

3. **Multilingual Support**:
   - Handles support tickets in multiple languages.

4. **Real-Time Escalation**:
   - Identifies and escalates critical issues in real-time.

5. **Sentiment Analysis**:
   - Analyzes customer sentiment to prioritize and personalize responses.

6. **Issue Prevention Dashboard**:
   - Provides insights into common issues and trends to prevent future problems.

---

## **Setup Instructions**

### **Prerequisites**
1. Python 3.10 or later.
2. Required Python libraries (install via `pip`):
   ```bash
   pip install pandas numpy openai pinecone-client sentence-transformers transformers ngrok zapier
   ```
3. API keys for:
   - OpenAI
   - Pinecone
   - Zapier
   - ngrok (if using local tunneling)

### **Steps to Run the Pipeline**
1. **Clone the Repository**:
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Set Up Environment Variables**:
   Create a `.env` file in the root directory and add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   ZAPIER_API_KEY=your_zapier_api_key
   NGROK_AUTH_TOKEN=your_ngrok_auth_token
   ```

3. **Run the Pipeline**:
   Open the `Final_Pipeline_Support_ticket_api_.ipynb` notebook in Jupyter or Google Colab and execute the cells.

4. **Test the System**:
   - Input a sample support ticket in the notebook.
   - Verify that the system retrieves similar issues and generates a response.
   - Check your email for the automated response (if Zapier integration is set up).

---
--------------------------------------------------------------------------------------------------------------
![Screenshot 2025-01-30 124224](https://github.com/user-attachments/assets/05e49ef1-638a-4055-9cde-dd17624ef60e)
--------------------------------------------------------------------------------------------------------------
![Screenshot 2025-01-30 124236](https://github.com/user-attachments/assets/a243aab1-16ee-431d-9586-ae26a7021f9a)
--------------------------------------------------------------------------------------------------------------
![Screenshot 2025-01-30 124937](https://github.com/user-attachments/assets/fc72c690-c40a-470a-aaa5-3115c6236135)

## **Usage**

### **Input**
- Provide the product name and issue description when prompted in the notebook.

### **Output**
- The system will:
  1. Retrieve the top 3 similar issues from the Pinecone vector database.
  2. Generate a personalized response using OpenAI's GPT model.
  3. Send the response via email (if Zapier integration is enabled).

---

## **Example**

### **Input**
```
Product Name: Dell XPS 13
Issue: My laptop is freezing intermittently.
```

### **Output**
```
Thanks for reaching out about your Dell XPS 13 issue. Our records show common problems include intermittent cursor freezing, software conflicts, and overheating. Based on the details you provided, it seems you may be experiencing intermittent cursor freezing. Please try updating your drivers and checking for background processes that may be causing the issue. Let me know if you need further assistance!
```

---

## **Contributing**

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request with a detailed description of your changes.

---

## **License**

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## **Contact**

For questions or feedback, please contact:
- **Your Name**: saivigneshmn@gmail.com
- **GitHub**: saivigneshmn

---
