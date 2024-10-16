import time
from typing import Optional

from openai import OpenAI

from guards import Guard


class Assistant:
    def __init__(
        self,
        prompt: str,
        client: OpenAI,
        instruction: Optional[str] = None,
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

        self.set_messages()

        self.total_tokens = 0
        self.response = None

    def set_messages(self):
        user_input = [{"type": "text", "text": self.prompt}]

        if self.img_url:
            user_input.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"{self.img_url}"},
                }
            )

        self.messages = [
            {
                "role": "user",
                "content": user_input,
            },
        ]

        if self.instruction:
            self.messages.insert(
                0,
                {
                    "role": "system",
                    "content": [{"type": "text", "text": self.instruction}],
                },
            )
        return self

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
        return f"{self.__class__.__name__}({tuple(self.__dict__.values())})"
