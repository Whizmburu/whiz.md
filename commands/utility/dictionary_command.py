# commands/utility/dictionary_command.py
# Needs an API for dictionary definitions or a library like PyDictionary (which scrapes).
# PyDictionary might be unreliable. A proper API (e.g., Merriam-Webster, Oxford Dictionaries)
# would require an API key stored in .env.
# For this placeholder, let's assume we'll try PyDictionary.
# Add 'PyDictionary' to requirements.txt.
# from PyDictionary import PyDictionary # This can be slow and error-prone

# Alternative: Use a free dictionary API if available, e.g., api.dictionaryapi.dev
import requests # For using a free API
import json

# Using api.dictionaryapi.dev as an example - no API key needed for this one.
DICTIONARY_API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"

async def handle_dictionary(message, args, client, bot_instance):
    """
    Handles the /dictionary command.
    Provides definitions for a given word.
    Example: /dictionary serendipity
    """
    if not args:
        await message.reply("Usage: `/dictionary <word_to_define>`\nExample: `/dictionary knowledge`")
        return

    word = " ".join(args) # Handle multi-word terms if the API supports it, though usually it's single words.

    try:
        # Using requests for the dictionary API
        # In an async context, aiohttp would be preferred.
        print("Note: Using synchronous 'requests' in async function for dictionary. Consider 'aiohttp'.")
        response = requests.get(f"{DICTIONARY_API_URL}{word}")

        if response.status_code == 404:
            await message.reply(f"😕 Sorry, I couldn't find a definition for \"{word}\". Please check the spelling.")
            return

        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        definitions_data = response.json()

        if not definitions_data or not isinstance(definitions_data, list):
            await message.reply(f"😕 No definitions found for \"{word}\", or the data format was unexpected.")
            return

        # Formatting the output
        response_parts = [f"📚 **Definitions for: {word.capitalize()}**\n"]

        for entry in definitions_data: # API returns a list of entries for the word
            if 'meanings' in entry:
                for meaning in entry['meanings']:
                    part_of_speech = meaning.get('partOfSpeech', 'N/A')
                    response_parts.append(f"\n🗣️ **As {part_of_speech.capitalize()}:**")
                    for i, definition_obj in enumerate(meaning.get('definitions', [])):
                        if i >= 3: # Limit to 3 definitions per part of speech for brevity
                            response_parts.append("   ...")
                            break
                        definition_text = definition_obj.get('definition', 'No definition text.')
                        example = definition_obj.get('example')
                        response_parts.append(f"  - {definition_text}")
                        if example:
                            response_parts.append(f"    *Example: \"{example}\"*")

            # Phonetics (optional)
            if 'phonetics' in entry and entry['phonetics']:
                phonetic_texts = [p.get('text') for p in entry['phonetics'] if p.get('text')]
                if phonetic_texts:
                     response_parts.append(f"\n🔊 Phonetics: {', '.join(phonetic_texts)}")


        if len(response_parts) <= 1: # Only title was added
             await message.reply(f"😕 No clear definitions found for \"{word}\" in the received data.")
             return

        response_message = "\n".join(response_parts)

        # Truncate if too long for WhatsApp
        max_len = 4000 # Approximate WhatsApp message limit
        if len(response_message) > max_len:
            response_message = response_message[:max_len-50] + "\n... (message truncated due to length)"

    except requests.exceptions.RequestException as e:
        # bot_instance.logger.error(f"Dictionary API request error: {e}", exc_info=True)
        print(f"Dictionary API request error: {e}")
        response_message = "⚠️ Sorry, I couldn't connect to the dictionary service."
    except (json.JSONDecodeError, KeyError, IndexError, TypeError) as e:
        # bot_instance.logger.error(f"Dictionary data parsing error: {e}", exc_info=True)
        print(f"Dictionary data parsing error: {e} - Response: {response.text if 'response' in locals() else 'N/A'}")
        response_message = f"⚠️ Sorry, I couldn't parse the dictionary data for \"{word}\"."
    except Exception as e:
        # bot_instance.logger.error(f"Unexpected dictionary error: {e}", exc_info=True)
        print(f"Unexpected dictionary error: {e}")
        response_message = f"⚠️ An unexpected error occurred while fetching the definition."

    # await message.reply(response_message) # Placeholder
    print(f"Output for /dictionary:\n{response_message}")
    print("Reminder: 'requests' (or 'aiohttp') library is required.")


if __name__ == '__main__':
    import asyncio

    class MockMessage:
        async def reply(self, text):
            print(f"BOT REPLIED: {text}")

    mock_msg = MockMessage()

    async def test_dictionary():
        print("--- Test 1: Define 'hello' ---")
        await handle_dictionary(mock_msg, ["hello"], None, None)

        print("\n--- Test 2: Define 'serendipity' ---")
        await handle_dictionary(mock_msg, ["serendipity"], None, None)

        print("\n--- Test 3: Word not found ---")
        await handle_dictionary(mock_msg, ["flibbertigibbetgibberish"], None, None)

        print("\n--- Test 4: No arguments ---")
        await handle_dictionary(mock_msg, [], None, None)

    asyncio.run(test_dictionary())
