
import os
import time

from dotenv import load_dotenv
from groq import Groq


# Load environment variables from .env
load_dotenv()

# Read API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is missing. Add it to your .env file."
    )

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)


def get_available_models():
    """
    Retrieve models available to this Groq account.
    """

    try:
        models = client.models.list()

        model_ids = [
            model.id for model in models.data
            if getattr(model, "active", True)
        ]

        return sorted(model_ids)

    except Exception as error:
        raise RuntimeError(
            f"Unable to retrieve Groq models: {error}"
        )


def generate_response(
    messages,
    model,
    temperature=0.7,
    max_tokens=1024
):
    """
    Generate an LLM response using Groq.

    Parameters:
        messages: Conversation history
        model: Selected Groq model
        temperature: Controls response randomness
        max_tokens: Maximum response token limit

    Returns:
        Dictionary containing response and performance metrics.
    """

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

        prompt_tokens = (
            usage.prompt_tokens if usage else 0
        )

        completion_tokens = (
            usage.completion_tokens if usage else 0
        )

        total_tokens = (
            usage.total_tokens if usage else 0
        )

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
