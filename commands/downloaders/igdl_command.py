# commands/downloaders/igdl_command.py
import instaloader
import os
import asyncio
import re

async def handle_igdl(message, args, client, bot_instance):
    """
    Handles the /igdl command (Instagram Downloader).
    Downloads content (image or video) from an Instagram post URL.
    Note: May require login for private accounts or certain content.
          This basic implementation attempts anonymous download.
    """
    command_name = "igdl"
    print(f"Executing /{command_name} with args: {args} for message: {message.sender if hasattr(message, 'sender') else 'Unknown'}")

    if not args:
        if hasattr(message, 'reply'): await message.reply("Please provide an Instagram post URL after the command.")
        return

    post_url = args[0]
    # Basic regex for Instagram post URL
    if not re.match(r"(https|http)://(www\.)?instagram\.com/(p|reel|tv)/[\w-]+/?", post_url):
        if hasattr(message, 'reply'): await message.reply("Invalid Instagram post URL provided.")
        return

    output_dir = "downloads/instagram"
    os.makedirs(output_dir, exist_ok=True)

    L = instaloader.Instaloader(
        dirname_pattern=output_dir,
        # filename_pattern="{profile}_{shortcode}", # Default is fine
        download_pictures=True,
        download_videos=True,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        # quiet=True # Suppress Instaloader's console output
    )
    # For downloading without login, Instaloader will try its best.
    # To download private posts, login is required:
    # L.login(USER, PASSWORD) # This would need credentials from config

    try:
        shortcode = instaloader.Post.shortcode_from_url(post_url)
        if not shortcode:
            if hasattr(message, 'reply'): await message.reply("Could not extract shortcode from Instagram URL.")
            return

        if hasattr(message, 'reply'): await message.reply("📥 Fetching Instagram post, please wait...")
        print(f"Attempting to download Instagram post: {post_url} (shortcode: {shortcode})")

        post = instaloader.Post.from_shortcode(L.context, shortcode)

        # Instaloader will download files to a subdirectory named after the profile
        # e.g., downloads/instagram/profile_name/filename.jpg
        # We need to find the path of the downloaded file(s).

        target_profile_dir = os.path.join(output_dir, post.owner_username)

        # Clear previous downloads for this shortcode in the specific profile directory to avoid confusion
        # This is a simple cleanup for testing; a more robust solution might be needed
        if os.path.exists(target_profile_dir):
            for item in os.listdir(target_profile_dir):
                if shortcode in item: # if old files from same shortcode exist
                    try:
                        os.remove(os.path.join(target_profile_dir, item))
                    except OSError as e:
                        print(f"Could not remove old file {item}: {e}")

        L.download_post(post, target=post.owner_username) # target specifies the subfolder name

        downloaded_files = []
        if os.path.exists(target_profile_dir):
            for item in os.listdir(target_profile_dir):
                # Instaloader names files like YYYY-MM-DD_HH-MM-SS_UTC_shortcode.jpg/mp4
                # or {profile}_{date_utc}_{shortcode}.jpg/mp4
                # We need to identify the main media file(s) associated with this specific post.
                # The default pattern is {date_utc}_{filename} inside the {profile} folder.
                # Let's assume files will contain the shortcode.
                if shortcode in item and (item.endswith(".jpg") or item.endswith(".jpeg") or item.endswith(".png") or item.endswith(".mp4")):
                    downloaded_files.append(os.path.join(target_profile_dir, item))

        if not downloaded_files:
            print(f"No media files found for post {shortcode} after download attempt.")
            if hasattr(message, 'reply'): await message.reply("⚠️ Could not download media from the post. It might be private, deleted, or an issue with Instaloader.")
            return

        for file_path in downloaded_files:
            file_size = os.path.getsize(file_path)
            print(f"Successfully downloaded Instagram media: {file_path}, Size: {file_size} bytes")
            caption = f"📸 IG: {post.caption[:50]}..." if post.caption else f"📸 Instagram content from {post.owner_username}"

            if hasattr(message, 'reply') and hasattr(client, 'send_file_simulation'):
                await client.send_file_simulation(
                    chat_id=message.sender,
                    filepath=file_path,
                    caption=caption
                )
            elif hasattr(message, 'reply'):
                await message.reply(f"✅ Successfully downloaded: {os.path.basename(file_path)} (Path: {file_path})")

            # Optional: Clean up
            # os.remove(file_path)

        if len(downloaded_files) > 1:
             if hasattr(message, 'reply'): await message.reply(f"Downloaded {len(downloaded_files)} items from the post (e.g., carousel).")


    except instaloader.exceptions.ConnectionException as e:
        print(f"Instaloader ConnectionException: {e}")
        if "Login required" in str(e) or "checkpoint_required" in str(e):
            if hasattr(message, 'reply'): await message.reply("⚠️ This post may require login to download (e.g., private account or login-restricted content).")
        else:
            if hasattr(message, 'reply'): await message.reply(f"⚠️ Connection error with Instagram: {str(e)[:100]}")
    except instaloader.exceptions.InstaloaderException as e: # Generic Instaloader error
        print(f"Instaloader generic exception: {e}")
        if hasattr(message, 'reply'): await message.reply(f"⚠️ An error occurred with Instaloader: {str(e)[:100]}")
    except Exception as e:
        print(f"An unexpected error occurred in igdl: {e}")
        if hasattr(message, 'reply'): await message.reply(f"⚠️ An unexpected error occurred: {str(e)[:100]}")
    finally:
        pass # Clean up L.context if needed, or handle session persistence

