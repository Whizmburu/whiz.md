# commands/downloaders/twitter_command.py
import yt_dlp
import os
import asyncio
import re

async def handle_twitter(message, args, client, bot_instance):
    """
    Handles the /twitter command (Twitter/X Video Downloader).
    Attempts to download video from a Twitter status URL using yt-dlp.
    """
    command_name = "twitter"
    print(f"Executing /{command_name} with args: {args} for message: {message.sender if hasattr(message, 'sender') else 'Unknown'}")

    if not args:
        if hasattr(message, 'reply'): await message.reply("Please provide a Twitter (X) status URL after the command.")
        return

    tweet_url = args[0]
    # Basic regex for Twitter status URL
    # e.g., https://twitter.com/username/status/1234567890123456789
    # or https://x.com/username/status/1234567890123456789
    if not re.match(r"https://(twitter\.com|x\.com)/[\w.-]+/status/\d+", tweet_url):
        if hasattr(message, 'reply'): await message.reply("Invalid Twitter (X) status URL provided.")
        return

    output_dir = "downloads/twitter"
    os.makedirs(output_dir, exist_ok=True)

    ydl_opts = {
        'outtmpl': os.path.join(output_dir, '%(uploader)s - %(id)s.%(ext)s'), # Twitter titles can be long/problematic
        'noplaylist': True,
        'quiet': True,
        'merge_output_format': 'mp4',
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        # Twitter might require login (cookies) for some content or to avoid rate limits.
        # 'cookiefile': 'path/to/twitter_cookies.txt', # Example
        # 'progress_hooks': [lambda d: print(d)],
    }

    try:
        if hasattr(message, 'reply'): await message.reply("📥 Downloading Twitter video, please wait...")
        print(f"Attempting to download Twitter video from: {tweet_url}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(tweet_url, download=True)
            # For Twitter, 'title' might be the full tweet text.
            # 'uploader' is the Twitter username, 'id' is the tweet ID.
            tweet_text = info_dict.get('title', 'Twitter Video')
            uploader = info_dict.get('uploader', 'Twitter User')
            tweet_id = info_dict.get('id', '')

            # Filename based on uploader and tweet ID is more stable
            # Sanitize uploader for filename
            sanitized_uploader = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in uploader)[:30]

            downloaded_file_path = None
            # Expected pattern: uploader - id.mp4
            expected_filename_part = f"{sanitized_uploader} - {tweet_id}"

            for f_name in os.listdir(output_dir):
                if expected_filename_part in f_name and (f_name.endswith(".mp4") or f_name.endswith(".mkv")):
                    downloaded_file_path = os.path.join(output_dir, f_name)
                    break

            if not downloaded_file_path: # Fallback
                files_in_dir = [os.path.join(output_dir, f) for f in os.listdir(output_dir) if (f.endswith(".mp4") or f.endswith(".mkv"))]
                if files_in_dir:
                    files_in_dir.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                    downloaded_file_path = files_in_dir[0]

            if downloaded_file_path and os.path.exists(downloaded_file_path):
                file_size = os.path.getsize(downloaded_file_path)
                final_caption = f"🐦 X/Twitter video by @{uploader}:\n{tweet_text[:100]}"
                print(f"Successfully downloaded Twitter video: {downloaded_file_path}, Size: {file_size} bytes")
                target_chat_id = getattr(message, 'chat_id', getattr(message, 'sender_id', 'unknown_chat'))

                sent_message_info = await client.send_video(
                    chat_id=target_chat_id,
                    video_data_or_path=downloaded_file_path,
                    caption=final_caption
                )
                bot_instance.logger.info(f"twitter: Sent video file {os.path.basename(downloaded_file_path)}, msg ID: {sent_message_info.get('id') if sent_message_info else 'N/A'}")

                # os.remove(downloaded_file_path) # Optional cleanup
            else:
                print(f"Error: Twitter video file not found after download attempt for URL {tweet_url}.")
                if hasattr(message, 'reply'): await message.reply("⚠️ Error: Could not locate the video file after download. The tweet might not contain a video or it's inaccessible.")

    except yt_dlp.utils.DownloadError as e:
        print(f"yt-dlp DownloadError for Twitter: {e}")
        error_message = "⚠️ Error downloading Twitter video. It might be from a private account, deleted, or require login (cookies)."
        if "is protected" in str(e).lower() or "private" in str(e).lower():
             error_message = "⚠️ This tweet is from a protected/private account and cannot be downloaded without authentication."
        elif "Status is a duplicate" in str(e) or "Could not find tweet" in str(e): # Example errors
            error_message = "⚠️ Could not find the tweet or it's a duplicate/invalid link."
        if hasattr(message, 'reply'): await message.reply(error_message)
    except Exception as e:
        print(f"An unexpected error occurred in twitter command: {e}")
        if hasattr(message, 'reply'): await message.reply(f"⚠️ An unexpected error occurred: {str(e)[:100]}")
    finally:
        pass

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

    class MockBotInstance:
        def __init__(self):
            self.message_templates = None

    async def main_test():
        mock_bot = MockBotInstance()
        mock_client = MockClient()

        # Use a known public Twitter/X video URL for testing.
        # These can also change. Find a public video tweet.
        # Example: (replace with a current, simple, public Twitter video URL)
        # valid_twitter_url = "https://twitter.com/SpaceX/status/1547693 SpaceX/status/1547693150749245441" # Example from SpaceX
        # valid_twitter_url = "https://twitter.com/NASA/status/1701603353000943894" # Example from NASA
        valid_twitter_url = "https://x.com/GoogleDeepMind/status/1798722460236001440" # Google DeepMind video tweet

        print("\n--- Twitter Test Case 1: Valid Twitter Video URL ---")
        if valid_twitter_url:
            mock_msg_valid = MockMessage(f"/twitter {valid_twitter_url}", "TestUserTwitter_1")
            await handle_twitter(mock_msg_valid, [valid_twitter_url], mock_client, mock_bot)
        else:
            print("Skipping Test Case 1: No valid_twitter_url provided for testing.")

        print("\n--- Twitter Test Case 2: Invalid URL (not Twitter/X) ---")
        invalid_url = "https://example.com/not_twitter"
        mock_msg_invalid = MockMessage(f"/twitter {invalid_url}", "TestUserTwitter_2")
        await handle_twitter(mock_msg_invalid, [invalid_url], mock_client, mock_bot)

        print("\n--- Twitter Test Case 3: No URL ---")
        mock_msg_no_url = MockMessage("/twitter", "TestUserTwitter_3")
        await handle_twitter(mock_msg_no_url, [], mock_client, mock_bot)

        print("\n--- Twitter Test Case 4: Tweet without video ---")
        # URL of a tweet that does not contain a video
        no_video_tweet_url = "https://x.com/elonmusk/status/1798895165098643613" # Example text tweet
        mock_msg_no_video = MockMessage(f"/twitter {no_video_tweet_url}", "TestUserTwitter_4")
        await handle_twitter(mock_msg_no_video, [no_video_tweet_url], mock_client, mock_bot)


    # Twitter/X downloads can be affected by API changes or login requirements.
    # yt-dlp usually keeps up but may require cookies for full access or to avoid rate limits.
    asyncio.run(main_test())
