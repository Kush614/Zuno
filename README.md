
# Zuno: AI-Powered Multimodal Shopping Advisor

![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
![Frameworks](https://img.shields.io/badge/Frameworks-FastAPI%20%7C%20Streamlit%20%7C%20LangChain-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)

Zuno is an intelligent e-commerce agent designed to simplify the online shopping experience. It acts as a personal shopping advisor, leveraging a multi-agent system, advanced search tools, and user-defined priorities to deliver highly personalized product recommendations.

![Zuno Video Demo](https://youtu.be/JIwXa71ZoAY?si=AVpXTX4kKjUJjexP) <!-- You can replace this with your own screenshot -->

## ✨ Features

-   **🤖 Intelligent Agent Architecture:** Built on a robust Model-Context-Protocol (MCP) server architecture for clean separation of concerns.
-   **⚖️ Personalized Ranking:** Users can set the importance of **Price** vs. **User Rating**, and Zuno's Comparison Agent ranks products according to these weights.
-   **📸 Multimodal Input:** Accepts both text queries and image uploads.
-   **✍️ Optical Character Recognition (OCR):** If a user uploads an image without a text query, Zuno uses `easyocr` to extract text from the image and initiate the search.
-   **🌐 Advanced Media Search:** Enriches product results with visually similar items (simulated via Google Images) and video reviews (via Google Video Search).
-   **🧠 AI-Powered Synthesis:** Uses the Gemini LLM to analyze all gathered data and provide a concise, human-readable summary and final recommendation.

## 🏗️ Architecture Overview

Zuno is built using a decoupled architecture inspired by the Model-Context-Protocol (MCP) design pattern:

-   **Frontend (UI):** A user-friendly interface built with **Streamlit**. It is responsible for capturing all user inputs (text, images, priority weights) and performing client-side OCR.
-   **API Gateway (Server):** A robust backend server built with **FastAPI**. It exposes a single, well-defined endpoint for the frontend to communicate with, acting as the entry point to the agent system.
-   **Backend (Agents & Tools):** The core logic powered by **LangChain** and **Google Gemini**. An `OrchestratorAgent` receives requests from the server, calls specialized tools for data retrieval (`SerpAPI`), and uses a `ComparisonAgent` to rank results before synthesizing a final answer.

## 🚀 Getting Started

Follow these instructions to set up and run the Zuno agent on your local machine.

### 1. Prerequisites

-   Python 3.9+
-   An active virtual environment (recommended)

### 2. Clone the Repository

```bash
git clone https://github.com/Kush-Ise/zuno-multimodal-agent.git
cd zuno-multimodal-agent
```

### 3. Set Up Environment

1.  **Create and activate a virtual environment:**
    ```bash
    # Create the environment
    python -m venv .venv

    # Activate on Windows (PowerShell)
    .\.venv\Scripts\Activate.ps1
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure API Keys:**
    -   Create a file named `.env` in the root directory of the project.
    -   Add your API keys to this file. You can get them from [Google AI Studio](https://ai.google.dev/) and [SerpApi](https://serpapi.com/).
    ```env
    GOOGLE_API_KEY="YOUR_GOOGLE_AI_API_KEY_HERE"
    SERPAPI_API_KEY="YOUR_SERPAPI_API_KEY_HERE"
    ```

### 4. Running the Application

Zuno requires two processes to run simultaneously in two separate terminals.

-   **Terminal 1: Start the Backend Server**
    *Ensure your virtual environment is active.*
    ```bash
    python -m zuno.server
    ```
    You should see Uvicorn running on `http://127.0.0.1:8000`.

-   **Terminal 2: Start the Frontend Application**
    *Ensure your virtual environment is active. Use the `-m streamlit` command for robustness.*
    ```bash
    python -m streamlit run app.py
    ```
    Your browser should automatically open to the Streamlit application.

---

## 📖 API Documentation

The Zuno system provides a single, powerful API endpoint to handle all shopping-related queries.

### Endpoint: `invoke_agent`

This endpoint is the main entry point to the Zuno agent system. It processes the user's query, orchestrates data retrieval and analysis, and returns a synthesized response.

-   **URL:** `/invoke_agent`
-   **Method:** `POST`
-   **Content-Type:** `application/json`

### Authentication

The API endpoint itself is not protected by a user-facing authentication token. However, the backend server requires valid `GOOGLE_API_KEY` and `SERPAPI_API_KEY` values to be present in the `.env` file to function correctly. If these keys are missing or invalid, the tools used by the agent will fail.

### Request Body

The request must be a JSON object with the following structure, corresponding to the `AgentRequest` Pydantic model.

| Parameter    | Type                                  | Description                                                                                              |
| :----------- | :------------------------------------ | :------------------------------------------------------------------------------------------------------- |
| `query`      | `string`                              | **Required.** The user's text query (e.g., "best wireless earbuds") or text derived from OCR.              |
| `image_data` | `string`                              | **Optional.** A Base64-encoded string representation of the uploaded product image.                      |
| `weights`    | `object` (`ComparisonWeights` model) | **Required.** An object containing the user's priorities for ranking products.                           |
| ↳ `price`    | `float`                               | A value between 0.0 and 1.0 representing the importance of price.                                        |
| ↳ `rating`   | `float`                               | A value between 0.0 and 1.0 representing the importance of user rating.                                  |

### Response Body

A successful request returns a `200 OK` status with a JSON object corresponding to the `AgentResponse` model.

| Parameter           | Type                      | Description                                                                  |
| :------------------ | :------------------------ | :--------------------------------------------------------------------------- |
| `summary`           | `string`                  | The final, AI-generated summary and recommendation for the user.             |
| `ranked_products`   | `array` of `Product` objects | A list of products found, sorted according to the user's weighted priorities.  |
| `image_results`     | `array` of `MediaResult` objects | A list of visually similar items found via image search.                     |
| `video_results`     | `array` of `MediaResult` objects | A list of relevant video reviews.                                          |
| `lens_results`      | `array` of `MediaResult` objects | A list of items found via reverse image search (simulated).                |

---

### Example API Call

Here is an example of how to call the API using `curl`.

#### Request Example

```bash
curl -X POST http://127.0.0.1:8000/invoke_agent \
-H "Content-Type: application/json" \
-d '{
  "query": "High-quality mechanical keyboard",
  "image_data": null,
  "weights": {
    "price": 0.3,
    "rating": 0.7
  }
}'
```

#### Expected Output Example (200 OK)

```json
{
  "summary": "Based on your focus on user ratings, the Keychron Q1 Pro seems to be the best match. It has excellent reviews praising its build quality and typing experience. I've also found some video reviews to help your decision.",
  "ranked_products": [
    {
      "title": "Keychron Q1 Pro Custom Mechanical Keyboard",
      "price": 199.99,
      "rating": 4.8,
      "reviews": 1250,
      "source": "Keychron Official",
      "link": "https://www.keychron.com/products/keychron-q1-pro-qmk-via-wireless-custom-mechanical-keyboard",
      "thumbnail": "...",
      "score": 0.85
    }
  ],
  "image_results": [],
  "video_results": [
    {
      "title": "Keychron Q1 Pro Review: The Best Yet?",
      "link": "https://www.youtube.com/watch?v=...",
      "thumbnail": "..."
    }
  ],
  "lens_results": []
}
```

---

## 📂 Code Documentation

This section provides a detailed breakdown of each module in the `zuno/` directory.

### `zuno/server.py`

This module contains the FastAPI application that serves as the API Gateway (MCP Server). Its primary role is to receive HTTP requests from the frontend, pass them to the `OrchestratorAgent`, and return the agent's response.

-   **`invoke_agent(request: AgentRequest)`**
    -   **Description:** The main API endpoint function. It receives the validated request, invokes the orchestrator's `run` method, and returns the final `AgentResponse`.
    -   **Parameters:**
        -   `request` (`AgentRequest`): A Pydantic model containing the query, optional image data, and user weights.
    -   **Returns:**
        -   `response` (`AgentResponse`): A Pydantic model containing the summarized results.

### `zuno/agents.py`

This is the core logic module. It contains the orchestrator that manages the workflow and the comparison agent logic for ranking products.

-   **`class OrchestratorAgent`**
    -   **Description:** Manages the entire process from receiving a request to generating a final summary. It does not perform tasks itself but delegates them to specialized tools.
    -   **`run(request: AgentRequest)`**
        -   **Description:** The main execution method. It calls the search tools, triggers the ranking function, and uses the Gemini LLM to synthesize the final summary.
        -   **Parameters:**
            -   `request` (`AgentRequest`): The incoming request object.
        -   **Returns:**
            -   `response` (`AgentResponse`): The final, populated response object.

-   **`rank_products(products: list, weights: dict)`**
    -   **Description:** Acts as the "Comparison Agent." It takes a raw list of products and the user's priorities, normalizes the data, calculates a weighted score for each product, and returns a sorted list.
    -   **Parameters:**
        -   `products` (`list`): A list of product dictionaries from the search tool.
        -   `weights` (`dict`): A dictionary containing `price` and `rating` weights.
    -   **Returns:**
        -   `ranked_list` (`list` of `Product`): A list of Pydantic `Product` objects, sorted by the calculated `score`.

### `zuno/models.py`

This module defines the strict data contracts (the "Protocol" in MCP) for communication between the frontend and backend, using Pydantic models. This ensures type safety and clear, validated data structures throughout the system.

-   **`AgentRequest`**: Defines the structure of the incoming request from the client.
-   **`ComparisonWeights`**: A sub-model defining the user's ranking priorities.
-   **`AgentResponse`**: Defines the structure of the final response sent back to the client.
-   **`Product`**: Defines the structure of a single, cleaned product item.
-   **`MediaResult`**: Defines the structure for a video or image search result.

### `zuno/tools.py`

This module contains functions that act as specialized tools for the agent. Each function interacts with an external API (`SerpAPI`) to retrieve real-time data from different Google search verticals.

-   **`search_products(query: str)`**: Searches Google Shopping for products matching the query.
-   **`search_google_images(query: str)`**: Searches Google Images for relevant pictures.
-   **`search_google_videos(query: str)`**: Searches Google Videos for product reviews.

## 🛠️ Technology Stack

-   **Backend:** FastAPI, LangChain, Google Gemini, Uvicorn
-   **Frontend:** Streamlit
-   **Data Validation:** Pydantic
-   **Data Manipulation:** Pandas
-   **External APIs:** SerpAPI (for Google Shopping, Images, Videos)
-   **Image Processing:** EasyOCR, Pillow

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.


