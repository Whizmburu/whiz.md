import os
import time
from datetime import datetime

from utils.config import Config
from utils.message_templates import MessageTemplates
from utils.logger import setup_logger # Import the logger setup function
import traceback # For logging exception tracebacks

# Placeholder for a WhatsApp client library
# For now, we'll use a MockClient for simulation.
# from whatsapp_client import WhatsAppClient # This is a hypothetical library

# Import command handlers
from commands.owner import *
from commands.utility import *
from commands.ai_tools import *
from commands.group_admin import *
from commands.media import *
from commands.fun import *
from commands.internet import *
from commands.downloaders import *
from commands.text_fonts import *
from commands.dev_tools import *

class MockClient: # Simple mock client for placeholder operations
    async def send_message(self, chat_id, text, **kwargs):
        # In a real client, this would send a message.
        # kwargs might include things like 'reply_to_message_id'
        print(f"MOCK_CLIENT: Sending message to {chat_id}: \"{text[:100]}{'...' if len(text) > 100 else ''}\"")

    async def send_file_simulation(self, chat_id, filepath, caption, **kwargs):
        # Simulates sending a file.
        print(f"MOCK_CLIENT: Sending file to {chat_id}: {filepath}, Caption: \"{caption}\"")
        # In a real bot, you might want to check if file exists, etc.
        # For some tests, command handlers might remove the file after sending.
        # if os.path.exists(filepath):
        #     print(f"File {filepath} exists. Size: {os.path.getsize(filepath)}")

    async def send_image_simulation(self, chat_id, image, caption, **kwargs):
        # Simulates sending an image (BytesIO object or path)
        image_info = f"BytesIO object (length: {len(image.getvalue())})" if hasattr(image, 'getvalue') else f"Path: {image}"
        print(f"MOCK_CLIENT: Sending image to {chat_id}: {image_info}, Caption: \"{caption}\"")


