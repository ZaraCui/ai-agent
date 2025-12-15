import openai
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

def generate_recommendation_reasoning(itinerary, preference):
    """
    使用 OpenAI GPT 生成一个自然语言解释，说明为什么推荐这个行程。
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "No API key provided, cannot generate recommendation reasoning."

    client = openai.OpenAI(api_key=api_key)

def generate_recommendation_reasoning(itinerary, preference):
    """
    使用 OpenAI GPT 生成一个自然语言解释，说明为什么推荐这个行程。
    """
    day_descriptions = []
    for day in itinerary.days:
        spots_names = [spot.name for spot in day.spots]
        day_descriptions.append(f"Day {day.day}: {', '.join(spots_names)}")

    itinerary_description = "\n".join(day_descriptions)

    # 更新后的 API 调用
    prompt = f"""
    Given the following itinerary, please provide a reason for recommending this mode of travel:
    
    Itinerary:
    {itinerary_description}
    
    The user’s travel preference is: {preference}
    
    Provide a detailed explanation of why this mode is recommended:
    """

    try:
        # 使用 ChatGPT 模型生成推荐解释
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7
        )
        
        # 提取并返回结果
        explanation = response.choices[0].message.content.strip()
        return explanation

    except openai.AuthenticationError as e:
        print(f"AuthenticationError: {e}")
    except openai.RateLimitError as e:
        print(f"RateLimitError: {e}")
    except openai.BadRequestError as e:
        print(f"BadRequestError: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return "Could not generate recommendation reasoning due to an error."