from openai import OpenAI
import os
import logging

# Set up client for OpenRouter API
try:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logging.warning("Environment variable OPENROUTER_API_KEY is not set.")
        
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key or "no_key_provided",  # Allow initialization even without key
    )
except Exception as e:
    logging.error(f"Error initializing OpenAI client: {str(e)}")
    client = None

def get_smart_label(text):
    """Generate a smart label for the headline using the OpenRouter API or fallback to local labeling."""
    if not client or not os.getenv("OPENROUTER_API_KEY"):
        return generate_local_label(text)
        
    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "http://localhost:5000",
                "X-Title": "IndianExpressTopicModeler",
            },
            model="mistralai/mistral-small-3.1-24b-instruct:free",  # Using free tier
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert news analyst that categorizes headlines into clear, concise topic labels."
                },
                {
                    "role": "user",
                    "content": f"Summarize the main topic of this news headline in 3-5 words:\n\n{text}"
                }
            ],
            max_tokens=30,
            temperature=0.2  # Lower temperature for more consistent responses
        )
        
        content = completion.choices[0].message.content
        # Clean up the response - remove quotes and period if present
        content = content.strip().strip('"\'').rstrip('.')
        return content if content else generate_local_label(text)
        
    except Exception as e:
        logging.error(f"AI Labeling Error: {str(e)}")
        return generate_local_label(text)
        
def generate_local_label(text):
    """Generate a label locally when API is unavailable."""
    # Simple keyword-based categorization
    text = text.lower()
    
    # Define categories with associated keywords
    categories = {
        "Politics": ["election", "minister", "government", "parliament", "congress", "bjp", "political", "vote", "party", "president", "prime minister"],
        "Economy": ["economy", "economic", "market", "finance", "bank", "stock", "trade", "business", "inflation", "tax", "budget"],
        "International": ["pakistan", "china", "us", "usa", "russia", "foreign", "global", "international", "world", "diplomatic", "border", "tensions"],
        "Health": ["covid", "virus", "disease", "health", "hospital", "medical", "doctor", "patient", "vaccine", "pandemic", "healthcare"],
        "Crime": ["murder", "crime", "police", "arrest", "court", "jail", "criminal", "investigation", "law", "victim", "attack", "terror"],
        "Technology": ["tech", "technology", "digital", "online", "internet", "cyber", "ai", "app", "software", "computer", "innovation"],
        "Sports": ["cricket", "sport", "player", "team", "match", "win", "tournament", "championship", "olympic", "game", "athlete"],
        "Entertainment": ["film", "movie", "actor", "actress", "bollywood", "celebrity", "music", "show", "star", "entertainment"],
        "Environment": ["climate", "environment", "pollution", "weather", "green", "sustainable", "flood", "disaster", "forest", "nature"],
        "Education": ["student", "education", "school", "university", "college", "exam", "academic", "teacher", "learning", "degree"]
    }
    
    # Count keyword matches for each category
    category_scores = {category: 0 for category in categories}
    
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in text:
                category_scores[category] += 1
                
    # Find category with highest score
    best_category = max(category_scores.items(), key=lambda x: x[1])
    
    # If no category found, extract main nouns
    if best_category[1] == 0:
        words = text.split()
        if len(words) >= 3:
            return " ".join(words[:3])
        return "General News"
    
    return best_category[0]