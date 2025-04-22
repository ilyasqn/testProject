import httpx


async def get_llm_response(message: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": "Bearer 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",
        "HTTP-Referer": "https://your-site.com",
        "X-Title": "Your Site Name"
    }
    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": message}
        ]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]
