import os
from pydantic_ai import Agent

prefixes = ['gemini:', 'google:', 'google-genai:', 'vertex:', 'google-vertex:', 'google-gla:', '']
models = ['gemini-1.5-flash', 'gemini-1.5-pro']

for p in prefixes:
    for m in models:
        model_str = f"{p}{m}"
        try:
            agent = Agent(model_str, system_prompt="Hello")
            print(f"SUCCESS: {model_str}")
        except Exception as e:
            print(f"ERROR for {model_str}: {e}")

