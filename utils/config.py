import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()  # Load environment variables from .env file

        # Core Bot Configuration
        self.session_id = os.getenv("SESSION_ID")
        self.bot_name = os.getenv("BOT_NAME", "WHIZ-MD")
        self.owner_name = os.getenv("OWNER_NAME", "WHIZ")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

        # Runtime Variables
        self.port = os.getenv("PORT", "3000") # Default port if not specified
        self.host = os.getenv("HOST", "0.0.0.0") # Default host
        self.mode = os.getenv("MODE", "development") # e.g., development, production

        # Session ID Validation
        self.session_id_provider_url = "https://whizmdsessions.onrender.com"
        # The actual check for `startswith("WHIZ_")` will be done in the main bot script
        # or where the bot client is initialized, as it's a critical startup check.

        # Bot settings
        self.default_prefix = os.getenv("DEFAULT_PREFIX", "/")
        # Prefixes can be a list, loaded from a string like "/ . #"
        self.prefixes = [p.strip() for p in os.getenv("PREFIXES", "/ . # whz !").split()]

        self.support_group_link = os.getenv("SUPPORT_GROUP_LINK", "https://chat.whatsapp.com/JLmSbTfqf4I2Kh4SNJcWgM")
        self.repo_url = os.getenv("REPO_URL", "github.com/WHIZ-MD/Bot")

        # Logging configuration (example)
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()

        # Bot's actual WhatsApp number (used for /invite command)
        self.bot_whatsapp_number = os.getenv("BOT_WHATSAPP_NUMBER")

        # External API Keys
        self.openweathermap_api_key = os.getenv("OPENWEATHERMAP_API_KEY")
        # self.another_api_key = os.getenv("ANOTHER_API_KEY") # Example for future keys

        # Bot Owner JID (or number, depending on WhatsApp lib)
        self.owner_jid = os.getenv("OWNER_JID")

        # Feature Flags & Settings from .env
        self.auto_view_react_statuses_enabled = os.getenv("AUTO_VIEW_REACT_STATUSES_ENABLED", "false").lower() == "true"

        raw_emojis = os.getenv("STATUS_REACTION_EMOJIS")
        if raw_emojis:
            self.status_reaction_emojis = [emoji.strip() for emoji in raw_emojis.split(',')]
        else: # Default if not set or empty
            self.status_reaction_emojis = ["👍", "🔥", "❤️", "😂", "😮", "🎉", "💯"] # Default list from spec/common usage

        # WhatsApp Client Library specific settings
        self.whatsapp_client_service_url = os.getenv("WHATSAPP_CLIENT_SERVICE_URL", "ws://localhost:8080")
        self.whatsapp_session_path = os.getenv("WHATSAPP_SESSION_PATH", "./whatsapp_session_data")


    def validate_session_id(self):
        """
        Validates the SESSION_ID.
        Returns True if valid, False otherwise.
        Prints an error message if invalid.
        """
        if not self.session_id:
            print("🔴 ERROR: SESSION_ID is not set in the .env file.")
            print(f"🔗 Please visit {self.session_id_provider_url} to obtain a valid session ID.")
            return False
        if not self.session_id.startswith("WHIZ_"):
            print(f"🔴 ERROR: Invalid SESSION_ID format: '{self.session_id}'.")
            print("SESSION_ID must start with 'WHIZ_'.")
            print(f"🔗 Please visit {self.session_id_provider_url} to obtain a valid session ID.")
            return False
        return True

if __name__ == '__main__':
    # Example usage:
    config = Config()
    print(f"Bot Name: {config.bot_name}")
    print(f"Owner Name: {config.owner_name}")
    print(f"Session ID: {config.session_id}")
    print(f"OpenAI Key: {'Set' if config.openai_api_key else 'Not Set'}")
    print(f"Prefixes: {config.prefixes}")
    print(f"Support Group: {config.support_group_link}")

    if config.validate_session_id():
        print("Session ID is valid.")
    else:
        print("Session ID is invalid. Please check your .env file.")
