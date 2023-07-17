import requests
import random
import logging

def get_random_image_from_unsplash(query):
    api_key = "5AtbQ-CihsI_Nn17xSZvKl-G-hQiwY-f5nUUjWJYUBI"
    headers = {
        "Authorization": f"Client-ID {api_key}",
    }

    params = {
        "query": query,
        "orientation": "landscape",
        "count": 1
    }

    response = requests.get("https://api.unsplash.com/photos/random", headers=headers, params=params)
    logging.debug(f"Unsplash API response status code: {response.status_code}")
    logging.debug(f"Unsplash API response content: {response.content}")

    if response.status_code == 200:
        result = response.json()
        if len(result) > 0 and "urls" in result[0]:
            return result[0]["urls"]["regular"]

    return None
