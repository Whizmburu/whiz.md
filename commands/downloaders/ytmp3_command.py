# commands/downloaders/ytmp3_command.py
import yt_dlp
import os
import asyncio # Required for async functions

async def handle_ytmp3(message, args, client, bot_instance):
    """
    Handles the /ytmp3 command (YouTube to MP3).
    Downloads audio from a YouTube video URL and provides it as an MP3 file.
    """
    command_name = "ytmp3"
    print(f"Executing /{command_name} with args: {args} for message: {message.sender if hasattr(message, 'sender') else 'Unknown'}")

    if not args:
        # await message.reply("Please provide a YouTube video URL.")
        print("User did not provide a URL for ytmp3.")
        # Simulate reply for now if message object is mock
        if hasattr(message, 'reply'): await message.reply("Please provide a YouTube video URL after the command.")
        return

    video_url = args[0]
    # A simple check for youtube.com or youtu.be in the URL
    if not ("youtube.com/" in video_url or "youtu.be/" in video_url):
        # await message.reply("Invalid YouTube URL provided.")
        print(f"Invalid YouTube URL: {video_url}")
        if hasattr(message, 'reply'): await message.reply("Invalid YouTube URL provided. Please make sure it's a valid YouTube link.")
        return

    # Define output directory for downloads
    # It's good practice to make this configurable or use a temp directory
    output_dir = "downloads/audio"
    os.makedirs(output_dir, exist_ok=True)

    # yt-dlp options
    # The %(title)s.%(ext)s template ensures the filename is based on the video title.
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192', # Standard quality
        }],
        'noplaylist': True, # Download only the single video, not playlist
        'quiet': True, # Suppress yt-dlp console output
        # 'progress_hooks': [lambda d: print(d)], # For debugging progress
    }

    try:
        # await message.reply("📥 Downloading and converting to MP3, please wait...")
        print(f"Attempting to download audio from: {video_url}")
        if hasattr(message, 'reply'): await message.reply("📥 Downloading and converting to MP3, please wait...")


        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            video_title = info_dict.get('title', 'audio')
            # yt-dlp handles the conversion and naming, the outtmpl gives us the path pattern
            # We need to find the actual resulting .mp3 file.
            # After download and postprocessing, the extension should be .mp3
            # We can construct the expected filename or search for it.

            # Construct expected filename based on title and .mp3 extension
            # Sanitize title for filename
            sanitized_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in video_title)
            # Limit title length to avoid overly long filenames
            max_title_len = 50
            sanitized_title = sanitized_title[:max_title_len]

            # yt-dlp's outtmpl will create a file like 'Video Title.mp3'
            # The exact filename after processing might be tricky if title has special chars.
            # A more robust way is to use a fixed name or get it from `info_dict` if available
            # For now, let's assume yt-dlp creates a .mp3 file based on the title in output_dir

            # Let's try to find the downloaded file. yt-dlp replaces the original extension.
            # The 'outtmpl' with '%(ext)s' might initially be .webm or .m4a before conversion.
            # After FFmpegExtractAudio, it becomes .mp3.
            # The `info_dict` usually contains `requested_downloads` or similar
            # For simplicity, let's assume the output file is based on title in the output_dir
            # and has .mp3 extension.

            # Expected filename after conversion.
            # yt-dlp will place it in output_dir.
            # Example: 'downloads/audio/My Video Title.mp3'
            # Need to be careful with special characters in title.

            # The `ydl.prepare_filename(info_dict)` can give the filename *before* postprocessing.
            # After postprocessing, the extension changes.
            # A common strategy is to download with a fixed name if possible, or list dir.

            # For now, let's assume the file path can be derived or is known.
            # If `outtmpl` was `os.path.join(output_dir, 'downloaded_audio.%(ext)s')`,
            # then the final file would be `os.path.join(output_dir, 'downloaded_audio.mp3')`.
            # Let's refine ydl_opts for a predictable output filename.

            # Simplified: find the first .mp3 file in the directory (if only one download at a time)
            # This is not robust for concurrent downloads.
            downloaded_file_path = None
            for f in os.listdir(output_dir):
                if f.endswith(".mp3") and sanitized_title in f: # Check if title is part of filename
                    downloaded_file_path = os.path.join(output_dir, f)
                    break

            if not downloaded_file_path:
                 # Fallback if title matching is difficult due to sanitization/special chars
                for f in os.listdir(output_dir):
                    if f.endswith(".mp3"): # Get the latest mp3
                        # To get latest, sort by creation/modification time if multiple mp3s
                        # For simplicity, taking the first one found for now
                        downloaded_file_path = os.path.join(output_dir, f)
                        break


            if downloaded_file_path and os.path.exists(downloaded_file_path):
                file_size = os.path.getsize(downloaded_file_path)
                print(f"Successfully downloaded and converted to MP3: {downloaded_file_path}, Size: {file_size} bytes")
                # await client.send_file(message.chat_id, downloaded_file_path, caption=f"🎶 {video_title}")
                # Placeholder for sending file:
                if hasattr(message, 'reply') and hasattr(client, 'send_file_simulation'):
                    await client.send_file_simulation(
                        chat_id=message.sender, # Assuming message.sender can be a chat_id
                        filepath=downloaded_file_path,
                        caption=f"🎶 Here's your MP3: {video_title}"
                    )
                elif hasattr(message, 'reply'):
                    await message.reply(f"✅ Successfully downloaded: {video_title}.mp3 (Path: {downloaded_file_path})")

                # Optional: Clean up the downloaded file after sending
                # os.remove(downloaded_file_path)
                # print(f"Cleaned up {downloaded_file_path}")
            else:
                print("Error: MP3 file not found after download process.")
                if hasattr(message, 'reply'): await message.reply("⚠️ Error: Could not locate the MP3 file after download.")

    except yt_dlp.utils.DownloadError as e:
        print(f"yt-dlp DownloadError: {e}")
        error_message = "⚠️ Error downloading video. It might be age-restricted, private, or an invalid URL."
        # More specific error parsing could be done here from e
        if "is age restricted" in str(e).lower():
            error_message = "⚠️ This video is age-restricted and cannot be downloaded directly."
        elif "private video" in str(e).lower():
            error_message = "⚠️ This video is private and cannot be downloaded."
        elif "video unavailable" in str(e).lower():
            error_message = "⚠️ This video is unavailable."

        if hasattr(message, 'reply'): await message.reply(error_message)
    except Exception as e:
        print(f"An unexpected error occurred in ytmp3: {e}")
        # await message.reply("⚠️ An unexpected error occurred. Please try again later.")
        if hasattr(message, 'reply'): await message.reply(f"⚠️ An unexpected error occurred: {str(e)[:100]}") # Show part of error for debug
    finally:
        # Any cleanup that should always happen
        pass

