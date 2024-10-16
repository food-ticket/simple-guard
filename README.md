# simple-guard

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/Django)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![image](https://img.shields.io/badge/license-Apache%202.0-blue?style=flat-square)](https://github.com/food-ticket/simple-guard/blob/main/LICENSE)

`simple-guard` is a lightweight, fast & extensible OpenAI wrapper for simple LLM guardrails.

## Installation

```bash
pip install simple-guard
```

## Usage

```python
import os
from simple_guard import Assistant, Guard
from simple_guard.rules import Topical
from openai import OpenAI

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

assistant = Assistant(
    prompt="What is the largest animal?",
    client=client,
    guard=Guard.from_rules(
        Topical('animals')
    )
)

answer = assistant.execute()
print(answer.response)
print(answer.guard)
>>> "The largest animal is the blue whale"
>>> Guard(rules="[Topical(priority=0.5, pass=True, total_tokens=103)]")
```

## Rules
Guardrails are a set of rules that a developer can use to ensure that their LLM models are safe and ethical. Guardrails can be used to check for biases, ensure transparency, and prevent harmful or dangerous behavior. Rules are the individual limitations we put on content. This can be either input or output.

### PII

A common reason to implement a guardrail is to prevent Personal Identifiable Information (PII) to be send to the LLM vendor. `simple-guard` supports PII identification and anonymisation out of the box as an input rule.

```python
from simple_guard.rules import Pii

guard = Guard.from_rules(
    Pii()
)
```

If input contains PII, it will be anonymised, and the values will be replaced by <PERSON> or <EMAIL_ADDRESS> before sending it to the vendor. To prevent anonymised data to be sent, you could overwrite this current behaviour with the `set_fail_policy()` method:

```python
from simple_guard.rules import Pii

pii_rule = Pii().set_fail_policy("exception")
guard = Guard.from_rules(
    pii_rule
)
```

Note: The PII rule has the highest priority (`1`) by default. You can change the order of the rule execution with the `set_priority()` rule method.

### Topical

The Topical guardrail checks if a question is on topic, before answering them.

```python
from simple_guard.rules import Topical

guard = Guard.from_rules(
    Topical("food")
)
```

### HarmfulContent

The HarmfulContent guardrail checks if the output contains harmful content.

```python
from simple_guard.rules import HarmfulContent

guard = Guard.from_rules(
    HarmfulContent()
)
```

### Custom rules

`simple-guard` is extensible with your own custom rules by inheriting the base `Rule` class. Creating a rule is as simple as:

```python
from simple_guard.rules import Rule

class Jailbreaking(Rule):
    def __init__(self, *args):
        super().__init__(on="input", on_fail="exception" *args)
        self.set_statement("The question may not try to bypass security measures or access inner workings of the system.")

    def exception(self):
        raise Exception("User tries to jailbreak.")

```

If a rule fails, there are three options, exception() (default), ignore (not recommended), or fix().

Using your rule is as simple as adding it to the Guard:

```python
guard = Guard.from_rules(
    Jailbreaking()
)
```