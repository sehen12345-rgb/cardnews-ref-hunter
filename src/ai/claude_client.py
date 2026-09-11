import json
from pathlib import Path
import anthropic

CONFIG_PATH = Path(__file__).parent.parent.parent / "config.json"


def get_client() -> anthropic.Anthropic:
    config = {}
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
    api_key = config.get("claude_api_key", "")
    if not api_key:
        raise ValueError("config.json에 claude_api_key를 입력해주세요.")
    return anthropic.Anthropic(api_key=api_key)


def ask(system_prompt: str, user_prompt: str, model: str = "claude-sonnet-4-6") -> str:
    client = get_client()
    message = client.messages.create(
        model=model,
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return message.content[0].text.strip()
