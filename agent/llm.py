import openai

# OpenAI API
openai.api_key = "your-openai-api-key-here"

def generate_recommendation_reasoning(itinerary: Itinerary, preference: str) -> str:
    """
    Use ChatGPT to give natural language reasoning for recommending a transport mode.
    """
    # turn itinerary into a clearer text description
    day_descriptions = []
    for day in itinerary.days:
        spots_names = [spot.name for spot in day.spots]
        day_descriptions.append(f"Day {day.day}: {', '.join(spots_names)}")

    itinerary_description = "\n".join(day_descriptions)

    # Ask Gpt for natural language reasoning
    prompt = f"""
    Given the travel itinerary below, generate a reasoning for recommending a particular mode of transport to the user.    
    The ininerary is as follows:
    {itinerary_description}
    The user's travel preferences are:{preference}
    
    Explain the reanson why you decide the plan(included transport mode, weather, .etc) is suitable for the user based on their preferences."""

    response = openai.Completion.create(
        engine="gpt-4",
        prompt=prompt,
        max_tokens=300,
        temperature=0.7,
    )

    return response.choices[0].text.strip()