class WhizMdBot:
    def __init__(self):
        self.config = Config()
        self.logger = setup_logger('WhizMdBot', self.config.log_level) # Initialize logger
        self.logger.info("Initializing Whiz-MD Bot...")

        if not self.config.session_id or not self.config.session_id.startswith("WHIZ_"):
            self.logger.error("🔴 FATAL ERROR: Invalid or missing SESSION_ID.")
            self.logger.error(f"Please ensure your .env file has a valid SESSION_ID starting with 'WHIZ_'.")
            self.logger.error(f"You can obtain a valid session ID from: {self.config.session_id_provider_url}")
            exit(1)

        self.bot_name = self.config.bot_name
        self.owner_name = self.config.owner_name
        self.start_time = time.time()
        self.message_templates = MessageTemplates(self.owner_name, self.bot_name)

        # Initialize the mock client for now
        self.client = MockClient() # This would be the actual WhatsApp client instance

        self._register_commands()
        self.group_settings = {} # Initialize group-specific settings store

        # Placeholder for actual WhatsApp client event hookups
        # self.actual_whatsapp_client.on_message(self.handle_message)
        # self.actual_whatsapp_client.on_ready(self.on_ready)

        self.logger.info(self.message_templates.get_connected_message().strip()) # Use logger
        self.logger.info(f"Total commands loaded: {len(self.commands)}")


    def _register_commands(self):
        self.commands = {
            # Owner Commands
            "ping": handle_ping, "uptime": handle_uptime, "stats": handle_stats,
            "about": handle_about, "help": handle_help, "prefix": handle_prefix,
            "setprefix": handle_setprefix, "report": handle_report,
            "invite": handle_invite, "support": handle_support,
            # Utility Commands
            "calc": handle_calc, "qr": handle_qr, "translate": handle_translate,
            "shorturl": handle_shorturl, "weather": handle_weather, "time": handle_time,
            "reminder": handle_reminder, "timer": handle_timer,
            "dictionary": handle_dictionary, "quote": handle_quote,
            # AI / Tools Commands
            "ask": handle_ask, "imagegen": handle_imagegen, "summarize": handle_summarize,
            "codegen": handle_codegen, "chat": handle_chat,
            # Group Admin Commands
            "ban": handle_ban, "kick": handle_kick, "mute": handle_mute,
            "warn": handle_warn, "unban": handle_unban, "promote": handle_promote,
            "demote": handle_demote, "groupinfo": handle_groupinfo,
            "antilink": handle_antilink, "lockgroup": handle_lockgroup,
            # Media Commands
            "sticker": handle_sticker, "toimg": handle_toimg, "tomp3": handle_tomp3,
            "gifsticker": handle_gifsticker, "removebg": handle_removebg,
            "resize": handle_resize, "filter": handle_filter, "vv": handle_vv,
            # Fun Commands
            "joke": handle_joke, "meme": handle_meme, "8ball": handle_8ball,
            "truth": handle_truth, "dare": handle_dare, "ship": handle_ship,
            "rate": handle_rate, "rps": handle_rps, "coinflip": handle_coinflip,
            "guess": handle_guess,
            # Internet Commands
            "news": handle_news, "wiki": handle_wiki, "movie": handle_movie,
            "anime": handle_anime, "github": handle_github, "npm": handle_npm,
            # Downloaders Commands
            "ytmp3": handle_ytmp3, "ytmp4": handle_ytmp4, "igdl": handle_igdl,
            "tiktok": handle_tiktok, "fb": handle_fb, "twitter": handle_twitter,
            "mediafire": handle_mediafire, "apk": handle_apk,
            # Text & Fonts Commands
            "fancy": handle_fancy, "ascii": handle_ascii, "emoji": handle_emoji,
            "reverse": handle_reverse, "zalgo": handle_zalgo,
            "cursive": handle_cursive, "tinytext": handle_tinytext,
            # Dev Tools Commands
            "base64": handle_base64, "jsonfmt": handle_jsonfmt, "whois": handle_whois,
            "dns": handle_dns, "headers": handle_headers,
        }
        # Add menu as an alias for help or its own handler if different
        self.commands["menu"] = self.display_main_menu


    async def display_main_menu(self, message, args, client, bot_instance):
        """Handler for the /menu command."""
        self.logger.info(f"Executing menu command for {message.sender}")
        num_commands = len(self.commands)
        # Forks count is static as per spec, or could be fetched if bot has GitHub API access
        forks = 327 # From spec
        uptime = self.get_uptime()
        # Prefixes string from config
        current_prefixes_str = " | ".join(self.config.prefixes)

        menu_response = self.message_templates.get_main_menu(
            owner=self.owner_name,
            repo_url=self.config.repo_url,
            prefixes=current_prefixes_str,
            forks=forks,
            command_count=num_commands, # Dynamic command count
            uptime=uptime,
            support_group_link=self.config.support_group_link
        )
        # await message.reply(menu_response) # Placeholder
        # For testing with MockMessage that has reply
        if hasattr(message, 'reply'):
            await message.reply(menu_response)
        else: # Fallback for other types of calls
            print(menu_response)

    def on_ready(self):
        """Called when the bot is connected and ready."""
        # This is a placeholder. Actual implementation depends on the WhatsApp library.
        self.logger.info("Bot is ready (simulated on_ready event).")
        self.logger.info(self.message_templates.get_connected_message().strip())

    def get_uptime(self):
        """Calculates the bot's uptime."""
        uptime_seconds = time.time() - self.start_time
        days = int(uptime_seconds // (24 * 3600))
        uptime_seconds %= (24 * 3600)
        hours = int(uptime_seconds // 3600)
        uptime_seconds %= 3600
        minutes = int(uptime_seconds // 60)
        uptime_seconds %= 60
        seconds = int(uptime_seconds)

        if days > 0:
            return f"{days}d {hours}h {minutes}m {seconds}s"
        elif hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

    async def handle_message(self, message):
        """
        Handles incoming messages.
        This is a placeholder and will need to be fleshed out with command parsing
        and calling the respective command handlers.
        """
        # print(f"Received message: {message.text} from {message.sender}") # Example

        # Basic command parsing example
        # self.logger.debug(f"Received message: '{message.text}' from {message.sender}") # Example debug log
        text = message.text.strip()
        # Use prefixes from config
        current_prefixes = self.config.prefixes

        parsed_command_name = None
        args = []

        for prefix in current_prefixes:
            if text.startswith(prefix):
                # Ensure there's something after the prefix
                if len(text) > len(prefix):
                    command_body = text[len(prefix):]
                    parts = command_body.split()
                    if parts: # Ensure parts is not empty
                        parsed_command_name = parts[0].lower()
                        args = parts[1:]
                    else: # Prefix was typed, but no command after it
                        parsed_command_name = None # Or handle as a special case, e.g. show help
                break # Prefix found

        if not parsed_command_name:
            # print(f"Not a command or empty command for text: '{text}'") # Debugging
            return # Not a command or empty command string

        # Command dispatching
        command_handler = self.commands.get(parsed_command_name)

        if command_handler:
            self.logger.info(f"Executing command '{parsed_command_name}' for {message.sender} with args: {args}")
            try:
                # Pass self.client (mock or real) and self (bot_instance) to the handler
                await command_handler(message, args, self.client, self)
            except Exception as e:
                self.logger.error(f"🔴 ERROR executing command '{parsed_command_name}': {e}", exc_info=True)
                # Optionally, send a generic error message to the user
                if hasattr(message, 'reply'):
                    await message.reply(f"⚠️ An error occurred while trying to run the `{parsed_command_name}` command. Please try again later or report this if it persists.")
                # Log the full traceback for debugging (handled by exc_info=True)
        else:
            self.logger.debug(f"Command '{parsed_command_name}' not found for input: '{text}'")
            # Optional: reply if command is not found, or stay silent
            # For now, stay silent if command is not recognized after prefix.
            pass


    def run(self):
        """Starts the bot."""
        self.logger.info(f"{self.bot_name} is starting...")
        # In a real scenario, this would start the WhatsApp client connection
        # self.client.connect()
        self.logger.info(f"{self.bot_name} has started. Owner: {self.owner_name}")
        self.logger.info("Simulating bot running. Press Ctrl+C to stop.")

        # Simulate keeping the bot alive.
        # In a real bot, this would be handled by the WhatsApp client's event loop.
        try:
            # Keep the main thread alive, or manage the event loop of the WhatsApp client
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("\nShutting down Whiz-MD Bot...")
        finally:
            # Perform any cleanup here
            # if self.client:
            #     self.client.disconnect()
            self.logger.info("Whiz-MD Bot has been shut down.")

if __name__ == "__main__":
    bot = WhizMdBot()
    # bot.run() # We will run it once we have more pieces for a full run
    bot.logger.info("WhizMdBot initialized from __main__. Call bot.run() to start interactive simulation.")

    # For testing purposes, let's simulate a 'ready' event and some commands
    # This part will now use the logger internally when methods like on_ready, handle_message are called.
    bot.on_ready()

    # Simulate receiving messages (for testing the dispatcher)
    class MockMessage:
        def __init__(self, text, sender):
            self.text = text
            self.sender = sender
        async def reply(self, content): # Make reply async
            print(f"BOT REPLIED TO {self.sender}: {content}")

    import asyncio

    import os # For OWNER_JID test

    async def test_bot_commands(): # Make test_commands async
        bot.logger.info("--- Running Bot Command Test Suite ---")

        # Standard commands
        bot.logger.info("\n--- Test: /ping ---")
        await bot.handle_message(MockMessage("/ping", "TestUserPing"))

        bot.logger.info("\n--- Test: /menu ---")
        await bot.handle_message(MockMessage("/menu", "TestUserMenu"))

        bot.logger.info("\n--- Test: .help (different prefix) ---")
        await bot.handle_message(MockMessage(".help", "TestUserHelp"))

        # Owner command
        bot.logger.info("\n--- Test: /about ---")
        await bot.handle_message(MockMessage("/about", "TestUserAbout"))

        # Utility command
        bot.logger.info("\n--- Test: /qr Hello ---")
        await bot.handle_message(MockMessage("/qr Hello", "TestUserQR"))

        # AI command (will use dummy API key if real one not set in env for test)
        bot.logger.info("\n--- Test: /ask What is Python? ---")
        await bot.handle_message(MockMessage("/ask What is Python?", "TestUserAsk"))

        # Group Admin command (simulating in a way that it hits a check)
        # MockMessage needs group_id and is_sender_admin attributes for /antilink to test permissions
        # For /ban, it might just say "group only" or similar without full context.
        bot.logger.info("\n--- Test: /ban TestUser (group admin command) ---")
        # await bot.handle_message(MockMessage("/ban TestUser", "TestUserBan", group_id="TestGroup123", is_sender_admin=True))
        # Simpler test for now, will likely hit a "group only" or "admin only" path in the command if not fully mocked
        await bot.handle_message(MockMessage("/ban TestUser", "TestUserBan"))


        # Media command placeholder
        bot.logger.info("\n--- Test: /sticker (media command placeholder) ---")
        # Needs replied_to_message for actual functionality, just testing dispatch
        await bot.handle_message(MockMessage("/sticker", "TestUserSticker"))

        # Fun command placeholder
        bot.logger.info("\n--- Test: /joke (fun command placeholder) ---")
        await bot.handle_message(MockMessage("/joke", "TestUserJoke"))

        # Internet command placeholder
        bot.logger.info("\n--- Test: /news (internet command placeholder) ---")
        await bot.handle_message(MockMessage("/news", "TestUserNews"))

        # Downloader command - /ytmp3 (will ask for URL)
        bot.logger.info("\n--- Test: /ytmp3 (downloader command) ---")
        await bot.handle_message(MockMessage("/ytmp3", "TestUserYtmp3"))

        # Text & Fonts command
        bot.logger.info("\n--- Test: /fancy bold Test ---")
        await bot.handle_message(MockMessage("/fancy bold Test", "TestUserFancy"))

        # Dev Tools command
        bot.logger.info("\n--- Test: /base64 encode test ---")
        await bot.handle_message(MockMessage("/base64 encode test", "TestUserBase64"))

        # Highlight feature: /setprefix (testing permission)
        bot.logger.info("\n--- Test: /setprefix (as non-owner) ---")
        await bot.handle_message(MockMessage("/setprefix ! #", "TestUserSetprefixNonOwner"))

        owner_jid_for_test = bot.config.owner_jid if bot.config.owner_jid else "test_owner_id@example.com"
        if not bot.config.owner_jid: # If not set in .env, set a mock one for this test path
            bot.logger.warning(f"OWNER_JID not in .env, using mock '{owner_jid_for_test}' for /setprefix owner test.")
            bot.config.owner_jid = owner_jid_for_test
            original_owner_jid_in_config = False # Flag that we mocked it
        else:
            original_owner_jid_in_config = True

        bot.logger.info(f"\n--- Test: /setprefix ! # (as owner: {owner_jid_for_test}) ---")
        await bot.handle_message(MockMessage("/setprefix ! #", sender=owner_jid_for_test)) # Sender matches owner_jid
        bot.logger.info(f"Prefixes after set: {bot.config.prefixes}")

        bot.logger.info("\n--- Test: /setprefix reset (as owner) ---")
        await bot.handle_message(MockMessage("/setprefix reset", sender=owner_jid_for_test))
        bot.logger.info(f"Prefixes after reset: {bot.config.prefixes}")

        if not original_owner_jid_in_config: # Clean up if we mocked it
            bot.config.owner_jid = None


        # Non-existent command
        bot.logger.info("\n--- Test: !nonexistentcmd (non-existent command) ---")
        await bot.handle_message(MockMessage("!nonexistentcmd", "TestUserNonExistent"))

        # Command that causes an error
        bot.logger.info("\n--- Test: /calc 1/0 (command with error) ---")
        await bot.handle_message(MockMessage("/calc 1/0", "TestUserCalcError"))

    # Run the async test function
    asyncio.run(test_bot_commands())
    bot.logger.info("\n--- Main bot script __main__ execution finished ---")
