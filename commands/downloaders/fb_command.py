# commands/downloaders/fb_command.py
import yt_dlp
import os
import asyncio
import re

async def handle_fb(message, args, client, bot_instance):
    """
    Handles the /fb command (Facebook Downloader).
    Attempts to download video from a Facebook URL using yt-dlp.
    Note: May require login for private videos. This implementation attempts anonymous download.
    """
    command_name = "fb"
    print(f"Executing /{command_name} with args: {args} for message: {message.sender if hasattr(message, 'sender') else 'Unknown'}")

    if not args:
        if hasattr(message, 'reply'): await message.reply("Please provide a Facebook video URL after the command.")
        return

    video_url = args[0]
    # Basic regex for Facebook video URL
    # e.g., https://www.facebook.com/watch/?v=VIDEO_ID
    # or https://www.facebook.com/username/videos/VIDEO_ID/
    # or https://fb.watch/SHORTCODE/
    if not (re.match(r"https://(www\.|m\.)?facebook\.com/(watch|[\w.-]+/videos|[\w.-]+/posts)/?(\?v=)?\d+", video_url) or \
            re.match(r"https://fb\.watch/[\w-]+/?", video_url)):
        if hasattr(message, 'reply'): await message.reply("Invalid Facebook video URL provided.")
        return

    output_dir = "downloads/facebook"
    os.makedirs(output_dir, exist_ok=True)

    ydl_opts = {
        'outtmpl': os.path.join(output_dir, '%(title)s - %(uploader)s.%(ext)s'),
        'noplaylist': True, # Usually not relevant for single FB videos but good practice
        'quiet': True,
        'merge_output_format': 'mp4',
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        # yt-dlp might require cookies for some Facebook videos, even public ones.
        # 'cookiefile': 'path/to/facebook_cookies.txt', # Example if cookies are needed
        # 'progress_hooks': [lambda d: print(d)],
    }

    try:
        if hasattr(message, 'reply'): await message.reply("📥 Downloading Facebook video, please wait...")
        print(f"Attempting to download Facebook video from: {video_url}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            video_title = info_dict.get('title', 'facebook_video')
            uploader = info_dict.get('uploader', 'Facebook User') # Uploader info might be less consistent

            sanitized_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in video_title)[:50]
            sanitized_uploader = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in uploader)[:30]

            downloaded_file_path = None
            for f_name in os.listdir(output_dir):
                if sanitized_title.lower() in f_name.lower() and (f_name.endswith(".mp4") or f_name.endswith(".mkv")):
                    downloaded_file_path = os.path.join(output_dir, f_name)
                    break

            if not downloaded_file_path: # Fallback
                files_in_dir = [os.path.join(output_dir, f) for f in os.listdir(output_dir) if (f.endswith(".mp4") or f.endswith(".mkv"))]
                if files_in_dir:
                    files_in_dir.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                    downloaded_file_path = files_in_dir[0]


            if downloaded_file_path and os.path.exists(downloaded_file_path):
                file_size = os.path.getsize(downloaded_file_path)
                final_caption = f"🎬 FB Video by {uploader}: {video_title[:50]}"
                print(f"Successfully downloaded Facebook video: {downloaded_file_path}, Size: {file_size} bytes")
                target_chat_id = getattr(message, 'chat_id', getattr(message, 'sender_id', 'unknown_chat'))

                sent_message_info = await client.send_video(
                    chat_id=target_chat_id,
                    video_data_or_path=downloaded_file_path,
                    caption=final_caption
                )
                bot_instance.logger.info(f"fb: Sent video file {os.path.basename(downloaded_file_path)}, msg ID: {sent_message_info.get('id') if sent_message_info else 'N/A'}")

                # os.remove(downloaded_file_path) # Optional cleanup
            else:
                print(f"Error: Facebook video file not found after download attempt for URL {video_url}.")
                if hasattr(message, 'reply'): await message.reply("⚠️ Error: Could not locate the video file after download. It might be private or a live stream not yet processed.")

    except yt_dlp.utils.DownloadError as e:
        print(f"yt-dlp DownloadError for Facebook: {e}")
        error_message = "⚠️ Error downloading Facebook video. It might be private, deleted, or require login (cookies)."
        if "Video is unavailable" in str(e): error_message = "⚠️ This Facebook video is unavailable or may have been deleted."
        elif "login required" in str(e).lower() or "cookies" in str(e).lower():
             error_message = "⚠️ This video may require login (cookies) to download, or it's private."
        if hasattr(message, 'reply'): await message.reply(error_message)
    except Exception as e:
        print(f"An unexpected error occurred in fb command: {e}")
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

        # Use a known public Facebook video URL for testing.
        # These URLs can change. Find a public video from a large page.
        # Example: (replace with a current, simple, public Facebook video URL)
        # valid_fb_url = "https://www.facebook.com/facebook/videos/10153231379946743/" # Old example
        # valid_fb_url = "https://www.facebook.com/MetaforDevelopers/videos/2 Developers/videos/294545590374479/" # Meta for Dev video
        # Let's try a short public one, e.g. from a news page or brand
        valid_fb_url = "https://www.facebook.com/watch?v=1203303820452321" # Example public video

        print("\n--- Facebook Test Case 1: Valid Facebook Video URL ---")
        if valid_fb_url:
            mock_msg_valid = MockMessage(f"/fb {valid_fb_url}", "TestUserFB_1")
            await handle_fb(mock_msg_valid, [valid_fb_url], mock_client, mock_bot)
        else:
            print("Skipping Test Case 1: No valid_fb_url provided for testing.")

        print("\n--- Facebook Test Case 2: Invalid URL (not Facebook) ---")
        invalid_url = "https://example.com/not_facebook"
        mock_msg_invalid = MockMessage(f"/fb {invalid_url}", "TestUserFB_2")
        await handle_fb(mock_msg_invalid, [invalid_url], mock_client, mock_bot)

        print("\n--- Facebook Test Case 3: No URL ---")
        mock_msg_no_url = MockMessage("/fb", "TestUserFB_3")
        await handle_fb(mock_msg_no_url, [], mock_client, mock_bot)

    # Facebook downloads with yt-dlp can sometimes be tricky due to login requirements
    # or changes in Facebook's layout. Using cookies can help for problematic videos.
    asyncio.run(main_test())
