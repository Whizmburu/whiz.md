# commands/ai_tools/imagegen_command.py
# Needs an AI image generation library/SDK, e.g., 'openai' for DALL-E, or other services.
# Add relevant library (e.g., 'openai') to requirements.txt.
# Requires API key for the image generation service in .env (e.g., OPENAI_API_KEY).

from openai import OpenAI, APIError
from io import BytesIO # To handle image data
import requests # If image is returned as URL and needs to be downloaded
import asyncio # For sleep and async def

# Reuse the client getter from ask_command or define locally if preferred
# For simplicity, let's assume ask_command's _openai_clients and get_openai_client are accessible
# If not, they should be defined here or in a shared utility.
# from .ask_command import get_openai_client # This creates a circular dependency if ask_command imports from here.
# Let's define it locally or move to a shared util if many commands use it.

# Re-defining for clarity, or use a shared AI utils module later.
_openai_clients_img = {}
def get_openai_client_img(api_key):
    if api_key not in _openai_clients_img:
        _openai_clients_img[api_key] = OpenAI(api_key=api_key)
    return _openai_clients_img[api_key]


async def handle_imagegen(message, args, client, bot_instance):
    """
    Handles the /imagegen command.
    Generates an image from a text prompt using an AI model (e.g., DALL-E).
    Example: /imagegen A futuristic cityscape at sunset
    """
    if not args:
        await message.reply("Usage: `/imagegen <text_prompt_for_image>`\n"
                          "Example: `/imagegen A cute cat wearing a wizard hat`")
        return

    prompt = " ".join(args)
    api_key = bot_instance.config.openai_api_key # Assuming OpenAI for DALL-E

    if not api_key:
        await message.reply("⚠️ AI image generation service API key is not configured. This command is unavailable.")
        print("Error: OPENAI_API_KEY not found in config for /imagegen command.")
        return

    ai_client = get_openai_client_img(api_key) # Use the local or imported client getter
    reply_target = getattr(message, 'reply', print) # Helper for replies

    await reply_target(f"🎨 Generating image for prompt: \"{prompt[:100]}{'...' if len(prompt)>100 else ''}\". This might take a moment...")

    image_bytes = None
    response_message = ""

    try:
        # Using OpenAI DALL-E for image generation
        # Note: dall-e-2 is cheaper and faster, dall-e-3 has higher quality.
        # Ensure the API key has DALL-E access.
        # Synchronous client call - consider executor for async if this blocks too long.
        img_response = ai_client.images.generate(
            model="dall-e-2",  # Or "dall-e-3" if preferred and key supports it
            prompt=prompt,
            n=1,               # Number of images to generate
            size="1024x1024",  # Supported sizes: "256x256", "512x512", "1024x1024" for DALL-E 2
                               # DALL-E 3 supports "1024x1024", "1024x1792", "1792x1024"
            response_format="url"  # "url" or "b64_json"
        )

        if img_response.data and img_response.data[0].url:
            image_url = img_response.data[0].url
            # Download the image from the URL
            # Again, using synchronous requests here. Consider aiohttp for full async.
            print(f"Generated image URL: {image_url}. Downloading...")
            http_response = requests.get(image_url, timeout=30) # Increased timeout for image download
            http_response.raise_for_status() # Check for download errors
            image_bytes = BytesIO(http_response.content)

            # Sending the image using the client's method
            if image_bytes:
                final_caption = f"🖼️ AI Generated Image for: \"{prompt[:150]}{'...' if len(prompt)>150 else ''}\""
                # Assuming message object has chat_id for where to send it
                target_chat_id = getattr(message, 'chat_id', getattr(message, 'sender_id', 'unknown_chat'))
                sent_message_info = await client.send_image(
                    chat_id=target_chat_id,
                    image_data_or_path=image_bytes, # PyBaileyClient mock expects image_data_or_path
                    caption=final_caption
                )
                logger.info(f"AI Generated image sent, msg ID: {sent_message_info.get('id') if sent_message_info else 'N/A'}")
                # No need for further reply_target if image is sent directly to chat.
                # If a confirmation is desired:
                # await reply_target(f"Image for \"{prompt[:30]}...\" has been generated and sent!")
            else: # Should have been caught by check on image_url earlier, but as safeguard
                response_message = "⚠️ Image data was not available to send."
                await reply_target(response_message)
        else:
            response_message = "⚠️ AI image service did not return image data (no URL found in response)."
            await reply_target(response_message)

    except APIError as e:
        print(f"OpenAI API error for /imagegen: {e.status_code} - {e.message}")
        error_detail = str(e.message)[:100]
        if e.status_code == 401:
             response_message = "⚠️ OpenAI API Key is invalid or lacks DALL-E permission. Contact owner."
        elif e.status_code == 429:
            response_message = "⚠️ AI image service rate limit exceeded. Please try again later."
        elif "billing" in str(e.message).lower() or "quota" in str(e.message).lower():
             response_message = "⚠️ There's an issue with the API account billing or quota. Contact owner."
        elif e.status_code == 400 and "safety system" in str(e.message).lower(): # Content policy violation
            response_message = "⚠️ Your prompt was rejected by the AI's safety system. Please try a different prompt."
        else:
            response_message = f"⚠️ An API error occurred with the AI image service: {error_detail}"
        await reply_target(response_message)
    except requests.exceptions.RequestException as e:
        print(f"Error downloading generated image: {e}")
        await reply_target(f"⚠️ Image generated by AI, but failed to download it: {str(e)[:100]}")
    except Exception as e:
        print(f"Unexpected error in /imagegen: {e}")
        await reply_target(f"⚠️ An unexpected error occurred: {str(e)[:100]}")


if __name__ == '__main__':
    import asyncio
    import os

    class MockMessage:
        async def reply(self, text):
            print(f"BOT REPLIED: {text}")
        # chat_id would be used by client.send_image

    class MockConfig:
        def __init__(self):
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
            if not self.openai_api_key:
                print("TEST INFO: OPENAI_API_KEY not found in env. /imagegen will simulate.")
                self.openai_api_key = "sk-dummykeyforimagegen"

    class MockBotInstance:
        def __init__(self):
            self.config = MockConfig()

    # Mock client for placeholder send_image
    class MockClient:
        async def send_image(self, chat_id, image, caption): # Define expected signature
            # In a real test, you might check image data.
            print(f"MOCK_CLIENT: Sending image to {chat_id} with caption: \"{caption}\" (image data placeholder)")

    mock_msg = MockMessage()
    mock_bot = MockBotInstance()
    mock_client = MockClient() # For the eventual client.send_image call

    async def test_imagegen():
        print("--- Test 1: Generate an image ---")
        await handle_imagegen(mock_msg, ["A", "photo", "of", "a", "happy", "robot", "gardening"], mock_client, mock_bot)

        print("\n--- Test 2: No arguments ---")
        await handle_imagegen(mock_msg, [], mock_client, mock_bot)

        original_key = mock_bot.config.openai_api_key
        mock_bot.config.openai_api_key = None
        print("\n--- Test 3: No API Key configured ---")
        await handle_imagegen(mock_msg, ["This", "should", "fail"], mock_client, mock_bot)
        mock_bot.config.openai_api_key = original_key

    asyncio.run(test_imagegen())
