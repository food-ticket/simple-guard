from openai import OpenAI
from simple_guard import Assistant


def test_assistant_messages():
    prompt = "This is a test prompt"
    assistant = Assistant(prompt=prompt, client=OpenAI(api_key="fake_key"))

    assert assistant.messages == [
        {
            "role": "user",
            "content": [{"type": "text", "text": prompt}],
        }
    ]


def test_assistant_messages_instruction():
    prompt = "This is a test prompt"
    instruction = "This is a test instruction"
    assistant = Assistant(
        prompt=prompt, instruction=instruction, client=OpenAI(api_key="fake_key")
    )

    assert assistant.messages == [
        {
            "role": "system",
            "content": [{"type": "text", "text": instruction}],
        },
        {
            "role": "user",
            "content": [{"type": "text", "text": prompt}],
        },
    ]


def test_assistant_messages_image():
    prompt = "This is a test prompt"
    img_url = "https://example.com/fake.png"
    assistant = Assistant(
        prompt=prompt, img_url=img_url, client=OpenAI(api_key="fake_key")
    )

    assert assistant.messages == [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": img_url},
                },
            ],
        }
    ]


def test_assistant_messages_instruction_image():
    prompt = "This is a test prompt"
    instruction = "This is a test instruction"
    img_url = "https://example.com/fake.png"
    assistant = Assistant(
        prompt=prompt,
        instruction=instruction,
        img_url=img_url,
        client=OpenAI(api_key="fake_key"),
    )

    assert assistant.messages == [
        {
            "role": "system",
            "content": [
                {"type": "text", "text": instruction},
            ],
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": img_url},
                },
            ],
        },
    ]
