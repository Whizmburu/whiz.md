# commands/utility/quote_command.py
# Needs a source for quotes. Can be a local list/file or an API.
# Example API: quotable.io (https://github.com/lukePeavey/quotable) - no key needed for random.
import requests # For using an API
import json
import random

# Using quotable.io for random quotes
QUOTABLE_API_RANDOM_URL = "https://api.quotable.io/random"
# Fallback quotes if API fails or for offline use (small list)
FALLBACK_QUOTES = [
    {"content": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
    {"content": "Strive not to be a success, but rather to be of value.", "author": "Albert Einstein"},
    {"content": "The mind is everything. What you think you become.", "author": "Buddha"},
    {"content": "Your time is limited, so don't waste it living someone else's life.", "author": "Steve Jobs"},
    {"content": "The best way to predict the future is to create it.", "author": "Peter Drucker"}
]

async def handle_quote(message, args, client, bot_instance):
    """
    Handles the /quote command.
    Fetches a random motivational or inspirational quote.
    Can optionally take a keyword to search for quotes (not implemented with this simple API).
    """
    quote_data = None
    source = "API (quotable.io)"

    try:
        # In an async context, aiohttp would be preferred.
        print("Note: Using synchronous 'requests' in async function for quote. Consider 'aiohttp'.")
        response = requests.get(QUOTABLE_API_RANDOM_URL, timeout=5) # 5 second timeout
        response.raise_for_status()
        quote_data = response.json()

        if not quote_data or 'content' not in quote_data or 'author' not in quote_data:
            raise ValueError("Invalid data from API")

    except (requests.exceptions.RequestException, ValueError, json.JSONDecodeError) as e:
        # bot_instance.logger.warning(f"Quote API error or bad data: {e}. Using fallback.", exc_info=True)
        print(f"Quote API error or bad data: {e}. Using fallback.")
        quote_data = random.choice(FALLBACK_QUOTES)
        source = "Fallback List"
    except Exception as e:
        # bot_instance.logger.error(f"Unexpected quote error: {e}", exc_info=True)
        print(f"Unexpected quote error: {e}. Using fallback.")
        quote_data = random.choice(FALLBACK_QUOTES)
        source = "Fallback List (due to unexpected error)"

    if quote_data:
        response_message = (
            f"📜 **Quote of the Moment** 📜\n\n"
            f"\"{quote_data['content']}\"\n"
            f"— *{quote_data['author']}*\n\n"
            # f"(Source: {source})" # Optional: for debugging or if you want to show source
        )
    else:
        # This should ideally not happen if fallback always works
        response_message = "⚠️ Sorry, I couldn't fetch a quote at this time."

    # await message.reply(response_message) # Placeholder
    print(f"Output for /quote:\n{response_message}")
    if source.startswith("API"):
        print("Reminder: 'requests' (or 'aiohttp') library is required for API quotes.")


if __name__ == '__main__':
    import asyncio

    class MockMessage:
        async def reply(self, text):
            print(f"BOT REPLIED: {text}")

    mock_msg = MockMessage()

    async def test_quote():
        print("--- Test 1: Fetch a quote (might use API or fallback) ---")
        await handle_quote(mock_msg, [], None, None)

        print("\n--- Test 2: Fetch another quote ---")
        await handle_quote(mock_msg, [], None, None)

    # To test fallback, you could temporarily disable network or use an invalid URL
    # For example:
    # original_url = QUOTABLE_API_RANDOM_URL
    # QUOTABLE_API_RANDOM_URL = "http://localhost:12345/nonexistent"
    # print("\n--- Test 3: Force Fallback (simulated by bad URL) ---")
    # await handle_quote(mock_msg, [], None, None)
    # QUOTABLE_API_RANDOM_URL = original_url # Restore

    asyncio.run(test_quote())
