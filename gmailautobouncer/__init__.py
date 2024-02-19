#!/usr/bin/env python3
"""
Gmail Auto Bouncer: Automated configurable message bouncing utility

Gmail Auto Bouncer is an open source package for performing automatic message
bouncing with GMail accounts so that after setting up the configuration for a
specific sender the user does not have the hassle of dealing with unwanted
messages in the future and no trace of the message or reply (if configured)
will exist in the associated account.  How many replies are sent, individual
response messages, forwarding addresses, and the option of keeping the replies
are all configurable wth no limitation on the number of from addresses to
bounce.  This utility is designed to be executed in conjunction with a
scheduler such as cron on a daily or hourly basis to minimize the inconvenience
of repetitive spam messages from specific senders.

Notes
-----
Gmail Auto Bouncer is distributed under the GNU Affero General Public License
v3 (https://www.gnu.org/licenses/agpl.html) as open source software with
attribution required.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License v3
(https://www.gnu.org/licenses/agpl.html) for more details.

Copyright (C) 2024 John Sonsini.  All rights reserved.  Source code available
under the AGPLv3.

"""
from . import __main__ as main

__all__ = [
    "config_manager",
    "gmail_auto_bouncer",
    "utilities"
]
