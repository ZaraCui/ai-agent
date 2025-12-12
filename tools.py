def run_python(code: str) -> str:
    try:
        result = eval(code)
        return str(result)
    except Exception as e:
        return f"Error: {e}"
