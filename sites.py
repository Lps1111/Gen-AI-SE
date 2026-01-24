# sites.py

SITES = [
    {
        "name": "The Hindu",
        "url": "https://www.thehindu.com/",
        "selectors": [
            "h3 a",
            "h2 a",
            "a.story-card75x1-text",
            "a.story-card-news-text",
        ],
        "max_items": 50
    },
    {
        "name": "BBC News",
        "url": "https://www.bbc.com/news",
        "selectors": [
            "a[data-testid='internal-link']",
            "h2 a",
            "h3 a",
        ],
        "max_items": 50
    },
    {
        "name": "Reuters World",
        "url": "https://www.reuters.com/world/",
        "selectors": [
            "a[data-testid='Heading']",
            "h3 a",
            "h2 a",
        ],
        "max_items": 50
    }
]
