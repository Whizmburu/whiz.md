# commands/text_fonts/emoji_command.py
import asyncio
import emoji # Python emoji library

async def handle_emoji(message, args, client, bot_instance):
    """
    Handles the /emoji command.
    Replaces emoji codes (like :smile:) in text with actual emojis.
    Or, if given a keyword, tries to find a matching emoji.
    Usage: /emoji :keyword: some text with :another_keyword:
           /emoji search <keyword>
    """
    command_name = "emoji"
    print(f"Executing /{command_name} with args: {args} for message: {message.sender if hasattr(message, 'sender') else 'Unknown'}")

    if not args:
        if hasattr(message, 'reply'): await message.reply(f"Usage: /{command_name} <text_with_emoji_codes> OR /{command_name} search <keyword>")
        return

    input_text = " ".join(args)

    # Option 1: Search for an emoji by keyword
    if args[0].lower() == "search" and len(args) > 1:
        search_keyword = args[1]
        # emoji.emojize can also take aliases, let's try that
        # We need to find an emoji from a keyword, not just replace :alias:
        # The emoji library doesn't have a direct search function in the way one might expect for finding *any* emoji by description.
        # It mainly works with known aliases (like :smile:) or by iterating through its EMOJI_DATA.

        found_emojis = []
        # A simple search through emoji aliases and names
        for emoji_char, data in emoji.EMOJI_DATA.items():
            if search_keyword.lower() in data['en'].lower() or search_keyword.lower() in data['alias']:
                found_emojis.append(f"{emoji_char} ({data['en']})")

        if found_emojis:
            reply_text = f"Emojis found for '{search_keyword}':\n" + "\n".join(found_emojis[:10]) # Show top 10 matches
            if len(found_emojis) > 10:
                reply_text += f"\n...and {len(found_emojis) - 10} more."
        else:
            # Try emojize with the keyword as an alias directly
            single_emoji_from_alias = emoji.emojize(f":{search_keyword.lower()}:", language='alias')
            if single_emoji_from_alias != f":{search_keyword.lower()}:": # Check if replacement happened
                 reply_text = f"Direct alias match for ':{search_keyword}:' -> {single_emoji_from_alias}"
            else:
                reply_text = f"No direct emoji alias or simple match found for '{search_keyword}'. Try more general terms or use :alias: format in text."

        if hasattr(message, 'reply'): await message.reply(reply_text)
        return

    # Option 2: Emojize the whole text (replace :aliases: with emojis)
    # The emoji.emojize function handles :alias: style replacements.
    emojified_text = emoji.emojize(input_text, language='alias')

    if hasattr(message, 'reply'):
        if emojified_text == input_text and not ":" in input_text : # No aliases were found and no colons were in input
             await message.reply(f"No emoji aliases (like :smile:) found in your text. For search, use `/{command_name} search <keyword>`.\nYour text: {input_text}")
        else:
            await message.reply(emojified_text)
    else:
        print(f"Original: {input_text}\nEmojified: {emojified_text}")


if __name__ == '__main__':
    class MockMessage:
        def __init__(self, text, sender):
            self.text = text
            self.sender = sender
        async def reply(self, text_content):
            print(f"BOT REPLIED TO {self.sender}: {text_content}")

    class MockClient: pass
    class MockBotInstance: pass

    async def main_test():
        mock_bot = MockBotInstance()
        mock_client = MockClient()

        print("\n--- Emoji Command Test Cases ---")

        print("\nTest 1: Text with emoji aliases")
        msg1 = MockMessage("/emoji Hello :world_map:, this is a :grinning_face_with_big_eyes: test with a :rocket:!", "TestUserEmoji_1")
        await handle_emoji(msg1, ["Hello", ":world_map:,", "this", "is", "a", ":grinning_face_with_big_eyes:", "test", "with", "a", ":rocket:!"], mock_client, mock_bot)

        print("\nTest 2: Text with no known aliases")
        msg2 = MockMessage("/emoji Just plain text.", "TestUserEmoji_2")
        await handle_emoji(msg2, ["Just", "plain", "text."], mock_client, mock_bot)

        print("\nTest 3: Search for an emoji (direct alias)")
        msg3 = MockMessage("/emoji search smile", "TestUserEmoji_3")
        await handle_emoji(msg3, ["search", "smile"], mock_client, mock_bot)

        print("\nTest 4: Search for an emoji (general keyword)")
        msg4 = MockMessage("/emoji search cat", "TestUserEmoji_4")
        await handle_emoji(msg4, ["search", "cat"], mock_client, mock_bot)

        print("\nTest 5: Search for non-existent emoji")
        msg5 = MockMessage("/emoji search nonexistentsymbol", "TestUserEmoji_5")
        await handle_emoji(msg5, ["search", "nonexistentsymbol"], mock_client, mock_bot)

        print("\nTest 6: No arguments")
        msg6 = MockMessage("/emoji", "TestUserEmoji_6")
        await handle_emoji(msg6, [], mock_client, mock_bot)

        print("\nTest 7: Only search keyword, no actual keyword")
        msg7 = MockMessage("/emoji search", "TestUserEmoji_7")
        await handle_emoji(msg7, ["search"], mock_client, mock_bot) # Should probably give usage

    asyncio.run(main_test())
