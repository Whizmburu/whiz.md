# commands/downloaders/mediafire_command.py
import yt_dlp
import os
import asyncio
import re

async def handle_mediafire(message, args, client, bot_instance):
    """
    Handles the /mediafire command.
    Attempts to download a file from a MediaFire link using yt-dlp.
    """
    command_name = "mediafire"
    print(f"Executing /{command_name} with args: {args} for message: {message.sender if hasattr(message, 'sender') else 'Unknown'}")

    if not args:
        if hasattr(message, 'reply'): await message.reply("Please provide a MediaFire file URL after the command.")
        return

    file_url = args[0]
    # Basic regex for MediaFire file URL
    # e.g., https://www.mediafire.com/file/yourfileid/filename.ext/file
    if not re.match(r"https://(www\.)?mediafire\.com/file/[\w.-]+", file_url):
        if hasattr(message, 'reply'): await message.reply("Invalid MediaFire URL provided.")
        return

    output_dir = "downloads/mediafire"
    os.makedirs(output_dir, exist_ok=True)

    # yt-dlp options for MediaFire
    # For MediaFire, outtmpl might just use %(title)s.%(ext)s or directly %(filename)s if available
    ydl_opts = {
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'), # yt-dlp will attempt to get a title
        # 'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'), # Or use ID
        'quiet': True,
        # No specific format conversion needed, download as is.
        # 'progress_hooks': [lambda d: print(d)],
    }

    try:
        if hasattr(message, 'reply'): await message.reply("📥 Downloading from MediaFire, please wait...")
        print(f"Attempting to download MediaFire file from: {file_url}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(file_url, download=True)
            # 'title' from info_dict is usually the filename from MediaFire
            file_title = info_dict.get('title', 'mediafire_file')
            file_ext = info_dict.get('ext', '') # Extension determined by yt-dlp

            # Construct expected filename part for searching
            sanitized_title = "".join(c if c.isalnum() or c in (' ', '-', '_', '.') else '_' for c in file_title)
            # Mediafire titles can be long or have original extensions.
            # Max length for the part of the title we search for:
            max_len = 60
            sanitized_title_part = sanitized_title[:max_len]
            if file_ext and not sanitized_title_part.endswith(f".{file_ext}"):
                # If the title from ydl doesn't include extension, but ext is known
                pass # ext will be used in the search below

            downloaded_file_path = None
            for f_name in os.listdir(output_dir):
                # Match based on title part and extension (if known)
                # yt-dlp's outtmpl is '%(title)s.%(ext)s'
                # So, f_name should be like "Actual File Name from MediaFire.actual_ext"
                if sanitized_title_part.lower() in f_name.lower():
                    if file_ext and f_name.lower().endswith(f".{file_ext.lower()}"):
                        downloaded_file_path = os.path.join(output_dir, f_name)
                        break
                    elif not file_ext: # If extension wasn't clear from info_dict, broader match
                        downloaded_file_path = os.path.join(output_dir, f_name)
                        break

            if not downloaded_file_path: # Fallback: get the newest file in directory
                files_in_dir = [os.path.join(output_dir, f) for f in os.listdir(output_dir)]
                if files_in_dir:
                    files_in_dir.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                    downloaded_file_path = files_in_dir[0]


            if downloaded_file_path and os.path.exists(downloaded_file_path):
                file_size = os.path.getsize(downloaded_file_path)
                final_caption = f"📄 MediaFire Download: {os.path.basename(downloaded_file_path)}"
                print(f"Successfully downloaded MediaFire file: {downloaded_file_path}, Size: {file_size} bytes")

                if hasattr(message, 'reply') and hasattr(client, 'send_file_simulation'):
                    await client.send_file_simulation(
                        chat_id=message.sender,
                        filepath=downloaded_file_path,
                        caption=final_caption
                    )
                elif hasattr(message, 'reply'):
                    await message.reply(f"✅ Successfully downloaded: {os.path.basename(downloaded_file_path)}")

                # os.remove(downloaded_file_path) # Optional cleanup
            else:
                print(f"Error: MediaFire file not found after download attempt for URL {file_url}.")
                if hasattr(message, 'reply'): await message.reply("⚠️ Error: Could not locate the file after download. The link might be broken, password-protected, or a problem with the extractor.")

    except yt_dlp.utils.DownloadError as e:
        print(f"yt-dlp DownloadError for MediaFire: {e}")
        error_message = "⚠️ Error downloading from MediaFire. The link may be invalid, password-protected, or the file deleted."
        if "File is password protected" in str(e):
            error_message = "🔒 This MediaFire file is password protected."
        elif "File does not exist" in str(e) or "Invalid URL" in str(e):
            error_message = "🚫 The MediaFire link is invalid or the file does not exist."
        if hasattr(message, 'reply'): await message.reply(error_message)
    except Exception as e:
        print(f"An unexpected error occurred in mediafire command: {e}")
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

        # Use a known public and working MediaFire file URL for testing.
        # These are hard to find reliably. This is a placeholder.
        # Create a small dummy file and upload to MediaFire for a stable test link.
        # Example: (replace with a real, small, public MediaFire file URL)
        # valid_mediafire_url = "https://www.mediafire.com/file/xxxxxxxxxxxxxxx/test_file.txt/file"
        # For this test, I will use a known yt-dlp test link for MediaFire if available,
        # otherwise, this test might not run correctly without a live link.
        # yt-dlp test suite has some, but they might change.
        # This is a sample link that has been used in some yt-dlp test cases in the past:
        # (It may or may not be active)
        valid_mediafire_url = "http://www.mediafire.com/download/155y72b4s0cqbqs/youtube-dl-test-video.flv"
        # Another example found in public discussions (check if active):
        # valid_mediafire_url = "https://www.mediafire.com/file/g669j8seg0702c5/Sample.txt/file"


        print("\n--- MediaFire Test Case 1: Valid MediaFire File URL ---")
        if "mediafire.com/file/" in valid_mediafire_url or "mediafire.com/download/" in valid_mediafire_url : # Basic check if a real URL is set
            mock_msg_valid = MockMessage(f"/mediafire {valid_mediafire_url}", "TestUserMediaFire_1")
            await handle_mediafire(mock_msg_valid, [valid_mediafire_url], mock_client, mock_bot)
        else:
            print(f"Skipping Test Case 1: Update 'valid_mediafire_url' with a live MediaFire link for testing. Current: {valid_mediafire_url}")


        print("\n--- MediaFire Test Case 2: Invalid URL (not MediaFire) ---")
        invalid_url = "https://example.com/not_mediafire"
        mock_msg_invalid = MockMessage(f"/mediafire {invalid_url}", "TestUserMediaFire_2")
        await handle_mediafire(mock_msg_invalid, [invalid_url], mock_client, mock_bot)

        print("\n--- MediaFire Test Case 3: No URL ---")
        mock_msg_no_url = MockMessage("/mediafire", "TestUserMediaFire_3")
        await handle_mediafire(mock_msg_no_url, [], mock_client, mock_bot)

        print("\n--- MediaFire Test Case 4: Likely broken/fake MediaFire URL ---")
        broken_mediafire_url = "https://www.mediafire.com/file/th1s1sbr0k3n/fake.zip/file"
        mock_msg_broken = MockMessage(f"/mediafire {broken_mediafire_url}", "TestUserMediaFire_4")
        await handle_mediafire(mock_msg_broken, [broken_mediafire_url], mock_client, mock_bot)


    # MediaFire links can be volatile. For robust testing, use a self-uploaded, small, public file.
    asyncio.run(main_test())
