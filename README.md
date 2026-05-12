# LLM YouTube landscape tracker  

    
>**[Live Demo: Click here to visit my Streamlit Web App](https://llmyoutube-2rt4553gd5ceydqtq8irqr.streamlit.app/)**


## 1. Problem Statement
In the rapidly evolving field of Artificial Intelligence, staying updated with high-quality video content (e.g., from Andrej Karpathy or AI Explained) is time-consuming.

* **The Challenges:** Manually tracking multiple channels is inefficient, and some videos lack subtitles or have restricted access, causing traditional scrapers to fail.  

* **The Solution:** An automated pipeline that fetches the latest videos, generates AI summaries using Large Language Model (LLMs), and provides a searchable web interface.  


## 2. Methodology
The system employs a decoupled architecture separating data ingestion, AI inference, and frontend presentation.

* **Data Ingestion:** Uses `yt-dlp` to fetch metadata and subtitles from designated YouTube channels.
* **AI Engine:** Integrated **deepseek-ai/DeepSeek-V3** (via SiliconFlow API) for high-performance, cost-effective English summarization.
* **Automation:** Managed by **GitHub Actions**, triggering a daily cron job to sync new data into a CSV-based "lightweight database".
* **Frontend:** A **Streamlit** web application that reads the CSV and provides real-time keyword search and filtering.


>![Action Workflow log](./image/Actons%20workflow%20log.png)
>
> Figure1: GitHub Actions Workflow Log
## 3. Key Technical Challenges & Solutions (Engineering Excellence)
### Challenge 1: Handling "Sign-in to confirm you're not a bot" errors.
* Issue: YouTube often block subtitle fetching in cloud environments.
* Solution: Implemented a **Fallback Summarization Logic**. If subtitles are unavailable, the system automatically shifts to "Title-based Insight Generation," ensuring the database remains populated and the service stays available.  

### Challenge 2: Variable Scope & Asynchronous Data Flow.
* Issue: Initial errors occurred when the AI prompt was called before data was fully cleaned.
* Solution: Refactored the code into a robust try-except structure, ensuring variable initialization (e.g., `full_text=" "`) occurs before usage to prevent runtime crashes.


## 4. Evaluation Dataset & Methods
* **Dataset:** A dynamic dataset consisting of the latest 5 videos from top-tier AI YouTube channels (e.g., Andrej Karpathy, AI Explained).
   