if __name__ == '__main__':
    class MockMessage:
        def __init__(self, text, sender):
            self.text = text
            self.sender = sender
        async def reply(self, text_content):
            print(f"BOT REPLIED TO {self.sender}: {text_content}")

    class MockClient:
        async def send_file_simulation(self, chat_id, filepath, caption):
            print(f"BOT SENDING FILE TO {chat_id}: {filepath}, Caption: {caption}")
            # if os.path.exists(filepath): os.remove(filepath)

    class MockBotInstance:
        def __init__(self):
            self.message_templates = None

    async def main_test():
        mock_bot = MockBotInstance()
        mock_client = MockClient()

        # Using a known public Instagram post URL. Replace with a current one if needed.
        # Make sure it's a simple image or video post for basic testing.
        # Example: A post from @instagram's official account (usually public and simple)
        # Find a public post URL, e.g., from a celebrity or brand that's unlikely to be private.
        # Let's use a placeholder - replace with a real, simple, public post URL for actual testing.
        # valid_ig_url = "https://www.instagram.com/p/Cxyzexample/" # Replace with a real URL
        # For this test, I'll use a well-known public post if possible, or skip if it's too volatile
        # Searching for a stable public post for testing:
        # Using a post from National Geographic (typically public and high quality)
        # Example: https://www.instagram.com/p/C7zbX04xL2N/ (Photo post)
        # Example: https://www.instagram.com/reel/C7w8X28Rgj2/ (Reel)

        valid_ig_url_photo = "https://www.instagram.com/p/C7zbX04xL2N/" # NatGeo Photo
        valid_ig_url_reel = "https://www.instagram.com/reel/C7w8X28Rgj2/" # NatGeo Reel

        print("\n--- igdl Test Case 1: Valid Instagram Photo URL ---")
        mock_msg_photo = MockMessage(f"/igdl {valid_ig_url_photo}", "TestUserIG_Photo")
        await handle_igdl(mock_msg_photo, [valid_ig_url_photo], mock_client, mock_bot)

        await asyncio.sleep(5) # Brief pause if Instaloader has internal rate limits/timing issues

        print("\n--- igdl Test Case 2: Valid Instagram Reel URL ---")
        mock_msg_reel = MockMessage(f"/igdl {valid_ig_url_reel}", "TestUserIG_Reel")
        await handle_igdl(mock_msg_reel, [valid_ig_url_reel], mock_client, mock_bot)

        await asyncio.sleep(5)

        print("\n--- igdl Test Case 3: Invalid URL ---")
        invalid_url = "https://example.com/not_instagram"
        mock_msg_invalid = MockMessage(f"/igdl {invalid_url}", "TestUserIG_Invalid")
        await handle_igdl(mock_msg_invalid, [invalid_url], mock_client, mock_bot)

        print("\n--- igdl Test Case 4: No URL ---")
        mock_msg_no_url = MockMessage("/igdl", "TestUserIG_NoURL")
        await handle_igdl(mock_msg_no_url, [], mock_client, mock_bot)

        # Note: Testing private posts would require credentials and is out of scope for this basic implementation.

    # Instaloader can be rate-limited or require session cookies for stability.
    # Running tests might hit these limits if run too frequently.
    # Consider adding delays or using a session file for Instaloader in a real bot.
    asyncio.run(main_test())
