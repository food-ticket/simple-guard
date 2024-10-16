from typing import Any, List, cast, Optional

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

import openai


class Rule:
    ON_FAIL_OPTIONS = ["fix", "ignore", "exception"]
    MAX_TRIES = 1
    INPUT_RULE_LEADER = "Your role is to assess whether the question of a user is allowed or not. Be skeptical."
    INPUT_RULE_TRAILER = (
        "If the question is allowed, say 'allowed' otherwise say 'not_allowed'"
    )

    OUTPUT_RULE_LEADER = (
        "Your role is to assess whether the generated answer is allowed or not."
    )
    OUTPUT_RULE_TRAILER = (
        "If the generated answer is allowed, say 'allowed' otherwise say 'not_allowed'"
    )

    def __init__(
        self,
        on: str,
        priority: Optional[float] = 0.5,
        statement: Optional[str] = None,
        on_fail: Optional[str] = "exception",
    ):
        """Construct a rule object"""
        # Properties
        self.on = on
        self.on_fail = on_fail
        self.content = ""
        self.priority = priority

        # Rule
        if statement:
            self.set_statement(statement)

        # Statusses
        self.tries = 0
        self.evaluated = False
        self.allowed = None
        self.total_tokens = 0

    def set_statement(self, statement: str):
        self.statement = statement
        if self.on == "input":
            self.rule = (
                self.INPUT_RULE_LEADER + self.statement + self.INPUT_RULE_TRAILER
            )
        elif self.on == "output":
            self.rule = (
                self.OUTPUT_RULE_LEADER + self.statement + self.OUTPUT_RULE_TRAILER
            )
        else:
            raise NotImplementedError(f"Rule type {self.on} not supported")
        return self

    def set_fail_policy(self, on_fail: str):
        assert on_fail in Rule.ON_FAIL_OPTIONS, f"On failure {on_fail} not supported"
        self.on_fail = on_fail
        return self

    def set_priority(self, priority: float):
        assert 0 < priority <= 1, "Priority has to be between 0-1."
        self.priority = priority
        return self

    def check(self, content: str):
        self.content = content
        messages = [
            {
                "role": "system",
                "content": self.rule,
            },
            {"role": "user", "content": self.content},
        ]

        response = openai.chat.completions.create(
            model="gpt-4o-mini", messages=messages, temperature=0
        )

        self.evaluated = True
        self.total_tokens += response.usage.total_tokens

        if response.choices[0].message.content.lower() == "allowed":
            self.allowed = True
        else:
            self.allowed = False
            # Trigger on_failure action
            self.fail()
        return self

    def fail(self):
        if self.on_fail == "ignore":
            pass

        elif self.on_fail == "exception":
            self.exception()

        elif self.on_fail == "fix":
            # Prevent loop
            if self.tries >= self.MAX_TRIES:
                self.max_tries_exceeded()

            self.tries += 1
            # Call fix that resets content
            self.fix()
            # Check again
            self.check(self.content)

        else:
            raise NotImplementedError(f"On failure {self.on_failure} not supported")

    def exception(self):
        """Optionally overwrite in rule class"""
        raise Exception(f"Rule failed: {self}")

    def fix(self, *args):
        """Implement in rule class"""
        raise NotImplementedError(
            "Fixing rule failure not implemented, implement in rule class"
        )

    def max_tries_exceeded(self):
        raise Exception("Max tries exceeded.")

    def __repr__(self):
        return f"{self.__class__.__name__}({tuple(self.__dict__.values())})"


class Topical(Rule):
    def __init__(self, topics: List[str], *args):
        super().__init__(on="input", *args)
        self.set_statement(
            f"The allowed topics are {', '.join(topics)}. Are you sure the question is in one of these topics?"
        )

    def exception(self):
        raise Exception("Input is not on topic")


class Pii(Rule):
    PII = [
        "EMAIL_ADDRESS",
        "PHONE_NUMBER",
        "DOMAIN_NAME",
        "IP_ADDRESS",
        "DATE_TIME",
        "LOCATION",
        "PERSON",
        "URL",
    ]

    def __init__(self, *args):
        super().__init__(on="input", *args)
        self.set_fail_policy("fix")
        self.set_priority(1)

        # Setup
        self.pii_analyzer = AnalyzerEngine()
        self.pii_anonymizer = AnonymizerEngine()

    def check(self, content: str):
        """
        Custom local check method to prevent PII data being send
        to OpenAI
        """
        # TODO: python -m spacy download en_core_web_lg
        self.content = content

        # Call analyzer to get results
        results = self.pii_analyzer.analyze(
            text=self.content, entities=self.PII, language="en"
        )
        self.results = cast(List[Any], results)

        if len(self.results) == 0:
            self.allowed = True
        else:
            self.allowed = False
            # Trigger on_failure action
            self.fail()
        return self

    def fix(self):
        """Corrects and sets content"""
        self.content = self.pii_anonymizer.anonymize(
            text=self.content, analyzer_results=self.results
        ).text
        return self


class HarmfulContent(Rule):
    def __init__(self, *args):
        super().__init__(on="output", *args)
        self.set_statement(
            "The answer may not contain harmful or dangerous content. The answer must solely consist of language suitable for the workplace."
        )

    def exception(self):
        return Exception("Harmful content found in output.")
