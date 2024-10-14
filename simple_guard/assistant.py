import time
from typing import Optional

from openai import OpenAI

from guards import Guard


class Assistant:
    def __init__(
        self,
        prompt: str,
        instruction: str,
        client: OpenAI,
        img_url: Optional[str] = None,
        guard: Optional[Guard] = None,
        model: Optional[str] = "gpt-4o-mini",
    ):
        self.started = time.time()
        self.prompt = prompt
        self.instruction = instruction
        self.client = client
        self.img_url = img_url
        self.guard = guard
        self.model = model

        self.total_tokens = 0
        self.response = None

        user_input = [{"type": "text", "text": prompt}]
        if img_url:
            user_input.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"{img_url}"},
                }
            )

        self.messages = [
            {
                "role": "system",
                "content": [{"type": "text", "text": instruction}],
            },
            {
                "role": "user",
                "content": user_input,
            },
        ]

    def execute(self, temperature: float = 0.7):
        if self.guard:
            response = self.guard.apply(
                client=self.client,
                model=self.model,
                messages=self.messages,
                temperature=temperature,
            )
        else:
            response = self.client.chat.completions.create(
                model=self.model, messages=self.messages, temperature=temperature
            )

        self.response = response
        self.total_tokens += response.usage.total_tokens
        self.total_duration = time.time() - self.started
        return self

    def __repr__(self):
        return repr(
            f"""Assistant(prompt="{self.prompt}",""",
            f"""img_url="{self.img_url}","""
            f"""response="{self.response.choices[0].message.content}",""",
            f"""guard={self.guard}",""",
            f"""total_tokens={self.total_tokens}",""",
            f"""total_duration={self.total_duration}")""",
        )
