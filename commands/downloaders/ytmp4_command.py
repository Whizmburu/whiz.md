# commands/downloaders/ytmp4_command.py
import yt_dlp
import os
import asyncio

async def handle_ytmp4(message, args, client, bot_instance):
    """
    Handles the /ytmp4 command (YouTube to MP4).
    Downloads video from a YouTube video URL as an MP4 file.
    """
    command_name = "ytmp4"
    print(f"Executing /{command_name} with args: {args} for message: {message.sender if hasattr(message, 'sender') else 'Unknown'}")

    if not args:
        if hasattr(message, 'reply'): await message.reply("Please provide a YouTube video URL after the command.")
        return

    video_url = args[0]
    if not ("youtube.com/" in video_url or "youtu.be/" in video_url):
        if hasattr(message, 'reply'): await message.reply("Invalid YouTube URL provided. Please make sure it's a valid YouTube link.")
        return

    output_dir = "downloads/video"
    os.makedirs(output_dir, exist_ok=True)

    # yt-dlp options for MP4 download
    # Prefer MP4 format directly if available, otherwise download best and convert.
    # 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best' is a common format string.
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': True,
        'merge_output_format': 'mp4', # Ensure output is mp4 if merging is needed
        # 'progress_hooks': [lambda d: print(d)], # For debugging
    }

    try:
        if hasattr(message, 'reply'): await message.reply("📥 Downloading video, please wait... This might take a while depending on video size.")
        print(f"Attempting to download video from: {video_url}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            video_title = info_dict.get('title', 'video')

            # Sanitize title for filename
            sanitized_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in video_title)
            max_title_len = 50
            sanitized_title = sanitized_title[:max_title_len]

            downloaded_file_path = None
            # yt-dlp might save the file with an extension like .mkv then remux to .mp4,
            # or directly as .mp4. The final extension should be .mp4 with merge_output_format.
            # We search for .mp4 files in the output directory.
            for f_name in os.listdir(output_dir):
                if f_name.endswith(".mp4") and sanitized_title in f_name:
                    downloaded_file_path = os.path.join(output_dir, f_name)
                    break

            if not downloaded_file_path: # Fallback if title matching fails
                 for f_name in os.listdir(output_dir):
                    if f_name.endswith(".mp4"):
                        downloaded_file_path = os.path.join(output_dir, f_name)
                        break

            if downloaded_file_path and os.path.exists(downloaded_file_path):
                file_size = os.path.getsize(downloaded_file_path)
                print(f"Successfully downloaded video: {downloaded_file_path}, Size: {file_size} bytes")

                if hasattr(message, 'reply') and hasattr(client, 'send_file_simulation'):
                    await client.send_file_simulation(
                        chat_id=message.sender,
                        filepath=downloaded_file_path,
                        caption=f"🎬 Here's your MP4: {video_title}"
                    )
                elif hasattr(message, 'reply'):
                    await message.reply(f"✅ Successfully downloaded: {video_title}.mp4 (Path: {downloaded_file_path})")

                # Optional: Clean up
                # os.remove(downloaded_file_path)
            else:
                print("Error: MP4 file not found after download process.")
                if hasattr(message, 'reply'): await message.reply("⚠️ Error: Could not locate the MP4 file after download.")

    except yt_dlp.utils.DownloadError as e:
        print(f"yt-dlp DownloadError for ytmp4: {e}")
        error_message = "⚠️ Error downloading video. It might be age-restricted, private, or an invalid URL."
        if "is age restricted" in str(e).lower(): error_message = "⚠️ This video is age-restricted."
        elif "private video" in str(e).lower(): error_message = "⚠️ This video is private."
        elif "video unavailable" in str(e).lower(): error_message = "⚠️ This video is unavailable."
        if hasattr(message, 'reply'): await message.reply(error_message)
    except Exception as e:
        print(f"An unexpected error occurred in ytmp4: {e}")
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
            # if os.path.exists(filepath): os.remove(filepath) # Clean up test file

    class MockBotInstance:
        def __init__(self):
            self.message_templates = None

    async def main_test():
        mock_bot = MockBotInstance()
        mock_client = MockClient()

        print("\n--- ytmp4 Test Case 1: Valid YouTube URL (short video) ---")
        # Use a very short public domain video to avoid long download times
        # Example: "https://www.youtube.com/watch?v= короткое видео " (replace with actual short video)
        # Using a known short public domain video: "https://www.youtube.com/watch?v=UZBiSUkn2yQ" (Big Buck Bunny ~1min trailer)
        # Or even shorter: "https://www.youtube.com/watch?v=Zc2g_4c4w2E" (Jellyfish ~30s)
        valid_url_short = "https://www.youtube.com/watch?v=Zc2g_4c4w2E"
        mock_msg_valid = MockMessage(f"/ytmp4 {valid_url_short}", "TestUserMP4_1")
        await handle_ytmp4(mock_msg_valid, [valid_url_short], mock_client, mock_bot)

        print("\n--- ytmp4 Test Case 2: Invalid URL ---")
        invalid_url = "https://example.com/not_youtube"
        mock_msg_invalid = MockMessage(f"/ytmp4 {invalid_url}", "TestUserMP4_2")
        await handle_ytmp4(mock_msg_invalid, [invalid_url], mock_client, mock_bot)

        print("\n--- ytmp4 Test Case 3: No URL ---")
        mock_msg_no_url = MockMessage("/ytmp4", "TestUserMP4_3")
        await handle_ytmp4(mock_msg_no_url, [], mock_client, mock_bot)

    asyncio.run(main_test())
