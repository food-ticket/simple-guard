import time
from typing import Optional

import openai

from guards import Guard

class Assistant:
    LLM_MODEL = "gpt-4o-mini"

    def __init__(
            self,
            prompt: str,
            instruction: str,
            img_url: Optional[str]=None,
            guard: Optional[Guard]=None
        ):
        self.started = time.time()
        self.prompt = prompt
        self.img_url = img_url
        self.instruction = instruction
        self.guard = guard
        self.total_tokens = 0
        self.response = None

        user_input = [{"type": "text", "text": prompt}]
        if img_url:
            user_input.append({
                "type": "image_url",
                "image_url": {"url": f"{img_url}"},
            })

        self.messages = [
            {
                "role": "system",
                "content": [
                    {"type": "text", "text": instruction}
                ],
            },
            {
                "role": "user",
                "content": user_input,
            }
        ]

    def execute(self, temperature: float=0.7):
        if self.guard:
            response = self.guard.apply(
                model=self.LLM_MODEL,
                messages=self.messages,
                temperature=temperature,
            )
        else:
            response = openai.chat.completions.create(
                model=self.LLM_MODEL,
                messages=self.messages,
                temperature=temperature
            )
        
        self.response = response
        self.total_tokens += response.usage.total_tokens
        self.total_duration = time.time() - self.started
        return self
    
    def __repr__(self):
        return f'Assistant(prompt="{self.prompt}", img_url="{self.img_url}", response="{self.response.choices[0].message.content}", guard={self.guard}, total_tokens={self.total_tokens}, total_duration={self.total_duration})'