# Example usage (for testing purposes, normally called by the bot's command dispatcher)
if __name__ == '__main__':
    class MockMessage:
        def __init__(self, text, sender):
            self.text = text
            self.sender = sender # Used as chat_id for simulation
        async def reply(self, text_content): # Made async
            print(f"BOT REPLIED TO {self.sender}: {text_content}")

    class MockClient:
        async def send_file_simulation(self, chat_id, filepath, caption): # Made async
            print(f"BOT SENDING FILE TO {chat_id}: {filepath}, Caption: {caption}")
            # Simulate file cleanup after sending for test
            if os.path.exists(filepath):
                 print(f"Test: Would delete {filepath} here if not needed for other tests.")
                 # os.remove(filepath)

    class MockBotInstance:
        def __init__(self):
            self.message_templates = None # Not used in this specific command directly for replies

    # Test cases
    async def main_test(): # Made async
        mock_bot = MockBotInstance()
        mock_client = MockClient()

        # Test 1: Valid YouTube URL
        print("\n--- Test Case 1: Valid YouTube URL ---")
        # Using a short, copyright-free music video for testing
        # Make sure this link is valid and public
        # Example: "https://www.youtube.com/watch?v=dQw4w9WgXcQ" (Rick Astley - too common, might be blocked by networks)
        # Using a known short public domain music video: "https://www.youtube.com/watch?v=N_GS3fDMBG4" (Audio Library)
        valid_url = "https://www.youtube.com/watch?v=N_GS3fDMBG4" # Example: Royalty Free Music
        # valid_url = "https://www.youtube.com/watch?v=LXb3EKWsInQ" # Another short one
        mock_msg_valid = MockMessage(f"/ytmp3 {valid_url}", "TestUser1")
        await handle_ytmp3(mock_msg_valid, [valid_url], mock_client, mock_bot)

        # Test 2: Invalid URL (not YouTube)
        print("\n--- Test Case 2: Invalid URL (not YouTube) ---")
        invalid_url_format = "https://example.com/video.mp4"
        mock_msg_invalid_format = MockMessage(f"/ytmp3 {invalid_url_format}", "TestUser2")
        await handle_ytmp3(mock_msg_invalid_format, [invalid_url_format], mock_client, mock_bot)

        # Test 3: No URL
        print("\n--- Test Case 3: No URL provided ---")
        mock_msg_no_url = MockMessage("/ytmp3", "TestUser3")
        await handle_ytmp3(mock_msg_no_url, [], mock_client, mock_bot)

        # Test 4: Potentially problematic URL (e.g., private or non-existent)
        # This is harder to make a consistent test case for without a known private URL
        print("\n--- Test Case 4: Non-existent video URL ---")
        non_existent_url = "https://www.youtube.com/watch?v=th1sIsFake"
        mock_msg_non_existent = MockMessage(f"/ytmp3 {non_existent_url}", "TestUser4")
        await handle_ytmp3(mock_msg_non_existent, [non_existent_url], mock_client, mock_bot)

    asyncio.run(main_test())
