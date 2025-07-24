import os
from serpapi import GoogleSearch

def search_products(query: str) -> list:
    """Searches Google Shopping and returns a list of product dictionaries."""
    search = GoogleSearch({
        "engine": "google_shopping",
        "q": query,
        "api_key": os.getenv("SERPAPI_API_KEY")
    })
    results = search.get_dict().get("shopping_results", [])
    return results

def search_google_lens(image_url: str) -> list:
    """Performs a reverse image search using an image URL."""
    search = GoogleSearch({
        "engine": "google_lens",
        "url": image_url,
        "api_key": os.getenv("SERPAPI_API_KEY")
    })
    results = search.get_dict().get("visual_matches", [])
    return results

def search_google_images(query: str) -> list:
    """Searches Google Images."""
    search = GoogleSearch({
        "engine": "google_images",
        "q": query,
        "api_key": os.getenv("SERPAPI_API_KEY")
    })
    results = search.get_dict().get("images_results", [])
    return results

def search_google_videos(query: str) -> list:
    """Searches Google Videos, perfect for finding product reviews."""
    search = GoogleSearch({
        "engine": "google_video",
        "q": f"{query} review", # Add 'review' to narrow the search
        "api_key": os.getenv("SERPAPI_API_KEY")
    })
    results = search.get_dict().get("video_results", [])
    return results