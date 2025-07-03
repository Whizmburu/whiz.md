# commands/text_fonts/fancy_command.py
import asyncio

# Unicode character mappings for various fancy styles
# Source: Mostly from online unicode text converters
# This is not exhaustive and can be expanded.

FANCY_STYLES = {
    "bold": {
        "normal": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        "fancy": "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵"
    },
    "italic": {
        "normal": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "fancy": "𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡"
        # Italic numbers are not commonly available as single unicode chars easily, often mixed with normal numbers
    },
    "bold_italic": {
        "normal": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "fancy": "𝙖𝙗𝙘𝙙𝙚𝙛𝙜𝙝𝙞𝙟𝙠𝙡𝙢𝙣𝙤𝙥𝙦𝙧𝙨𝙩𝙪𝙫𝙬𝙭𝙮𝙯𝘼𝘽𝘾𝘿𝙀𝙁𝙂𝙃𝙄𝙅𝙆𝙇𝙈𝙉𝙊𝙋𝙌𝙍𝙎𝙏𝙐𝙑𝙒𝙓𝙔𝙕"
    },
    "script": { # Mathematical Script
        "normal": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "fancy": "𝒶𝒷𝒸𝒹𝑒𝒻𝑔𝒽𝒾𝒿𝓀𝓁𝓂𝓃𝑜𝓅𝓆𝓇𝓈𝓉𝓊𝓋𝓌𝓍𝓎𝓏𝒜ℬ𝒞𝒟ℰℱ𝒢ℋℐ𝒥𝒦ℒℳ𝒩𝒪𝒫𝒬ℛ𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵"
    },
    "script_bold": { # Mathematical Bold Script
        "normal": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "fancy": "𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟𝓠𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩"
    },
    "fraktur": { # Mathematical Fraktur
        "normal": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "fancy": "𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷𝔄𝔅ℭ𝔇𝔈𝔉𝔊ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔖𝔗𝔘𝔙𝔚𝔛𝔜ℨ"
    },
    "fraktur_bold": { # Mathematical Bold Fraktur
        "normal": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "fancy": "𝖆𝖇𝖈𝖉𝖊𝖋𝖌𝖍𝖎𝖏𝖐𝖑𝖒𝖓𝖔𝖕𝖖𝖗𝖘𝖙𝖚𝖛𝖜𝖝𝖞𝖟𝕬𝕭𝕮𝕯𝕰𝕱𝕲𝕳𝕴𝕵𝕶𝕷𝕸𝕹𝕺𝕻𝕼𝕽𝕾𝕿𝖀𝖁𝖂𝖃𝖄𝖅"
    },
    "monospace": {
        "normal": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        "fancy": "𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿"
    },
    "doublestruck": { # Double-Struck (often for sets in math, e.g. ℝ for real numbers)
        "normal": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", # Some letters don't have standard double-struck lowercase
        "fancy": "𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𕍢𝕎𝕏𝕐ℤ𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡" # Note: \U0001D55D is 𝕝, etc. 𝕍 is \U0001D54D, 𝕎 is \U0001D54E
    },
    "smallcaps": {
        # True small caps are limited in Unicode. These are the Unicode Small Capital letters.
        # Lowercase letters are converted to these if a direct mapping exists, otherwise to their uppercase equivalent.
        "normal": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "fancy": "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢABCDEFGHIJKLMNOPQRSTUVWXYZ" # Using full-size caps for missing small caps lowercase. x and q are tricky.
        # A better map would convert 'a' to 'ᴀ', 'B' to 'B' (as small cap B is same as cap B visually in many fonts if not scaled)
        # For a true "tiny text" effect, one might just use smaller font size if platform supports,
        # or use a mix of actual small cap characters and regular lowercase for those not available.
        # This version primarily provides the Unicode SMALL CAPITAL letters for input 'a-z' and 'A-Z'.
        # For a more common "small caps" effect where 'a' -> 'A' (small version), 'b' -> 'B' (small version) etc.
        # This is typically a font rendering feature, not a direct Unicode char swap for all letters.
        # The provided 'fancy' string here uses available Unicode small capital letters.
        # Let's refine: map lowercase to available small caps, and uppercase to standard uppercase (as they'd be the 'large' caps).
        # Or, more simply, map all input a-z and A-Z to the available small caps (A-Z like).
        # "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ" are for a-z. What about A-Z input?
        # For "tiny text", it's usually about making all letters look like smaller capitals.
        # So, a->ᴀ, b->ʙ, ..., z->ᴢ, A->ᴀ, B->ʙ, ..., Z->ᴢ.
        # Small caps for q, x are often missing. Using phonetic extensions or regular letters for those.
        # q -> q (regular), x -> x (regular) or similar looking small caps if available.
        # Using standard uppercase for letters without direct small_cap unicode.
        # True small caps: A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
        # Unicode:        ᴀ ʙ ᴄ ᴅ ᴇ ғ ɢ ʜ ɪ ᴊ ᴋ ʟ ᴍ ɴ ᴏ P Q R s ᴛ ᴜ V w x Y Z (P,Q,R,S,T,U,V,W,X,Y,Z are not true small caps but phonetic symbols or regular caps)
        # For a simpler "tiny text" (superscript like, but not always):
        # Let's provide a common "smallcaps" based on available Unicode block:
        # U+1D2C - U+1D6A has some.
        # For simplicity, I'll use a common mapping found online for "small caps generator"
        # This often means converting all letters to their uppercase versions first, then mapping.
        # Or mapping lowercase to available small caps, and uppercase to... also small caps.
        # Standard approach for "tiny text" generators:
        # a -> ᴀ, b -> ʙ, c -> ᴄ, ..., A -> ᴀ, B -> ʙ ...
        # Using a good mapping:
        "normal": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        "fancy":  "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ0123456789"
        # Note: some characters like 'q' and 'x' might not have perfect small cap Unicode equivalents
        # and may appear as regular lowercase or slightly different symbols.
        # The above fancy string maps both lower and upper to the same set of small cap looking chars.
    }
    # Add more styles as needed: e.g., circled, squared, parenthesized
}

