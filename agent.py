from openai import OpenAI
from tools import run_python

client = OpenAI()

def agent(task: str):
    # Step 1: Ask LLM how to完成这个任务
    prompt = f"""
You are an agent. Your job is to complete this task using Python code when possible.

Task: {task}

Respond with:
1. Thought: explain your plan
2. Action: the Python code to run (only code)
"""

    response = client.chat.completions.create(
        model="gpt-5.1",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message["content"]

    # Step 2: Extract the action
    if "Action:" in content:
        code = content.split("Action:")[1].strip()
        result = run_python(code)
        return f"{content}\n\nResult: {result}"
    else:
        return content
