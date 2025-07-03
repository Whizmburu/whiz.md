# commands/dev_tools/headers_command.py
import asyncio
import requests # For making HTTP requests

async def handle_headers(message, args, client, bot_instance):
    """
    Handles the /headers command.
    Fetches and displays HTTP headers for a given URL.
    Usage: /headers <URL>
    """
    command_name = "headers"
    print(f"Executing /{command_name} with args: {args} for message: {message.sender if hasattr(message, 'sender') else 'Unknown'}")

    if not args:
        if hasattr(message, 'reply'): await message.reply(f"Usage: /{command_name} <URL (e.g., https://example.com)>")
        return

    url_to_fetch = args[0]

    # Basic URL validation (must start with http:// or https://)
    if not (url_to_fetch.startswith("http://") or url_to_fetch.startswith("https://")):
        url_to_fetch = "http://" + url_to_fetch # Default to http if no scheme
        # A better approach might be to try https first, then http, or require scheme.
        # For now, defaulting to http if scheme is missing, but warning user.
        if hasattr(message, 'reply'): await message.reply(f"Scheme (http/https) missing, defaulting to http. For specific scheme, please include it (e.g. https://{args[0]})")


    reply_message = ""

    try:
        if hasattr(message, 'reply'): await message.reply(f"🔍 Fetching HTTP headers for {url_to_fetch}, please wait...")

        # Make a HEAD request to get headers without downloading the full content
        # Allow redirects as sites often redirect (e.g. http to https)
        response = requests.head(url_to_fetch, timeout=10, allow_redirects=True) # 10 second timeout

        # If HEAD fails or gives minimal info (some servers don't like HEAD), try GET
        # but only stream headers if possible.
        if not response.headers or response.status_code >= 400 :
             print(f"HEAD request failed or returned status {response.status_code}. Trying GET request for headers.")
             response = requests.get(url_to_fetch, timeout=10, allow_redirects=True, stream=True)
             response.close() # Close connection after getting headers if stream=True

        status_code = response.status_code
        final_url = response.url # URL after any redirects

        reply_message = f"📊 HTTP Headers for {final_url} (Status: {status_code}):\n"
        reply_message += "```\n"
        for key, value in response.headers.items():
            reply_message += f"{key}: {value}\n"
        reply_message += "```"

        if len(reply_message) > 1900: # Truncate if too long
            reply_message = reply_message[:1900] + "\n... (headers truncated)```"

    except requests.exceptions.Timeout:
        reply_message = f"⚠️ Timeout: The request to {url_to_fetch} timed out."
    except requests.exceptions.TooManyRedirects:
        reply_message = f"⚠️ Error: Too many redirects for {url_to_fetch}."
    except requests.exceptions.SSLError as e:
        reply_message = f"🔒 SSL Error for {url_to_fetch}: {e}. Try with http:// or check the certificate."
    except requests.exceptions.ConnectionError as e:
        reply_message = f"🔗 Connection Error for {url_to_fetch}: {e}. Check the URL or your network."
    except requests.exceptions.RequestException as e: # Catch other requests-related errors
        print(f"Error in headers command for {url_to_fetch}: {e}")
        reply_message = f"An error occurred while fetching headers: {e}"
    except Exception as e: # Catch any other unexpected errors
        print(f"Unexpected error in headers command for {url_to_fetch}: {e}")
        reply_message = f"An unexpected error occurred: {e}"


    if hasattr(message, 'reply'):
        await message.reply(reply_message)
    else:
        # Print without markdown for console testing if reply_message is the success one
        if "HTTP Headers for" in reply_message:
             print(reply_message.replace("```\n", "").replace("```", ""))
        else:
            print(reply_message)


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

        print("\n--- HTTP Headers Test Cases ---")

        print("\nTest 1: Valid URL (https://google.com)")
        msg1 = MockMessage("/headers https://google.com", "TestUserHeaders_1")
        await handle_headers(msg1, ["https://google.com"], mock_client, mock_bot)

        await asyncio.sleep(1) # Small delay

        print("\nTest 2: Valid URL without scheme (example.com)")
        msg2 = MockMessage("/headers example.com", "TestUserHeaders_2")
        await handle_headers(msg2, ["example.com"], mock_client, mock_bot)

        await asyncio.sleep(1)

        print("\nTest 3: URL that redirects (http://github.com should redirect to https)")
        msg3 = MockMessage("/headers http://github.com", "TestUserHeaders_3")
        await handle_headers(msg3, ["http://github.com"], mock_client, mock_bot)

        await asyncio.sleep(1)

        print("\nTest 4: Non-existent domain")
        msg4 = MockMessage("/headers https://th1sdomainsh0uldn0tex1stabcdef.com", "TestUserHeaders_4")
        await handle_headers(msg4, ["https://th1sdomainsh0uldn0tex1stabcdef.com"], mock_client, mock_bot)

        print("\nTest 5: No arguments")
        msg5 = MockMessage("/headers", "TestUserHeaders_5")
        await handle_headers(msg5, [], mock_client, mock_bot)

        print("\nTest 6: URL with potential SSL error (e.g. expired cert - hard to find a stable one)")
        # msg6 = MockMessage("/headers https://expired.badssl.com/", "TestUserHeaders_6")
        # await handle_headers(msg6, ["https://expired.badssl.com/"], mock_client, mock_bot)
        # print("Skipping Test 6: expired.badssl.com can be unreliable for automated tests.")


    # HTTP requests are network-dependent.
    asyncio.run(main_test())
