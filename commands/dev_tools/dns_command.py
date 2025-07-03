# commands/dev_tools/dns_command.py
import asyncio
import dns.resolver
import dns.reversename

VALID_DNS_TYPES = ['A', 'AAAA', 'MX', 'TXT', 'CNAME', 'NS', 'SOA', 'SRV', 'PTR']

async def get_dns_records(domain_name, record_type='A'):
    """Helper function to query DNS records."""
    results = []
    record_type = record_type.upper()
    if record_type not in VALID_DNS_TYPES:
        return [f"Invalid DNS record type: {record_type}. Valid types: {', '.join(VALID_DNS_TYPES)}"]

    try:
        if record_type == 'PTR': # PTR requires reverse DNS address format
            # For simplicity, assume domain_name is an IP for PTR. A more robust PTR would validate/convert.
            # Example: if domain_name is "1.2.3.4", it becomes "4.3.2.1.in-addr.arpa."
            # This simple version won't auto-convert general domain names to IPs for PTR.
            # User must provide an IP for PTR or a correctly formatted reverse DNS name.
            try:
                # Attempt to treat input as an IP address for PTR lookup
                addr = dns.reversename.from_address(domain_name)
                answers = dns.resolver.resolve(addr, record_type)
            except dns.exception.SyntaxError: # If domain_name is not an IP
                 answers = dns.resolver.resolve(domain_name, record_type) # Try as is

        else: # For other record types
            answers = dns.resolver.resolve(domain_name, record_type)

        for rdata in answers:
            if record_type == 'A' or record_type == 'AAAA':
                results.append(rdata.address)
            elif record_type == 'MX':
                results.append(f"Preference: {rdata.preference}, Mail Exchanger: {rdata.exchange.to_text(omit_final_dot=True)}")
            elif record_type == 'TXT':
                # TXT records can be bytes or list of bytes, decode them
                # Each rdata.strings is a tuple of bytes
                results.append(" ".join(s.decode('utf-8', 'ignore') for s in rdata.strings))
            elif record_type == 'CNAME' or record_type == 'NS':
                results.append(rdata.target.to_text(omit_final_dot=True))
            elif record_type == 'SOA':
                results.append(f"MNAME: {rdata.mname.to_text(omit_final_dot=True)}, RNAME: {rdata.rname.to_text(omit_final_dot=True)}, Serial: {rdata.serial}")
            elif record_type == 'SRV':
                results.append(f"Priority: {rdata.priority}, Weight: {rdata.weight}, Port: {rdata.port}, Target: {rdata.target.to_text(omit_final_dot=True)}")
            elif record_type == 'PTR':
                 results.append(rdata.target.to_text(omit_final_dot=True))
            else:
                results.append(rdata.to_text())
    except dns.resolver.NXDOMAIN:
        results.append(f"No such domain: {domain_name}")
    except dns.resolver.NoAnswer:
        results.append(f"No {record_type} records found for {domain_name}")
    except dns.resolver.Timeout:
        results.append(f"DNS query timed out for {domain_name}")
    except dns.exception.DNSException as e:
        results.append(f"DNS query error for {domain_name} ({record_type}): {type(e).__name__} - {e}")

    return results if results else ["No records found or error."]


