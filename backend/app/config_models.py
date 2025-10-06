"""
AI Model Configuration
Centralized configuration for AI models used in the application.
"""

# OpenAI Model Configuration
OPENAI_MODEL = "gpt-5-nano"  # Model for sentiment analysis
# Note: gpt-5-nano only supports temperature=1.0 (default), so we don't set it

# Model fallback chain
MODEL_FALLBACK_CHAIN = [
    "gpt-5-nano",
    "gpt-4o-mini",  # Fallback if gpt-5-nano is unavailable
]

def get_openai_model():
    """Get the configured OpenAI model name."""
    return OPENAI_MODEL

def get_model_config():
    """Get the full model configuration for OpenAI API calls.
    Note: temperature is not included as gpt-5-nano only supports default (1.0).
    """
    return {
        "model": OPENAI_MODEL,
        # temperature not supported by gpt-5-nano
        "response_format": {"type": "json_object"},  # Force JSON responses
    }
