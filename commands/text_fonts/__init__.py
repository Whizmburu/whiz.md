# commands/text_fonts/__init__.py

from .fancy_command import handle_fancy
from .ascii_command import handle_ascii
from .emoji_command import handle_emoji
from .reverse_command import handle_reverse
from .zalgo_command import handle_zalgo
from .cursive_command import handle_cursive
from .tinytext_command import handle_tinytext

__all__ = [
    "handle_fancy",
    "handle_ascii",
    "handle_emoji",
    "handle_reverse",
    "handle_zalgo",
    "handle_cursive",
    "handle_tinytext",
]
