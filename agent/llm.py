import openai

# OpenAI API
openai.api_key = "your-openai-api-key-here"
import openai

# Use OpenAI API with the correct method
openai.api_key = "your-openai-api-key-here"

def generate_recommendation_reasoning(itinerary, preference):
    """
    Use OpenAI GPT to generate a natural language explanation of why this itinerary is recommended.
    """
    day_descriptions = []
    for day in itinerary.days:
        spots_names = [spot.name for spot in day.spots]
        day_descriptions.append(f"Day {day.day}: {', '.join(spots_names)}")

    itinerary_description = "\n".join(day_descriptions)

    # New API call with the correct model
    prompt = f"""
    Given the following itinerary, please provide a reason for recommending this mode of travel:
    
    Itinerary:
    {itinerary_description}
    
    The user’s travel preference is: {preference}
    
    Provide a detailed explanation of why this mode is recommended:
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # You can also use "gpt-4" if you have access
        messages=[
            {"role": "system", "content": "You are a helpful travel assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.7
    )

    return response['choices'][0]['message']['content'].strip()
