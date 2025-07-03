# commands/dev_tools/whois_command.py
import asyncio
import whois # python-whois library
from datetime import datetime

async def handle_whois(message, args, client, bot_instance):
    """
    Handles the /whois command.
    Performs a WHOIS lookup for a given domain.
    Usage: /whois <domain_name>
    """
    command_name = "whois"
    print(f"Executing /{command_name} with args: {args} for message: {message.sender if hasattr(message, 'sender') else 'Unknown'}")

    if not args:
        if hasattr(message, 'reply'): await message.reply(f"Usage: /{command_name} <domain_name (e.g., example.com)>")
        return

    domain_name = args[0]
    # Basic validation: check for at least one dot and no http/https prefix
    if '.' not in domain_name or domain_name.startswith(('http://', 'https://')):
        if hasattr(message, 'reply'): await message.reply("Invalid domain name format. Please provide a clean domain like 'example.com'.")
        return

    reply_message = ""

    try:
        if hasattr(message, 'reply'): await message.reply(f"🔍 Performing WHOIS lookup for {domain_name}, please wait...")

        w = whois.whois(domain_name)

        if not w.domain_name: # If domain_name is None or empty, lookup likely failed or domain doesn't exist
            # Sometimes w might exist but critical fields are None.
            # The python-whois library might return a result object even for non-existent domains,
            # with many fields being None. Or it might raise an exception.
            # If w.text is empty and no domain_name, it's a strong indicator of failure.
            if not w.text and not any([w.creation_date, w.registrar, w.status]): # Check a few key fields
                 reply_message = f"⚠️ Could not retrieve WHOIS information for '{domain_name}'. The domain may not exist or the WHOIS server is unavailable."
            else: # Some data might be present, or it's a TLD not fully supported by simple parsing
                reply_message = f"📋 WHOIS information for {domain_name}:\n"
                if isinstance(w.domain_name, list):
                    reply_message += f"Domain Name: {', '.join(w.domain_name)}\n"
                else:
                    reply_message += f"Domain Name: {w.domain_name}\n"

                if w.registrar: reply_message += f"Registrar: {w.registrar}\n"

                # Dates can be single datetime objects or lists of them
                def format_date_field(date_field):
                    if isinstance(date_field, list):
                        return ", ".join([d.strftime('%Y-%m-%d %H:%M:%S') if isinstance(d, datetime) else str(d) for d in date_field])
                    elif isinstance(date_field, datetime):
                        return date_field.strftime('%Y-%m-%d %H:%M:%S')
                    return str(date_field) if date_field else "N/A"

                if w.creation_date: reply_message += f"Creation Date: {format_date_field(w.creation_date)}\n"
                if w.expiration_date: reply_message += f"Expiration Date: {format_date_field(w.expiration_date)}\n"
                if w.updated_date: reply_message += f"Updated Date: {format_date_field(w.updated_date)}\n"

                if w.name_servers: reply_message += f"Name Servers: {', '.join(w.name_servers)}\n"
                if w.status: reply_message += f"Status: {w.status}\n" # Can be a list or string
                if w.emails: reply_message += f"Emails: {', '.join(w.emails) if isinstance(w.emails, list) else w.emails}\n"

                # For more verbose output, one could include w.text, but it's often very long and unformatted.
                # reply_message += f"\nRaw Output (partial):\n```\n{w.text[:1000]}...\n```"

        else: # Successfully got some structured data
            reply_message = f"📋 WHOIS information for {w.domain_name if isinstance(w.domain_name, str) else domain_name}:\n"
            if w.registrar: reply_message += f"Registrar: {w.registrar}\n"

            def format_date_field(date_field):
                if isinstance(date_field, list):
                    return ", ".join([d.strftime('%Y-%m-%d %H:%M:%S') if isinstance(d, datetime) else str(d) for d in date_field])
                elif isinstance(date_field, datetime):
                    return date_field.strftime('%Y-%m-%d %H:%M:%S')
                return str(date_field) if date_field else "N/A"

            if w.creation_date: reply_message += f"Creation Date: {format_date_field(w.creation_date)}\n"
            if w.expiration_date: reply_message += f"Expiration Date: {format_date_field(w.expiration_date)}\n"
            if w.updated_date: reply_message += f"Updated Date: {format_date_field(w.updated_date)}\n"

            if w.name_servers: # name_servers is often a list
                ns_list = [ns.lower() for ns in w.name_servers] # Normalize to lowercase for consistency
                reply_message += f"Name Servers: {', '.join(sorted(list(set(ns_list))))}\n" # Sort and unique

            if w.status: # status can be a string or list
                if isinstance(w.status, list):
                    reply_message += f"Status: {', '.join(w.status)}\n"
                else:
                    reply_message += f"Status: {w.status}\n"

            if w.emails: # emails can be a string or list
                 if isinstance(w.emails, list):
                    reply_message += f"Contact Email(s): {', '.join(w.emails)}\n" # Often redacted
                 else:
                    reply_message += f"Contact Email(s): {w.emails}\n"

            # Optional: Add registrant information if available and not redacted
            if w.org: reply_message += f"Organization: {w.org}\n"
            # if w.name: reply_message += f"Registrant Name: {w.name}\n" # Often redacted

            # Truncate if too long for a message
            if len(reply_message) > 1500: # Arbitrary limit
                reply_message = reply_message[:1500] + "\n... (output truncated)"

    except whois.parser.PywhoisError as e: # Specific error from the library for parsing issues or no domain
        reply_message = f"⚠️ WHOIS lookup error for '{domain_name}': {e}. The domain may not exist or WHOIS data is unavailable/unparsable for this TLD."
    except Exception as e:
        print(f"Error in whois command for {domain_name}: {e}")
        reply_message = f"An unexpected error occurred during WHOIS lookup: {e}"

    if hasattr(message, 'reply'):
        await message.reply(reply_message)
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

        print("\n--- WHOIS Test Cases ---")

        print("\nTest 1: Valid domain (google.com)")
        # Note: WHOIS lookups can be slow and are subject to rate limits by servers.
        msg1 = MockMessage("/whois google.com", "TestUserWhois_1")
        await handle_whois(msg1, ["google.com"], mock_client, mock_bot)

        await asyncio.sleep(2) # Brief pause to avoid stressing WHOIS servers if running multiple tests

        print("\nTest 2: Domain that might not exist or has minimal info (e.g., a very new gTLD or specific ccTLD)")
        # Using a domain known for having parseable but sometimes unusual WHOIS data
        # msg2 = MockMessage("/whois example.org", "TestUserWhois_2") # example.com/org/net are IANA reserved
        # await handle_whois(msg2, ["example.org"], mock_client, mock_bot)
        # Using a more common TLD that python-whois handles well
        msg2 = MockMessage("/whois github.com", "TestUserWhois_Github")
        await handle_whois(msg2, ["github.com"], mock_client, mock_bot)

        await asyncio.sleep(2)

        print("\nTest 3: Invalid domain format")
        msg3 = MockMessage("/whois http://invalid-domain", "TestUserWhois_3")
        await handle_whois(msg3, ["http://invalid-domain"], mock_client, mock_bot)

        print("\nTest 4: Non-existent domain (hopefully)")
        msg4 = MockMessage("/whois th1sdomainsh0uldn0tex1stabcdef.com", "TestUserWhois_4")
        await handle_whois(msg4, ["th1sdomainsh0uldn0tex1stabcdef.com"], mock_client, mock_bot)

        print("\nTest 5: No arguments")
        msg5 = MockMessage("/whois", "TestUserWhois_5")
        await handle_whois(msg5, [], mock_client, mock_bot)

        # Test with a ccTLD known to have issues with some simple WHOIS parsers
        # For example, .de or .ru can sometimes be tricky without direct server support.
        # python-whois aims to handle many of these.
        # print("\nTest 6: ccTLD (e.g., .io)")
        # msg6 = MockMessage("/whois notion.io", "TestUserWhois_6")
        # await handle_whois(msg6, ["notion.io"], mock_client, mock_bot)


    # Running WHOIS tests can be slow due to network requests.
    asyncio.run(main_test())
