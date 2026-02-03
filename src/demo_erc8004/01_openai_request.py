"""01 - OpenAI Chat Completion Request

Makes a single chat completion call using the nilAI / OpenAI-compatible API.
Configuration is read from .env file.
"""

import os
import sys

from dotenv import load_dotenv
from openai import OpenAI


def main():
    load_dotenv()

    base_url = os.environ.get("NILAI_BASE_URL", "")
    api_key = os.environ.get("NILAI_API_KEY", "")
    model = os.environ.get("NILAI_MODEL", "")

    if not base_url or not api_key or not model:
        print(
            "WARNING: NILAI_BASE_URL, NILAI_API_KEY, and NILAI_MODEL must be set in .env"
        )
        print("Copy .env.sample to .env and fill in your credentials.")
        sys.exit(1)

    client = OpenAI(base_url=base_url, api_key=api_key)

    print(f"Sending chat completion request to {base_url} using model {model}...")

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Hello, how are you?"}],
    )

    print(f"Response: {response.choices[0].message.content}")


if __name__ == "__main__":
    main()
