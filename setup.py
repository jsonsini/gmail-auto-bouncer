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

Example
-------
To install Gmail Auto Bouncer, simply execute the following command from the
download directory:

sudo python3 setup.py install

To execute Gmail Auto Bouncer from the command line run the following:

gmail-auto-bouncer /full/path/to/configuration/file.json

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
import setuptools

setuptools.setup(
    name="gmail-auto-bouncer",
    version="1.0",
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": [
            "gmail-auto-bouncer=gmailautobouncer.__main__:main"
        ]
    },
    python_requires=">3.8.4",
    install_requires=[
        "google-api-core>=2.0.1",
        "google-api-python-client>=2.19.1",
        "google-auth>=2.0.2",
        "google-auth-httplib2>=0.1.0",
        "google-auth-oauthlib>=0.4.6",
        "googleapis-common-protos>=1.53.0"
    ],
    include_package_data=True,
    author="John Sonsini",
    author_email="john.a.sonsini@gmail.com",
    description="Performs configurable automatic replies to gmail messages",
    license="GNU AGPLv3",
    keywords="gmail spam auto-bouncer",
    url="https://github.com/jsonsini/gmail-auto-bouncer",
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.8",
        "Topic :: Communications :: Email :: Filters"
    ]
)
