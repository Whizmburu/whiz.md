# commands/downloaders/__init__.py

from .ytmp3_command import handle_ytmp3
from .ytmp4_command import handle_ytmp4
from .igdl_command import handle_igdl
from .tiktok_command import handle_tiktok
from .fb_command import handle_fb
from .twitter_command import handle_twitter
from .mediafire_command import handle_mediafire
from .apk_command import handle_apk

__all__ = [
    "handle_ytmp3",
    "handle_ytmp4",
    "handle_igdl",
    "handle_tiktok",
    "handle_fb",
    "handle_twitter",
    "handle_mediafire",
    "handle_apk",
]
