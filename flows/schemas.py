KEY_IDEAS_SCHEMA = {
    "type": "object",
    "properties": {
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
        }
    },
    "required": ["key_ideas"],
}