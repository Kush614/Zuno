# zuno/agents.py - FINAL CORRECTED VERSION

import os
import pandas as pd
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Relative imports because this file is part of the 'zuno' package
from .tools import search_products, search_google_images, search_google_videos
from .models import AgentResponse, Product, MediaResult, AgentRequest

# Load the environment variables from the .env file in the root directory
load_dotenv()


def rank_products(products: list, weights: dict) -> list:
    """
    Ranks products based on user-defined weights.
    This version is robustly designed to handle missing or inconsistent API data.
    """
    if not products:
        return []

    df = pd.DataFrame(products)

    # --- Robust Data Cleaning and Normalization ---
    if 'extracted_price' not in df.columns:
        df['price'] = None
    else:
        df['price'] = pd.to_numeric(df['extracted_price'], errors='coerce')

    if 'rating' not in df.columns:
        df['rating'] = None
    else:
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce')

    df.dropna(subset=['price', 'rating'], inplace=True)

    if df.empty:
        return []

    if not df.empty and (df['price'].max() - df['price'].min()) != 0:
        df['price_norm'] = 1 - (df['price'] - df['price'].min()) / (df['price'].max() - df['price'].min())
    else:
        df['price_norm'] = 0.5
        
    if not df.empty and (df['rating'].max() - df['rating'].min()) != 0:
        df['rating_norm'] = (df['rating'] - df['rating'].min()) / (df['rating'].max() - df['rating'].min())
    else:
        df['rating_norm'] = 0.5
    
    df.fillna(0.5, inplace=True)

    total_weight = weights.get('price', 0) + weights.get('rating', 0)
    if total_weight == 0: total_weight = 1
    
    df['score'] = (
        (df['price_norm'] * weights.get('price', 0)) +
        (df['rating_norm'] * weights.get('rating', 0))
    ) / total_weight

    df = df.sort_values(by='score', ascending=False)
    
    # Pre-emptively clean data before sending to Pydantic
    ranked_list = [
        Product(
            title=row.get('title', 'No Title Available'),
            price=row.get('price'),
            rating=row.get('rating'),
            reviews=row.get('reviews'),
            source=row.get('source', 'Unknown Source'),
            link=row.get('link', ''),
            thumbnail=row.get('thumbnail', ''),
            score=row.get('score')
        ) for _, row in df.iterrows()
    ]
    return ranked_list


class OrchestratorAgent:
    """The main agent that manages the workflow."""
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.2,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

    def run(self, request: AgentRequest) -> AgentResponse:
        """Executes the agent workflow from search to synthesis."""
        response = AgentResponse(summary="Starting analysis...")

        raw_products = search_products(request.query)
        if raw_products:
            ranked_products = rank_products(raw_products, request.weights.dict())
            response.ranked_products = ranked_products

        if request.image_data:
            lens_raw = search_google_images(request.query)
            response.lens_results = [
                MediaResult(**item) for item in lens_raw if item.get('link') and item.get('thumbnail')
            ][:5]

        if "review" in request.query.lower() or "video" in request.query.lower():
            video_raw = search_google_videos(request.query)
            response.video_results = [
                MediaResult(**item) for item in video_raw if item.get('link') and item.get('thumbnail')
            ][:3]

        synthesis_prompt = self._create_synthesis_prompt(request, response)
        final_summary = self.llm.invoke(synthesis_prompt).content
        response.summary = final_summary

        return response
    
    def _create_synthesis_prompt(self, request: AgentRequest, response: AgentResponse) -> str:
        """Generates a detailed prompt for the LLM to summarize all gathered data."""
        prompt = f"You are Zuno, a helpful shopping assistant. Summarize the following findings for the user.\n"
        prompt += f"User's initial query: '{request.query}'\n"
        prompt += f"User's priorities: Price ({request.weights.price*100:.0f}%), Rating ({request.weights.rating*100:.0f}%).\n\n"
        
        if response.ranked_products:
            prompt += "Here are the top products I found, ranked according to your priorities:\n"
            for p in response.ranked_products[:3]:
                prompt += f"- **{p.title}** (Price: ${p.price:.2f}, Rating: {p.rating}, Score: {p.score:.2f})\n"
            if response.ranked_products:
                prompt += f"\nBased on your weights, the **{response.ranked_products[0].title}** seems to be the best match.\n\n"
        else:
            prompt += "I could not find any products with enough pricing and rating information to create a comparison.\n\n"
        
        if response.lens_results:
            prompt += "Based on the provided image, I found these visually similar items:\n"
            for item in response.lens_results[:2]:
                prompt += f"- {item.title}\n"
            prompt += "\n"

        if response.video_results:
            prompt += "I also found these video reviews that could be helpful for your decision:\n"
            for video in response.video_results:
                prompt += f"- {video.title}\n"
            prompt += "\n"

        prompt += "Please provide a final, concise, and helpful summary that synthesizes all of this information for the user. Speak directly to the user."
        return prompt