def convert_text_to_fancy(text, style_name):
    if style_name not in FANCY_STYLES:
        return f"Style '{style_name}' not found. Available styles: {', '.join(FANCY_STYLES.keys())}"

    style = FANCY_STYLES[style_name]
    translation_table = str.maketrans(style["normal"], style["fancy"])
    return text.translate(translation_table)

async def handle_fancy(message, args, client, bot_instance):
    """
    Handles the /fancy command.
    Converts text to a specified fancy Unicode style.
    Usage: /fancy <style_name> <text_to_convert>
           /fancy list (to see available styles)
    """
    command_name = "fancy"
    print(f"Executing /{command_name} with args: {args} for message: {message.sender if hasattr(message, 'sender') else 'Unknown'}")

    if not args:
        if hasattr(message, 'reply'): await message.reply(f"Usage: /{command_name} <style> <text> OR /{command_name} list")
        return

    style_arg = args[0].lower()

    if style_arg == "list":
        available_styles = ", ".join(FANCY_STYLES.keys())
        if hasattr(message, 'reply'): await message.reply(f"Available fancy styles: {available_styles}")
        return

    if len(args) < 2:
        if hasattr(message, 'reply'): await message.reply(f"Please provide text to convert. Usage: /{command_name} {style_arg} <text>")
        return

    text_to_convert = " ".join(args[1:])
    converted_text = convert_text_to_fancy(text_to_convert, style_arg)

    if hasattr(message, 'reply'):
        await message.reply(converted_text)
    else:
        print(f"Original: {text_to_convert}\n{style_arg}: {converted_text}")


if __name__ == '__main__':
    class MockMessage:
        def __init__(self, text, sender):
            self.text = text
            self.sender = sender
        async def reply(self, text_content):
            print(f"BOT REPLIED TO {self.sender}: {text_content}")

    class MockClient: pass
    class MockBotInstance: pass

    async def main_test():
        mock_bot = MockBotInstance()
        mock_client = MockClient()

        print("\n--- Fancy Text Test Cases ---")

        test_text = "Hello World 123"

        print("\nTest 1: List styles")
        msg_list = MockMessage("/fancy list", "TestUserFancy_List")
        await handle_fancy(msg_list, ["list"], mock_client, mock_bot)

        print("\nTest 2: Specific style (bold)")
        msg_bold = MockMessage(f"/fancy bold {test_text}", "TestUserFancy_Bold")
        await handle_fancy(msg_bold, ["bold", test_text], mock_client, mock_bot)

        print("\nTest 3: Specific style (script)")
        msg_script = MockMessage(f"/fancy script {test_text}", "TestUserFancy_Script")
        await handle_fancy(msg_script, ["script", test_text], mock_client, mock_bot)

        print("\nTest 4: Specific style (monospace)")
        msg_mono = MockMessage(f"/fancy monospace {test_text}", "TestUserFancy_Monospace")
        await handle_fancy(msg_mono, ["monospace", test_text], mock_client, mock_bot)

        print("\nTest 5: Invalid style")
        msg_invalid = MockMessage(f"/fancy non_existent_style {test_text}", "TestUserFancy_Invalid")
        await handle_fancy(msg_invalid, ["non_existent_style", test_text], mock_client, mock_bot)

        print("\nTest 6: No text provided")
        msg_no_text = MockMessage("/fancy bold", "TestUserFancy_NoText")
        await handle_fancy(msg_no_text, ["bold"], mock_client, mock_bot)

        print("\nTest 7: No args provided")
        msg_no_args = MockMessage("/fancy", "TestUserFancy_NoArgs")
        await handle_fancy(msg_no_args, [], mock_client, mock_bot)

    asyncio.run(main_test())
