# commands/dev_tools/jsonfmt_command.py
import asyncio
import json

async def handle_jsonfmt(message, args, client, bot_instance):
    """
    Handles the /jsonfmt command.
    Formats a JSON string with indentation for pretty printing.
    Usage: /jsonfmt <json_string>
    """
    command_name = "jsonfmt"
    print(f"Executing /{command_name} with args: {args} for message: {message.sender if hasattr(message, 'sender') else 'Unknown'}")

    if not args:
        if hasattr(message, 'reply'): await message.reply(f"Usage: /{command_name} <JSON string to format>")
        return

    json_string_to_format = " ".join(args)
    formatted_json_string = ""
    reply_message = ""

    try:
        # Attempt to parse the JSON string
        parsed_json = json.loads(json_string_to_format)
        # Re-serialize with indentation (4 spaces is common, can be configured)
        formatted_json_string = json.dumps(parsed_json, indent=4, sort_keys=True) # sort_keys for consistent output
        reply_message = f"📄 Formatted JSON:\n```json\n{formatted_json_string}\n```"
    except json.JSONDecodeError as e:
        reply_message = f"⚠️ Invalid JSON string: {e}. Please check your input.\nError at line {e.lineno}, column {e.colno} (char {e.pos})."
    except Exception as e:
        print(f"Error in jsonfmt command: {e}")
        reply_message = f"An unexpected error occurred while formatting JSON: {e}"

    if hasattr(message, 'reply'):
        await message.reply(reply_message)
    else:
        # Print without markdown for console testing if reply_message is the success one
        if "Formatted JSON" in reply_message:
             print(f"Formatted JSON:\n{formatted_json_string}")
        else:
            print(reply_message)


if __name__ == '__main__':
    class MockMessage:
        def __init__(self, text, sender):
            self.text = text
            self.sender = sender
        async def reply(self, text_content):
            print(f"BOT REPLIED TO {self.sender}:\n{text_content}")

    class MockClient: pass
    class MockBotInstance: pass

    async def main_test():
        mock_bot = MockBotInstance()
        mock_client = MockClient()

        print("\n--- JSON Format Test Cases ---")

        valid_compact_json = '{"name":"Whiz-MD","version":1,"features":["awesome","cool","fast"]}'
        expected_formatted_json_part = '"name": "Whiz-MD"' # Just a part to check

        print("\nTest 1: Valid compact JSON")
        msg1 = MockMessage(f"/jsonfmt {valid_compact_json}", "TestUserJSON_1")
        await handle_jsonfmt(msg1, [valid_compact_json], mock_client, mock_bot)

        already_formatted_json = """
        {
            "user": "test",
            "id": 123
        }
        """
        print("\nTest 2: Already formatted JSON (should re-format with consistent indent/sort)")
        msg2 = MockMessage(f"/jsonfmt {already_formatted_json}", "TestUserJSON_2")
        await handle_jsonfmt(msg2, [already_formatted_json], mock_client, mock_bot)

        invalid_json_missing_quote = '{"name":"Whiz-MD", "error: true}' # error value not quoted
        print("\nTest 3: Invalid JSON (missing quote on value)")
        msg3 = MockMessage(f"/jsonfmt {invalid_json_missing_quote}", "TestUserJSON_3")
        await handle_jsonfmt(msg3, [invalid_json_missing_quote], mock_client, mock_bot)

        invalid_json_trailing_comma = '{"name":"Whiz-MD", "features":["one",]}' # Trailing comma in list
        print("\nTest 4: Invalid JSON (trailing comma)")
        msg4 = MockMessage(f"/jsonfmt {invalid_json_trailing_comma}", "TestUserJSON_4")
        await handle_jsonfmt(msg4, [invalid_json_trailing_comma], mock_client, mock_bot)

        print("\nTest 5: No arguments")
        msg5 = MockMessage("/jsonfmt", "TestUserJSON_5")
        await handle_jsonfmt(msg5, [], mock_client, mock_bot)

        json_with_unicode = '{"message": "こんにちは世界"}'
        print("\nTest 6: JSON with Unicode characters")
        msg6 = MockMessage(f"/jsonfmt {json_with_unicode}", "TestUserJSON_6")
        await handle_jsonfmt(msg6, [json_with_unicode], mock_client, mock_bot)

    asyncio.run(main_test())
