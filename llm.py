
import os
import time

import streamlit as st
from dotenv import load_dotenv
from groq import Groq


# Load environment variables from the local .env file
load_dotenv()


# Get the Groq API key from Streamlit Cloud Secrets
# or fall back to the local .env file
def get_api_key():
    try:
        key = st.secrets.get("GROQ_API_KEY")
    except Exception:
        key = None

    return key or os.getenv("GROQ_API_KEY")


GROQ_API_KEY = get_api_key()

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is missing. Add it to your .env file "
        "or Streamlit Cloud Secrets."
    )


# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)


# Retrieve available Groq models
def get_available_models():
    try:
        models = client.models.list()

        model_ids = [
            model.id
            for model in models.data
            if getattr(model, "active", True)
        ]

        return sorted(model_ids)

    except Exception as error:
        raise RuntimeError(
            f"Unable to retrieve Groq models: {error}"
        ) from error


# Generate an LLM response
def generate_response(
    messages,
    model,
    temperature=0.7,
    max_tokens=1024
):
    start_time = time.perf_counter()

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_completion_tokens=max_tokens
        )

        end_time = time.perf_counter()

        answer = completion.choices[0].message.content
        usage = completion.usage

        prompt_tokens = usage.prompt_tokens if usage else 0
        completion_tokens = (
            usage.completion_tokens if usage else 0
        )
        total_tokens = usage.total_tokens if usage else 0

        response_time = end_time - start_time

        return {
            "response": answer or "",
            "response_time": round(response_time, 3),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "model": model
        }

    except Exception as error:
        raise RuntimeError(
            f"Groq API request failed: {error}"
        ) from error
