# simple-guard

Guardrails are a set of rules that a developer can use to ensure that their LLM models are safe and ethical. Guardrails can be used to check for biases, ensure transparency, and prevent harmful or dangerous behavior.

`simple-guard` implements guardrails through:
- Assistant: Main class that accepts and executes requests, much like the OpenAI client
- Guard: The guard holds the set of rules
- Rule: A limitation on the content it refers to

## Assistant
The Assistant is the query interface. The class holds the prompt and context, and executes and processes the rules in the correct order. The class also collects statistics like tokens and duration, that are convenient for logging purposes.

Setting up an assistant is as easy as:
```python
assistant = Assistant(
    prompt,
    context,
    img_url=img_url,
    guard=guard
)
response = assistant.execute()
```

## Guard
We put a guard in place to protect us agains the risks. The Guard holds the collection of rules. A guard can be created from rules like: 
```python
guard=Guard.from_rules(
    "Guardrails",
    [
        Pii(),
        Language(),
        Topical([
            "food",
        ])
    ]
)
```

## Rule
Rules are the individual limitations we put on content. This can be either input or output. Rules are separate classes based on the Rule base class that implements all common methods.

If a rule fails, there are three options, exception() (default), ignore (not recommended), or fix().