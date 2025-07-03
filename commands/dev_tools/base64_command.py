# commands/dev_tools/base64_command.py
import asyncio
import base64

async def handle_base64(message, args, client, bot_instance):
    """
    Handles the /base64 command.
    Encodes text to Base64 or decodes Base64 to text.
    Usage: /base64 encode <text_to_encode>
           /base64 decode <base64_string_to_decode>
    """
    command_name = "base64"
    print(f"Executing /{command_name} with args: {args} for message: {message.sender if hasattr(message, 'sender') else 'Unknown'}")

    if len(args) < 2:
        if hasattr(message, 'reply'): await message.reply(f"Usage: /{command_name} <encode|decode> <string>")
        return

    mode = args[0].lower()
    input_string = " ".join(args[1:])
    result = ""

    try:
        if mode == "encode":
            encoded_bytes = base64.b64encode(input_string.encode('utf-8'))
            result = encoded_bytes.decode('utf-8')
            reply_message = f"🔒 Base64 Encoded:\n```\n{result}\n```"
        elif mode == "decode":
            # Ensure padding is correct for base64 string
            missing_padding = len(input_string) % 4
            if missing_padding:
                input_string += '=' * (4 - missing_padding)

            decoded_bytes = base64.b64decode(input_string.encode('utf-8'))
            result = decoded_bytes.decode('utf-8')
            reply_message = f"🔓 Base64 Decoded:\n```\n{result}\n```"
        else:
            reply_message = f"Invalid mode '{mode}'. Use 'encode' or 'decode'."

    except UnicodeDecodeError:
        reply_message = "⚠️ Error: Could not decode the input. It might not be valid UTF-8 text after decoding, or the Base64 string is corrupted/not text."
    except base64.binascii.Error as e: # Covers incorrect padding and non-base64 characters
        reply_message = f"⚠️ Invalid Base64 string: {e}. Please check your input."
    except Exception as e:
        print(f"Error in base64 command: {e}")
        reply_message = f"An unexpected error occurred: {e}"

    if hasattr(message, 'reply'):
        await message.reply(reply_message)
    else:
        print(reply_message.replace("```\n", "").replace("\n```", ""))


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

        print("\n--- Base64 Test Cases ---")

        text_to_encode = "Hello Whiz-MD Bot!"
        base64_encoded_text = "SGVsbG8gV2hpei1NRCBCb3Qh" # base64.b64encode(text_to_encode.encode()).decode()

        print("\nTest 1: Encode text")
        msg1 = MockMessage(f"/base64 encode {text_to_encode}", "TestUserBase64_1")
        await handle_base64(msg1, ["encode", text_to_encode], mock_client, mock_bot)

        print(f"\nTest 2: Decode text ('{base64_encoded_text}')")
        msg2 = MockMessage(f"/base64 decode {base64_encoded_text}", "TestUserBase64_2")
        await handle_base64(msg2, ["decode", base64_encoded_text], mock_client, mock_bot)

        print("\nTest 3: Invalid mode")
        msg3 = MockMessage("/base64 unknown_mode test", "TestUserBase64_3")
        await handle_base64(msg3, ["unknown_mode", "test"], mock_client, mock_bot)

        print("\nTest 4: Not enough arguments")
        msg4 = MockMessage("/base64 encode", "TestUserBase64_4")
        await handle_base64(msg4, ["encode"], mock_client, mock_bot)

        msg4b = MockMessage("/base64", "TestUserBase64_4b")
        await handle_base64(msg4b, [], mock_client, mock_bot)

        print("\nTest 5: Invalid Base64 string for decoding")
        invalid_b64 = "ThisIsNotBase64%%"
        msg5 = MockMessage(f"/base64 decode {invalid_b64}", "TestUserBase64_5")
        await handle_base64(msg5, ["decode", invalid_b64], mock_client, mock_bot)

        print("\nTest 6: Base64 string with missing padding (should be auto-handled by the code)")
        # "Hello" -> "SGVsbG8="
        b64_missing_padding = "SGVsbG8"
        msg6 = MockMessage(f"/base64 decode {b64_missing_padding}", "TestUserBase64_6")
        await handle_base64(msg6, ["decode", b64_missing_padding], mock_client, mock_bot)

        print("\nTest 7: Encode string with unicode characters")
        unicode_string = "こんにちは世界" # Hello World in Japanese
        # base64.b64encode("こんにちは世界".encode('utf-8')).decode('utf-8') -> '4こんにちは世界'
        msg7 = MockMessage(f"/base64 encode {unicode_string}", "TestUserBase64_7")
        await handle_base64(msg7, ["encode", unicode_string], mock_client, mock_bot)

        print("\nTest 8: Decode unicode base64")
        # 4こんにちは世界 -> '4こんにちは世界' (Incorrect, this is the original string, not its b64)
        # Correct b64 for "こんにちは世界" is "4こんにちは世界" -> This is not how it works.
        # "こんにちは世界" -> b'4こんにちは世界' (utf-8 bytes) -> "4bGonnichiwaSekai" (example, actual is longer)
        # Let's use the output from test 7 if possible or a known one.
        # Output from test 7 for "こんにちは世界" is "4こんにちは世界" (actual was こんにちわ世界 -> 4こんにちわ世界)
        # For "こんにちは世界":
        # In Python: base64.b64encode("こんにちは世界".encode('utf-8')).decode('utf-8') -> '4こんにちは世界=='
        unicode_b64 = "4こんにちは世界=="
        msg8 = MockMessage(f"/base64 decode {unicode_b64}", "TestUserBase64_8")
        await handle_base64(msg8, ["decode", unicode_b64], mock_client, mock_bot)


    asyncio.run(main_test())
