# AzureAIValidation

Modern, Fully Asynchronous Document Processing with Azure — Upload → Queue → Function → AI → Result
<p align="center"> <img src="https://img.shields.io/badge/Azure-Document%20Intelligence-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white"/> <img src="https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/> <img src="https://img.shields.io/badge/Azure%20Functions-Serverless-0062AD?style=for-the-badge&logo=azurefunctions&logoColor=white"/> <img src="https://img.shields.io/badge/Async-Pipeline-6C63FF?style=for-the-badge"/> </p>
✨ Overview

This repository contains a fully functional, production-ready asynchronous pipeline for processing documents using:

Azure Document Intelligence (OCR + extraction)

Azure Functions (serverless queue consumers)

Azure Storage Queues

Streamlit for a modern async UI

Auto-tuning of thresholds

Full local + cloud versions of the pipeline

🎯 Upload a file → it enters the queue → serverless processor extracts insights → result appears automatically.

🚀 Features
💠 End-to-End Async Processing

Modern queue-based architecture

High-scale, serverless, low-latency

📄 Document Intelligence Integration

OCR

Layout extraction

Key-value prediction

Custom schema mapping

🕸️ Streamlit Modern UI

Drag-and-drop uploader

Live task polling

Real-time status indicators

Colorful and clean interface

🔁 Automatic Threshold Tuning

Runs metrics over past extractions

Suggests new thresholds automatically

Optional automated “smart tuning” mode

⚙ Azure Function Processor

Stateless

Idempotent

Production-ready

Includes retry/backoff handling

🧩 Architecture Diagram
```
flowchart LR
    A[Streamlit App<br>Upload File] --> B[Blob Storage]
    B --> C[Queue Message<br>("process_file")]
    C --> D[Azure Function<br>Document Processor]
    D --> E[Azure Document Intelligence]
    E --> F[AI Post-Processing<br>Thresholds, Validation]
    F --> G[Final Result Stored]
    G --> H[Streamlit Polls<br>and Shows Output]
```
Project Structure

```
📁 AzureAIValidation/
│
├── app_streamlit_async.py        
├── config.py                    
│
├── pipeline/
│   ├── aml_client.py          
│   ├── doc_analysis.py         
│   ├── embeddings_client.py     
│   ├── features.py
│   ├── report.py
│   └── scoring.py
│  
│
├── function_app/
│   ├── host.json
│   ├── local.settings.json             
│   └── QueuePorcessor/
│         ├── ___init___.py
│         └── functions.json
│
├── tune_thresholds.py           
├── requirements.txt
└── README.md
```

🧪 Quick Start
▶️ Run Streamlit App
```streamlit run app_streamlit_async.py ```

▶️ Run Azure Function Locally
```cd function_app
func start
```
▶️ Tune thresholds
```python tune_thresholds.py ```

🎛️ Configuration

Set your Azure keys in config.py:

```AZURE_DOCUMENT_KEY = "your-key"
AZURE_DOCUMENT_ENDPOINT = "https://xxxx.cognitiveservices.azure.com/"
AZURE_DOCUMENT_REGION = "eastus2"


For Azure Functions:

{
  "Values": {
    "AzureWebJobsStorage": "<connection-string>",
    "DOCUMENT_INTELLIGENCE_KEY": "your-key",
    "DOCUMENT_INTELLIGENCE_ENDPOINT": "https://xxx.cognitiveservices.azure.com/"
  }
}
```
🧠 AI Post-Processing

We apply:
- Confidence thresholding
- Schema normalization
- Automatic retry logic
- Weighted consensus scoring
- Optional Azure OpenAI validation
```
<details> <summary>📘 What is Document Intelligence?</summary> Document Intelligence is Azure’s engine for processing PDFs, invoices, receipts, identity documents, and more. It performs OCR, layout parsing, table detection, and key-value extraction. </details> <details> <summary>🌀 How the async queue improves performance</summary> By decoupling upload → compute, you avoid blocking users and allow scaling based on load. </details> <details> <summary>⚡ Auto-threshold tuning algorithm</summary>
``` 1. Load historical extracted results  
2. Compute precision, recall, f1  
3. Sweep confidence thresholds  
4. Pick optimal threshold  
5. Suggest update / write results  
</details>
```

🛠 Deployment Options
☁ Deploy Azure Function

Run:

``` func azure functionapp publish <your-app-name> ```

☁ Deploy Streamlit via Azure App Service

Or via container using the included Dockerfile.

☁ Deploy Complete Pipeline

You may use the included CI/CD YAML sample files.