async def handle_dns(message, args, client, bot_instance):
    """
    Handles the /dns command.
    Performs DNS lookups for a given domain and record type.
    Usage: /dns <domain_name> [record_type] (default: A)
           /dns <record_type> <domain_name> (alternative order)
           /dns all <domain_name> (for common record types)
    """
    command_name = "dns"
    print(f"Executing /{command_name} with args: {args} for message: {message.sender if hasattr(message, 'sender') else 'Unknown'}")

    if not args:
        if hasattr(message, 'reply'): await message.reply(f"Usage: /{command_name} <domain> [type] OR /{command_name} <type> <domain> OR /{command_name} all <domain>")
        return

    domain_name = ""
    record_type_req = "A" # Default record type

    if len(args) == 1:
        domain_name = args[0]
    elif len(args) >= 2:
        # Check if first arg is a valid type or "all"
        if args[0].upper() in VALID_DNS_TYPES or args[0].lower() == "all":
            record_type_req = args[0].upper()
            domain_name = " ".join(args[1:]) # Domain can have spaces if user quotes it, though unlikely for DNS
            if len(args[1:]) > 1: # If domain has spaces, it's likely an error or quoted string
                 if hasattr(message, 'reply'): await message.reply("Warning: Domain names usually don't contain spaces. If your domain has spaces, ensure it's correctly specified.")
                 # For simplicity, we'll assume the first part after type is the domain.
                 domain_name = args[1]

        else: # Assume first arg is domain, second is type
            domain_name = args[0]
            record_type_req = args[1].upper()

    # Basic domain validation (similar to whois, but less strict as subdomains are common)
    if '.' not in domain_name or domain_name.startswith(('http://', 'https://')):
        # Allow IPs for PTR lookups if record_type_req is PTR
        is_ip_for_ptr = record_type_req == 'PTR' and all(c.isdigit() or c == '.' for c in domain_name) # Very basic IP check
        if not is_ip_for_ptr:
            if hasattr(message, 'reply'): await message.reply("Invalid domain/IP format. Provide a clean domain like 'example.com' or an IP for PTR lookups.")
            return

    response_message = f"🌐 DNS Lookup for {domain_name}:\n"

    if hasattr(message, 'reply'): await message.reply(f"🔍 Performing DNS lookup for {domain_name} (type: {record_type_req})...")

    record_types_to_query = []
    if record_type_req == "ALL":
        record_types_to_query = ['A', 'AAAA', 'MX', 'TXT', 'NS', 'CNAME', 'SOA']
    else:
        if record_type_req not in VALID_DNS_TYPES:
            if hasattr(message, 'reply'): await message.reply(f"Invalid DNS record type: {record_type_req}. Valid types: {', '.join(VALID_DNS_TYPES)}")
            return
        record_types_to_query = [record_type_req]

    all_results_empty = True
    for r_type in record_types_to_query:
        records = await get_dns_records(domain_name, r_type)
        if records and not (len(records)==1 and ("No such domain" in records[0] or f"No {r_type} records found" in records[0] or "DNS query error" in records[0])):
            all_results_empty = False
            response_message += f"\n--- {r_type} Records ---\n"
            for record in records:
                response_message += f"{record}\n"
        elif record_type_req != "ALL": # If specific type query yielded no answer or error
            response_message += f"\n--- {r_type} Records ---\n"
            response_message += f"{records[0]}\n" # Show the error/no answer message

    if all_results_empty and record_type_req == "ALL":
        response_message += "\nNo common DNS records found or domain does not exist."

    if len(response_message) > 1900 : # Discord max message length is 2000, common for bots
        response_message = response_message[:1900] + "\n... (output truncated)"

    if hasattr(message, 'reply'):
        await message.reply(response_message)
    else:
        print(response_message)


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

        print("\n--- DNS Test Cases ---")

        print("\nTest 1: A record for google.com")
        msg1 = MockMessage("/dns google.com A", "TestUserDNS_1")
        await handle_dns(msg1, ["google.com", "A"], mock_client, mock_bot)

        print("\nTest 1b: A record for google.com (alternative order)")
        msg1b = MockMessage("/dns A google.com", "TestUserDNS_1b")
        await handle_dns(msg1b, ["A", "google.com"], mock_client, mock_bot)

        print("\nTest 2: MX records for gmail.com")
        msg2 = MockMessage("/dns gmail.com MX", "TestUserDNS_2")
        await handle_dns(msg2, ["gmail.com", "MX"], mock_client, mock_bot)

        print("\nTest 3: TXT records for google.com")
        msg3 = MockMessage("/dns google.com TXT", "TestUserDNS_3")
        await handle_dns(msg3, ["google.com", "TXT"], mock_client, mock_bot)

        print("\nTest 4: ALL common records for github.com")
        msg4 = MockMessage("/dns all github.com", "TestUserDNS_4")
        await handle_dns(msg4, ["all", "github.com"], mock_client, mock_bot)

        print("\nTest 5: Non-existent domain")
        msg5 = MockMessage("/dns th1sdomainsh0uldn0tex1stabcdef.com A", "TestUserDNS_5")
        await handle_dns(msg5, ["th1sdomainsh0uldn0tex1stabcdef.com", "A"], mock_client, mock_bot)

        print("\nTest 6: Invalid record type")
        msg6 = MockMessage("/dns google.com INVALIDTYPE", "TestUserDNS_6")
        await handle_dns(msg6, ["google.com", "INVALIDTYPE"], mock_client, mock_bot)

        print("\nTest 7: No arguments")
        msg7 = MockMessage("/dns", "TestUserDNS_7")
        await handle_dns(msg7, [], mock_client, mock_bot)

        print("\nTest 8: PTR record for an IP (e.g., Google's DNS server 8.8.8.8)")
        msg8 = MockMessage("/dns PTR 8.8.8.8", "TestUserDNS_8")
        await handle_dns(msg8, ["PTR", "8.8.8.8"], mock_client, mock_bot)

        print("\nTest 9: CNAME for www.google.com (might not exist directly, or be an A/AAAA)")
        # www.google.com is typically an A/AAAA, not a CNAME to google.com.
        # Let's try a known CNAME, e.g. sometimes 'mail.domain.com' CNAMEs to 'ghs.googlehosted.com' or similar.
        # Using 'www.github.com' which often CNAMEs to 'github.com.' (or similar)
        msg9 = MockMessage("/dns CNAME www.github.com", "TestUserDNS_9")
        await handle_dns(msg9, ["CNAME", "www.github.com"], mock_client, mock_bot)


    asyncio.run(main_test())
