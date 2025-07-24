# Zuno: The AI-Powered Multimodal Shopping Advisor

Zuno is an intelligent e-commerce agent designed to simplify the online shopping experience. It acts as a personal shopping advisor, leveraging a multi-agent system, advanced search tools, and user-defined priorities to deliver highly personalized product recommendations.

## ✨ Features

- 🤖 **Intelligent Agent Architecture**: Built on a robust Model-Context-Protocol (MCP) server architecture for clean separation of concerns.
- ⚖️ **Personalized Ranking**: Users can set the importance of Price vs. User Rating, and Zuno's Comparison Agent ranks products according to these weights.
- 📸 **Multimodal Input**: Accepts both text queries and image uploads.
- ✍️ **Optical Character Recognition (OCR)**: If a user uploads an image without a text query, Zuno uses easyocr to extract text from the image and initiate the search.
- 🌐 **Advanced Media Search**: Enriches product results with visually similar items (simulated via Google Images) and video reviews (via Google Video Search).
- 🧠 **AI-Powered Synthesis**: Uses the Gemini LLM to analyze all gathered data and provide a concise, human-readable summary and final recommendation.

## 🏗️ Architecture Overview

Zuno is built using a decoupled architecture inspired by the Model-Context-Protocol (MCP) design pattern:

- **Frontend (UI)**: A user-friendly interface built with Streamlit. It captures all user inputs (text, images, priority weights) and performs client-side OCR.
- **API Gateway (Server)**: A backend server built with FastAPI. It exposes a single, well-defined endpoint for the frontend to communicate with, acting as the entry point to the agent system.
- **Backend (Agents & Tools)**: The core logic powered by LangChain and Google Gemini. An `OrchestratorAgent` receives requests from the server, calls specialized tools for data retrieval (SerpAPI), and uses a `ComparisonAgent` to rank results before synthesizing a final answer.

## 🚀 Getting Started

Follow these instructions to set up and run Zuno on your local machine.

### 1. Prerequisites

- [Python 3.9+](https://www.python.org/)
- An active virtual environment (recommended)

### 2. Clone the Repository

```bash
git clone https://github.com/your-username/zuno-multimodal-agent.git
cd zuno-multimodal-agent
```

### 3. Set Up Environment

#### Create and activate a virtual environment:

```bash
python -m venv .venv
# Activate on Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# Activate on macOS/Linux
source .venv/bin/activate
```

#### Install dependencies:

```bash
pip install -r requirements.txt
```

#### Configure API Keys:

Create a `.env` file in the root directory and add your API keys:

```env
GOOGLE_API_KEY="YOUR_GOOGLE_AI_API_KEY_HERE"
SERPAPI_API_KEY="YOUR_SERPAPI_API_KEY_HERE"
```

### 4. Running the Application

Zuno requires two processes to run simultaneously in separate terminals.

- **Backend Server** (Terminal 1):

  ```bash
  uvicorn zuno.server:app --reload
  ```

  The server will run at `http://127.0.0.1:8000`.

- **Frontend Application** (Terminal 2):

  ```bash
  streamlit run app.py
  ```

  Your browser should automatically open to the Streamlit application.

## 📖 API Documentation

The Zuno system provides a single API endpoint:

### **Endpoint**: `/invoke_agent`

- **Method**: `POST`
- **Content-Type**: `application/json`

#### Authentication

The endpoint requires valid `GOOGLE_API_KEY` and `SERPAPI_API_KEY` in the `.env` file. If these keys are missing or invalid, the tools will fail.

#### Request Body

```json
{
  "query": "Best wireless earbuds",
  "image_data": "data:image/jpeg;base64,...",
  "weights": {
    "price": 0.5,
    "rating": 0.5
  }
}
```

- **query** (string, required): The user's text query or OCR-derived text.
- **image_data** (string, optional): Base64-encoded image data.
- **weights** (object, required): User's ranking priorities.
  - **price** (float): Importance of price (0.0 - 1.0).
  - **rating** (float): Importance of user rating (0.0 - 1.0).

#### Response Body

```json
{
  "summary": "AI-generated summary and recommendation.",
  "ranked_products": [...],
  "image_results": [...],
  "video_results": [...],
  "lens_results": [...]
}
```

## 📂 Code Documentation

### `zuno/server.py`

- **Function**: `invoke_agent(request: AgentRequest)`
  - Receives the request, invokes the orchestrator's `run` method, and returns `AgentResponse`.

### `zuno/agents.py`

- **Class**: `OrchestratorAgent`
  - **Method**: `run(request: AgentRequest)`
    - Delegates data retrieval, ranking, and synthesis.
  - **Method**: `rank_products(products: list, weights: dict)`
    - Calculates weighted scores and returns sorted products.

### `zuno/models.py`

Defines Pydantic models:

- `AgentRequest`
- `ComparisonWeights`
- `AgentResponse`
- `Product`
- `MediaResult`

### `zuno/tools.py`

Provides specialized tools:

- `search_products(query: str)`
- `search_google_images(query: str)`
- `search_google_videos(query: str)`

For detailed module usage, refer to inline docstrings. Contributions and issues are welcome!

