# commands/utility/shorturl_command.py
# Needs a library for URL shortening, e.g., 'pyshorteners'.
# Add 'pyshorteners' to requirements.txt
import pyshorteners

async def handle_shorturl(message, args, client, bot_instance):
    """
    Handles the /shorturl command.
    Shortens a given URL using a service like TinyURL.
    Example: /shorturl https://very.long.url/that/needs/shortening
    """
    if not args or not args[0].startswith(('http://', 'https://')):
        await message.reply("Usage: `/shorturl <URL_to_shorten>`\nExample: `/shorturl https://example.com`")
        return

    long_url = args[0]

    try:
        s = pyshorteners.Shortener()
        # Using TinyURL as it usually doesn't require an API key for basic use.
        # Other services might need API keys configured in .env
        short_url = s.tinyurl.short(long_url)

        response_message = (
            f"🔗 **URL Shortened** 🔗\n"
            f"Original: `{long_url}`\n"
            f"Shortened: `{short_url}`"
        )
    except pyshorteners.exceptions.ShorteningErrorException as e:
        # bot_instance.logger.error(f"URL shortening error: {e}", exc_info=True)
        print(f"URL shortening error: {e}")
        response_message = f"⚠️ Sorry, I couldn't shorten that URL. The service might be down or the URL invalid.\nError: {str(e)}"
    except Exception as e:
        # bot_instance.logger.error(f"Unexpected URL shortening error: {e}", exc_info=True)
        print(f"Unexpected URL shortening error: {e}")
        response_message = f"⚠️ An unexpected error occurred while shortening the URL: {str(e)}"

    # await message.reply(response_message) # Placeholder
    print(f"Output for /shorturl:\n{response_message}")
    print("Reminder: 'pyshorteners' library is required.")

if __name__ == '__main__':
    import asyncio

    class MockMessage:
        async def reply(self, text):
            print(f"BOT REPLIED: {text}")

    mock_msg = MockMessage()

    async def test_shorturl():
        print("--- Test 1: Valid URL ---")
        # Using a known service that pyshorteners can access without API key
        await handle_shorturl(mock_msg, ["https://github.com/WHIZ-MD/Bot"], None, None)

        print("\n--- Test 2: Another valid URL ---")
        await handle_shorturl(mock_msg, ["https://www.google.com/search?q=pyshorteners+library"], None, None)

        print("\n--- Test 3: Invalid URL (format) ---")
        await handle_shorturl(mock_msg, ["not_a_url"], None, None)

        print("\n--- Test 4: No arguments ---")
        await handle_shorturl(mock_msg, [], None, None)

        # This might fail if the domain is invalid or the service can't reach it
        # print("\n--- Test 5: Potentially unreachable/invalid domain ---")
        # await handle_shorturl(mock_msg, ["http://thisshouldnotexist12345.com"], None, None)


    asyncio.run(test_shorturl())
