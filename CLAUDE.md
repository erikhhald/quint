# Quint - Spaced Repetition Learning System

A PyQt5-based spaced repetition application with AI-powered content generation.

## Project Structure

```
quint/
├── main.py                 # Application entry point
├── ui/
│   ├── __init__.py
│   ├── pages/
│   │   ├── chat.py         # Chat interface page
│   │   ├── decks.py        # Deck management page
│   │   ├── main_window.py  # Main application window
│   │   ├── settings.py     # Settings configuration page
│   │   └── stats.py        # Statistics and analytics page
│   ├── template.py         # Base template for UI pages
│   └── theme.py            # UI theme and styling
├── flows/
│   ├── chat.py             # AI chat functionality and key ideas generation
│   ├── prompts.py          # AI prompts for content generation
│   └── schemas.py          # JSON schemas for AI responses
├── database/
│   └── models.py           # SQLAlchemy database models
└── settings/
    └── settings.py         # Global settings management
```

## Key Features

- **Spaced Repetition**: FSRS and SM2 algorithm support for optimized learning
- **AI Integration**: OpenAI-powered key ideas extraction from markdown content
- **Deck Management**: Organize flashcards into decks with custom parameters
- **Review Tracking**: Comprehensive analytics and review history
- **Settings**: Persistent configuration with global settings object

## Database Models

- **Deck**: Flashcard collections with FSRS parameters
- **Card**: Individual flashcards with scheduling state
- **Review**: Detailed review history and analytics
- **Message**: Chat/AI interaction logs

## AI Features

- **Key Ideas Generation**: Extract structured learning points from markdown text
- **JSON Schema Validation**: Structured AI responses with title/description format
- **Settings Integration**: API keys managed through global settings

## Development Notes

- Uses PyQt5 for cross-platform GUI
- SQLAlchemy for database ORM
- OpenAI SDK for AI functionality
- Singleton pattern for global settings management
- Structured logging and error handling

## Settings

Global settings are persisted to `~/.quint/config.json` and include:
- Documents path for file storage
- Spaced repetition algorithm selection (FSRS/SM2)
- OpenAI API key for AI features

## Testing

Run tests with the appropriate framework (check project files for specific commands).

## Build Commands

Check package.json or project files for build and lint commands.