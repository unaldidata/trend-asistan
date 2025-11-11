import requests

serpapi_key = "c95ac986901e516c9b5dbdc7be961344c2b186c83b5192dc22e0a67842a5001e"

params = {
    "engine": "ebay",
    "_nkw": "Winco ESW-70 Electric Soup Warmer",
    "api_key": serpapi_key
}

r = requests.get("https://serpapi.com/search.json", params=params)
print("Status:", r.status_code)
print(r.text[:700])
