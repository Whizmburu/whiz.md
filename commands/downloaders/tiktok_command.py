# commands/downloaders/tiktok_command.py
import yt_dlp
import os
import asyncio
import re

async def handle_tiktok(message, args, client, bot_instance):
    """
    Handles the /tiktok command.
    Attempts to download video from a TikTok URL using yt-dlp.
    """
    command_name = "tiktok"
    print(f"Executing /{command_name} with args: {args} for message: {message.sender if hasattr(message, 'sender') else 'Unknown'}")

    if not args:
        if hasattr(message, 'reply'): await message.reply("Please provide a TikTok video URL after the command.")
        return

    video_url = args[0]
    # Basic regex for TikTok video URL
    # e.g. https://www.tiktok.com/@username/video/1234567890123456789
    # or https://vm.tiktok.com/SHORTCODE/
    if not (re.match(r"https://(www\.)?tiktok\.com/@[\w.-]+/video/\d+", video_url) or \
            re.match(r"https://vm\.tiktok\.com/[\w-]+/?", video_url)):
        if hasattr(message, 'reply'): await message.reply("Invalid TikTok URL provided.")
        return

    output_dir = "downloads/tiktok"
    os.makedirs(output_dir, exist_ok=True)

    # yt-dlp options for TikTok
    ydl_opts = {
        'outtmpl': os.path.join(output_dir, '%(title)s - %(uploader)s.%(ext)s'),
        'noplaylist': True,
        'quiet': True,
        'merge_output_format': 'mp4', # Prefer mp4
        # 'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', # Similar to ytmp4
         'format': 'best', # yt-dlp often handles tiktok best with simpler format string
        # 'progress_hooks': [lambda d: print(d)],
    }

    try:
        if hasattr(message, 'reply'): await message.reply("📥 Downloading TikTok video, please wait...")
        print(f"Attempting to download TikTok video from: {video_url}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            video_title = info_dict.get('title', 'tiktok_video')
            uploader = info_dict.get('uploader', '') # TikTok username

            # Sanitize title and uploader for filename
            sanitized_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in video_title)
            sanitized_uploader = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in uploader)
            max_len = 30
            sanitized_title = sanitized_title[:max_len]
            sanitized_uploader = sanitized_uploader[:max_len]

            # Try to find the downloaded file. yt-dlp's naming can be complex.
            # The outtmpl is '%(title)s - %(uploader)s.%(ext)s'.
            downloaded_file_path = None
            for f_name in os.listdir(output_dir):
                # A bit lenient matching as titles/uploaders can have many special chars
                if sanitized_title.lower() in f_name.lower() and (f_name.endswith(".mp4") or f_name.endswith(".mkv") or f_name.endswith(".webm")):
                    downloaded_file_path = os.path.join(output_dir, f_name)
                    break

            if not downloaded_file_path: # Fallback: get the newest mp4/video file in directory
                 # Sort files by modification time, newest first
                files_in_dir = [os.path.join(output_dir, f) for f in os.listdir(output_dir) if (f.endswith(".mp4") or f.endswith(".mkv") or f.endswith(".webm"))]
                if files_in_dir:
                    files_in_dir.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                    downloaded_file_path = files_in_dir[0]


            if downloaded_file_path and os.path.exists(downloaded_file_path):
                file_size = os.path.getsize(downloaded_file_path)
                final_caption = f"🎬 TikTok by {uploader}: {video_title[:50]}"
                print(f"Successfully downloaded TikTok video: {downloaded_file_path}, Size: {file_size} bytes")
                target_chat_id = getattr(message, 'chat_id', getattr(message, 'sender_id', 'unknown_chat'))

                sent_message_info = await client.send_video(
                    chat_id=target_chat_id,
                    video_data_or_path=downloaded_file_path,
                    caption=final_caption
                )
                bot_instance.logger.info(f"tiktok: Sent video file {os.path.basename(downloaded_file_path)}, msg ID: {sent_message_info.get('id') if sent_message_info else 'N/A'}")

                # Optional: Clean up
                # os.remove(downloaded_file_path)
            else:
                print(f"Error: TikTok video file not found after download attempt for URL {video_url}.")
                if hasattr(message, 'reply'): await message.reply("⚠️ Error: Could not locate the video file after download.")

    except yt_dlp.utils.DownloadError as e:
        print(f"yt-dlp DownloadError for TikTok: {e}")
        error_message = "⚠️ Error downloading TikTok video. It might be private, deleted, or region-locked."
        if "Video unavailable" in str(e): error_message = "⚠️ This TikTok video is unavailable."
        if hasattr(message, 'reply'): await message.reply(error_message)
    except Exception as e:
        print(f"An unexpected error occurred in tiktok command: {e}")
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

        # Use a known public and working TikTok video URL for testing.
        # These URLs can become invalid quickly.
        # Example: (replace with a current, simple, public TikTok video URL)
        # valid_tiktok_url = "https://www.tiktok.com/@tiktok/video/7065033851200408834" # Example from official tiktok
        valid_tiktok_url = "https://www.tiktok.com/@google/video/7310998269460139307" # Example from Google's TikTok

        print("\n--- TikTok Test Case 1: Valid TikTok URL ---")
        if valid_tiktok_url:
            mock_msg_valid = MockMessage(f"/tiktok {valid_tiktok_url}", "TestUserTikTok_1")
            await handle_tiktok(mock_msg_valid, [valid_tiktok_url], mock_client, mock_bot)
        else:
            print("Skipping Test Case 1: No valid_tiktok_url provided for testing.")

        print("\n--- TikTok Test Case 2: Invalid URL (not TikTok) ---")
        invalid_url = "https://example.com/not_tiktok"
        mock_msg_invalid = MockMessage(f"/tiktok {invalid_url}", "TestUserTikTok_2")
        await handle_tiktok(mock_msg_invalid, [invalid_url], mock_client, mock_bot)

        print("\n--- TikTok Test Case 3: No URL ---")
        mock_msg_no_url = MockMessage("/tiktok", "TestUserTikTok_3")
        await handle_tiktok(mock_msg_no_url, [], mock_client, mock_bot)

        # Test with a short vm.tiktok.com URL if one is available
        # short_tiktok_url = "https://vm.tiktok.com/ZMabcdefg/" # Replace with a real short URL
        # print("\n--- TikTok Test Case 4: Short TikTok URL ---")
        # if short_tiktok_url and "ZMabcdefg" not in short_tiktok_url : # Ensure it's not the placeholder
        #     mock_msg_short = MockMessage(f"/tiktok {short_tiktok_url}", "TestUserTikTok_4")
        #     await handle_tiktok(mock_msg_short, [short_tiktok_url], mock_client, mock_bot)
        # else:
        #     print("Skipping Test Case 4: No short_tiktok_url provided for testing.")


    # TikTok downloads can be flaky due to frequent site changes.
    # yt-dlp is generally good but might break for TikTok from time to time.
    asyncio.run(main_test())
