from typing import List

from openai import OpenAI

from rules import Rule


class Guard:
    def __init__(
        self,
        name: str,
        rules: List[Rule],
    ):
        self.name = name
        self.rules = rules
        self.content = ""
        self.total_tokens = 0
        self.response = None

    @staticmethod
    def from_rules(name, rules: List[Rule]):
        return Guard(name=name, rules=rules)

    def apply(
        self,
        messages: list[dict],
        client: OpenAI,
        temperature: float = 0.7,
        model: str = "gpt-4o-mini",
    ) -> str:
        input_rules = [rule for rule in self.rules if rule.type == "input"]
        output_rules = [rule for rule in self.rules if rule.type == "output"]

        # Find user prompt in messages
        user_prompt = next(
            (
                content["text"]
                for message in messages
                if message["role"] == "user"
                for content in message["content"]
                if content["type"] == "text"
            ),
            None,
        )

        if not user_prompt:
            raise Exception("User input can not be found.")

        # Check input rules
        input_text = user_prompt
        for rule in input_rules:
            input_text = rule.check(input_text).content

        # Generate response
        response = client.chat.completions.create(
            model=model, messages=messages, temperature=temperature
        )
        self.response = response

        # Check output rules
        for rule in output_rules:
            if not rule.check(response.choices[0].message.content).allowed:
                raise ValueError(f"Output rule {rule} failed")

        # Attribute rule tokens to response
        response.usage.total_tokens = self.collect_total_tokens()
        response.usage.completion_tokens = None
        response.usage.prompt_tokens = None
        return response

    def collect_total_tokens(self):
        self.total_tokens += self.response.usage.total_tokens
        for rule in self.rules:
            self.total_tokens += rule.total_tokens
        return self.total_tokens

    def __repr__(self):
        return f"""Guard(name="{self.name}", rules="{self.rules}")"""
