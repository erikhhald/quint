KEY_IDEAS_SCHEMA = {
    "type": "object",
    "properties": {
        "topic": {
            "type": "string",
            "description": "Brief title for the topic discussed",
        },
        "key_ideas": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Brief title for the key idea",
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed explanation of the key idea",
                    },
                },
                "required": ["title", "description"],
            },
        },
    },
    "required": ["topic", "key_ideas"],
}


JUDGE_ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "key_ideas_answered": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": None,
                "description": "Title of a key idea that the student demonstrates understanding of",
            },
            "description": "Array of key idea titles that the student shows understanding of",
            "uniqueItems": True,
        }
    },
    "required": ["key_ideas_answered"],
}
