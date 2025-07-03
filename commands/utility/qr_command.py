# commands/utility/qr_command.py
# Needs 'qrcode' and 'Pillow' libraries. Add to requirements.txt
# qrcode[pil] might install both.
import qrcode
from io import BytesIO

async def handle_qr(message, args, client, bot_instance):
    """
    Handles the /qr command.
    Generates a QR code for the given text.
    Example: /qr https://whiz.md
    """
    if not args:
        await message.reply("Usage: `/qr <text_to_encode>`\nExample: `/qr Hello Whiz-MD`")
        return

    text_to_encode = " ".join(args)

    try:
        qr_img = qrcode.make(text_to_encode)

        # Save QR code to a BytesIO object to send as an image
        img_byte_arr = BytesIO()
        qr_img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0) # Rewind to the start of the stream

        # Sending an image depends on the WhatsApp library.
        # Placeholder for sending image:
        # await client.send_image(
        #     message.chat_id, # or message.reply_to_message_id for replying
        #     image=img_byte_arr,
        #     caption=f"QR Code for: \"{text_to_encode[:50]}{'...' if len(text_to_encode) > 50 else ''}\""
        # )

        print(f"Output for /qr: Generated QR code for \"{text_to_encode}\". (Image data not printed).")
        print("Reminder: 'qrcode' and 'Pillow' (or 'qrcode[pil]') libraries are required.")
        await message.reply(f"✅ QR Code generated for: `{text_to_encode}`. (Imagine an image is sent here!)")

    except Exception as e:
        # bot_instance.logger.error(f"QR generation error: {e}", exc_info=True)
        print(f"Error generating QR: {e}")
        await message.reply(f"⚠️ Sorry, I couldn't generate a QR code for that. Error: {e}")


if __name__ == '__main__':
    import asyncio

    class MockMessage:
        async def reply(self, text):
            print(f"BOT REPLIED: {text}")
        # In a real scenario, this would also have chat_id or similar
        # for client.send_image

    # Mock client for placeholder send_image
    class MockClient:
        async def send_image(self, chat_id, image, caption):
            print(f"MOCK_CLIENT: Sending image to {chat_id} with caption: \"{caption}\" (image data length: {len(image.getvalue())})")

    mock_msg = MockMessage()
    mock_client = MockClient() # Not fully used in placeholder, but for structure

    async def test_qr():
        print("--- Test 1: Simple text ---")
        await handle_qr(mock_msg, ["Hello", "Whiz-MD"], mock_client, None)

        print("\n--- Test 2: URL ---")
        await handle_qr(mock_msg, ["https://github.com/WHIZ-MD/Bot"], mock_client, None)

        print("\n--- Test 3: No arguments ---")
        await handle_qr(mock_msg, [], mock_client, None)

        # Test very long string (qrcode library handles it, but caption is truncated)
        long_string = "This is a very long string designed to test the QR code generation and caption truncation logic. " * 3
        print("\n--- Test 4: Long string ---")
        await handle_qr(mock_msg, [long_string], mock_client, None)

    asyncio.run(test_qr())
