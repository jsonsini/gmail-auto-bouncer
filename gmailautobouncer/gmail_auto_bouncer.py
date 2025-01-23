#!/usr/bin/env python3
"""
Replies to unread messages based on configured settings.

This module uses the GMail API to find all unread messages from the inbox and
spam folders of an account and sends a reply back to each one with a default or
customized message.  If the account of the sender does not accept incoming
messages an alternate address to forward the response can be provided in the
configuration.  The option to keep the reply message for auditing purposes is
also included should that be preferred.  In addition to that multiple replies
can be sent in parallel for any configured message via a concurrent pool
specified individually by a parameter.  All deleted messages are logged as
being found in the configured reply mapping.

Glossary of configuration properties:

credentials_file
    Full path of JSON based credentials downloaded from account console
default_prefix
    Standard response prepended to messages found in the reply mapping
delete_delay
    Number of seconds to wait after sending before deleting the reply message
logging_config
    Formatters, handlers, and level specifications for logging
pool_size
    Maximum number of processes in parallel for concurrent replies
reply_mapping
    Custom parameters for each from address to override defaults
scopes
    URL associated with group of GMail API permissions
token_file
    Full path of OAuth 2.0 token in JSON format

Glossary of reply_mapping properties:

keep_reply
    Flag to retain reply messages in sent box for record keeping purposes
multiple
    Number of reply messages to send to specified recipient
prefix
    Customer response to prepend to original message body in reply
to
    Address to send reply to in case sender cannot receive incoming messages

Notes
-----
Gmail Auto Bouncer is distributed under the GNU Affero General Public License
v3 (https://www.gnu.org/licenses/agpl.html) as open source software with
attribution required.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License v3
(https://www.gnu.org/licenses/agpl.html) for more details.

Copyright (C) 2025 John Sonsini.  All rights reserved.  Source code available
under the AGPLv3.

"""
import base64
import email.mime.text
import logging.config
import os.path
import sys
import time

import googleapiclient.discovery
import google_auth_oauthlib.flow
import google.auth.exceptions
import google.auth.transport.requests
import google.oauth2.credentials

import gmailautobouncer.config_manager
import gmailautobouncer.utilities


class GmailAutoBouncer(object):
    """
    Replies to unread messages based on configured settings.

    This class uses the GMail API to find all unread messages from the inbox
    and spam folders of an account and sends a reply back to each one with a
    default or customized message.  If the account of the sender does not
    accept incoming messages an alternate address to forward the response can
    be provided in the configuration.  The option to keep the reply message for
    auditing purposes is also included should that be preferred.  In addition
    to that multiple replies can be sent in parallel for any configured message
    via a concurrent pool specified individually by a parameter.  All deleted
    messages are logged as being found in the configured reply mapping.

    """

    _conf_man = None
    """obj: Configuration wrapper utility."""
    _logger = None
    """obj: Logging utility."""

    def __init__(self, config_path):
        """
        Prepares all needed instance variables for scraping.

        Sets up logging utilities, GMail OAuth 2.0 credentials and token,
        mapping of email addresses to customized handling, standardized response
        message, degree of concurrency, and wait time before deleting messages.

        Parameters
        ----------
        config_path : str
            File path to JSON configuration.

        """
        if not GmailAutoBouncer._conf_man:
            GmailAutoBouncer._conf_man = \
                gmailautobouncer.config_manager.ConfigurationManager()
            GmailAutoBouncer._conf_man.load_configuration(config_path)
            logging.config.dictConfig(GmailAutoBouncer._conf_man.get_property(
                "logging_config"))
            GmailAutoBouncer._logger = logging.getLogger("gmail_auto_bouncer")
            GmailAutoBouncer._logger.debug(
                "configuration loaded from %s" % config_path)
        self.__scopes = GmailAutoBouncer._conf_man.get_property("scopes")
        """list: List of endpoints associated with API permissions."""
        self.__credentials_file = GmailAutoBouncer._conf_man.get_property(
            "credentials_file")
        """obj: Downloaded OAuth 2.0 credentials in JSON format."""
        self.__token_file = GmailAutoBouncer._conf_man.get_property(
            "token_file")
        """obj: Generated OAuth 2.0 token in JSON format."""
        self.__reply_mapping = GmailAutoBouncer._conf_man.get_property(
            "reply_mapping")
        """dict: Mapping of email addresses to reply parameters."""
        self.__default_prefix = GmailAutoBouncer._conf_man.get_property(
            "default_prefix")
        """str: Default string prepended to replies unless overridden."""
        self.__pool_size = GmailAutoBouncer._conf_man.get_property("pool_size")
        """int: Maximum number of concurrent processes in pool."""
        self.__delete_delay = GmailAutoBouncer._conf_man.get_property(
            "delete_delay")
        """int: Number of seconds to wait before deleting reply message."""

    def __get_credentials(self):
        """
        Retrieves GMail OAuth 2.0 credentials.

        Loads credentials from local file system based on configured path if
        available else attempts to refresh existing credentials if expired else
        loads credentials from downloaded new authorization code.

        Returns
        -------
        credentials : obj
            OAUth 2.0 credentials.

        """
        GmailAutoBouncer._logger.debug("getting gmail credentials")
        credentials = None
        # determines if the token exists locally
        if os.path.exists(self.__token_file):
            GmailAutoBouncer._logger.debug("found gmail credentials at %s"
                                           % self.__token_file)
            # loads the credentials from the found token
            credentials = \
                google.oauth2.credentials.Credentials.from_authorized_user_file(
                    self.__token_file, self.__scopes)
        # determines if the token does not exist or is not valid
        if not credentials or not credentials.valid:
            # determines if the token exists and has expired and needs to be
            # refreshed
            if credentials and credentials.expired \
                    and credentials.refresh_token:
                try:
                    # attempts to refresh the token
                    credentials.refresh(
                        google.auth.transport.requests.Request())
                except google.auth.exceptions.RefreshError:
                    # aborts execution based on manual credential download
                    # required
                    GmailAutoBouncer._logger.warn(
                        "Gmail credentials expired, need to update manually, "
                        "aborting processing")
                    sys.exit()
            else:
                # convenience instance to handle OAuth 2.0 credential processing
                flow = google_auth_oauthlib.flow.InstalledAppFlow. \
                    from_client_secrets_file(self.__credentials_file,
                                             self.__scopes)
                # opens a local browser window to download credentials manually
                credentials = flow.run_local_server(port=0)
            with open(self.__token_file, "w") as token_file:
                GmailAutoBouncer._logger.debug("writing gmail credentials to %s"
                                               % self.__token_file)
                # writes credentials to local file
                token_file.write(credentials.to_json())
        GmailAutoBouncer._logger.debug("got gmail credentials")
        return credentials

    def __get_header_field(self, headers, field_name):
        """
        Finds header value from list of mappings if available.

        Searches the list of message header mappings to select the matching
        field and return a new mapping of the list index to field value.  If not
        found in the list return a null value with an invalid index.

        Parameters
        ----------
        headers : list
            Name value pairs of message header information.
        field_name : str
            Specific field in header to get value from.

        Returns
        -------
        dict
            Mapping of list index to header field value.

        """
        GmailAutoBouncer._logger.debug("getting header field %s" % field_name)
        index = 0
        # iterates over headers to find matching field name
        for info in headers:
            if info["name"] == field_name:
                GmailAutoBouncer._logger.debug(
                    "got header field %s - %s" % (field_name, info["value"]))
                # returns the index and corresponding header field value
                return {"index": index, "value": info["value"]}
            index += 1
        GmailAutoBouncer._logger.warning("did not find header field %s"
                                         % field_name)
        # returns null value if header field name not found in list
        return {"index": -1, "value": None}

    def __process_message(self, message):
        """
        Extracts necessary fields from message for constructing response.

        Collects the sent datetime, to address, subject, and either the full
        message body or a leading snippet depending on which fields are
        available.

        Parameters
        ----------
        message : dict
            Mapping of message metadata and payload information.

        Returns
        -------
        date_field : dict
            Mapping of index to sent datetime of associated message.
        to_field : dict
            Mapping of index to to address of associated message.
        subject_field : dict
            Mapping of index to subject of associated message.
        message_body : str
            Available text of message body.

        """
        GmailAutoBouncer._logger.debug("processing message")
        headers = message["payload"]["headers"]
        # extracts the sent datetime from the header fields
        date_field = self.__get_header_field(headers, "Date")
        # extracts the to address from the header fields
        to_field = self.__get_header_field(headers, "To")
        # extracts the subject from the header fields
        subject_field = self.__get_header_field(headers, "Subject")
        # determines which field contains the message body
        if "parts" in message["payload"] and \
                "data" in message["payload"]["parts"][0]["body"]:
            # decodes the full message body
            message_body = base64.urlsafe_b64decode(
                message["payload"]["parts"][0]["body"]["data"]).decode("utf-8")
        else:
            # extracts the leading portion of the message body
            message_body = message["snippet"]
        GmailAutoBouncer._logger.debug("processed message")
        return date_field, to_field, subject_field, message_body

    def __construct_reply(self, from_field, date_field, to_field,
                          subject_field, message_body, reply_attributes):
        """
        Builds response message body from original header fields and attributes.

        Creates the reply message body from the original message, a default or
        customized prefix text, and metadata from the original message before
        encoding the reply in a mapping.

        Parameters
        ----------
        from_field : dict
            Mapping of index to from address of associated message.
        date_field : dict
            Mapping of index to sent datetime of associated message.
        to_field : dict
            Mapping of index to to address of associated message.
        subject_field : dict
            Mapping of index to subject of associated message.
        message_body : str
            Available text of message body.
        reply_attributes : dict
            Name value pairs to override default parameters for the associated
            message.

        Returns
        -------
        raw_reply : dict
            Mapping of the encoded reply message with associated metadata.

        """
        GmailAutoBouncer._logger.debug("constructing reply")
        # includes a customized response if specified, else the default
        prefix = reply_attributes["prefix"] if "prefix" in reply_attributes \
            else self.__default_prefix
        # captures the original message metadata to be included in the reply
        metadata = "From:  %s\nSent:  %s\nTo:  %s\nSubject:  %s" \
                   % (from_field["value"], date_field["value"],
                      to_field["value"], subject_field["value"])
        # creates the text based reply message
        reply_message = email.mime.text.MIMEText(
            "%s\n\n%s\n\n%s" % (prefix, metadata, message_body))
        # adds the configured or default to field to the reply message
        reply_message["to"] = reply_attributes["to"] if "to" in \
            reply_attributes else from_field["value"]
        # adds the from field to the reply message
        reply_message["from"] = to_field["value"]
        # adds the subject field to the reply message
        reply_message["subject"] = "Re:  %s" % subject_field["value"]
        # encodes the reply message body and associated metadata fields
        raw_reply = {
            "raw": base64.urlsafe_b64encode(
                reply_message.as_bytes()).decode()}
        GmailAutoBouncer._logger.debug("constructed reply")
        return raw_reply

    def send_reply(self, service, raw_reply, keep_reply, index):
        """
        Returns original message to configured recipient.

        Sends original message with metadata and a brief response prepended to
        the sender or an alternate address as configured and either deletes the
        reply message or retains it as specified.  Replies will continue to be
        attempted until successful.

        Parameters
        ----------
        service : obj
            A resource object with methods for interacting with service.
        raw_reply : dict
            Mapping of the encoded reply message with associated metadata.
        keep_reply : bool
            Flag determining if reply should be deleted or kept.
        index : int
            When multiple replies configured, the index of each message.

        """
        GmailAutoBouncer._logger.debug("sending and deleting reply - %s"
                                       % index)
        success = False
        # loops until reply successfully sent
        while not success:
            try:
                # sends the message
                reply = service.users().messages().send(
                    userId="me", body=raw_reply).execute()
                if not keep_reply:
                    # waits until reply is available in sent box
                    time.sleep(self.__delete_delay)
                    # deletes the reply
                    service.users().messages().delete(
                        userId="me", id=reply["id"]).execute()
                success = True
            except:
                GmailAutoBouncer._logger.warning(
                    "reply not sent, attempting again, error %s"
                    % gmailautobouncer.utilities.format_error(sys.exc_info()))
        GmailAutoBouncer._logger.debug("sent and deleted reply - %s" % index)

    def execute(self):
        """
        Processes all replies to messages with configured responses.

        Creates a resource for accessing the GMail API with credentials to list
        unread messages in the inbox and spam folders.  Iterates over resulting
        list to determine whether a configured response exists and if so
        proceeds to construct a response message.  Based on configuration
        parameters sends one or more replies and deletes the original message
        if desired.

        """
        GmailAutoBouncer._logger.info("executing automatic message bouncing")
        # finds the credentials
        credentials = self.__get_credentials()
        # creates the service for interacting with Gmail
        service = googleapiclient.discovery.build("gmail", "v1",
                                                  credentials=credentials)
        results = list()
        # retrieves unread messages from the inbox
        inbox_results = service.users().messages().list(
            userId="me", maxResults=100, pageToken=1, q="is:unread",
            labelIds=["INBOX"], includeSpamTrash=True).execute()
        if "messages" in inbox_results:
            results.extend(inbox_results["messages"])
        # retrieves unread messages from the spam folder
        spam_results = service.users().messages().list(
            userId="me", maxResults=100, pageToken=1, q="is:unread",
            labelIds=["SPAM"], includeSpamTrash=True).execute()
        if "messages" in spam_results:
            results.extend(spam_results["messages"])
        # iterates over unread messages
        for message_id in results:
            GmailAutoBouncer._logger.debug(
                "processing message ID %s" % message_id["id"])
            message = service.users().messages().get(
                userId="me", id=message_id["id"]).execute()
            from_field = self.__get_header_field(message["payload"]["headers"],
                                                 "From")
            # determines whether the sender is in the reply mappings
            if from_field["index"] < 0 or not from_field["value"] or \
                    not from_field["value"] in self.__reply_mapping:
                GmailAutoBouncer._logger.debug(
                    "sender of unread message %s not found in reply mapping, "
                    "no action taken" % from_field["value"])
            else:
                # gets any custom attributes related to the from address
                reply_attributes = self.__reply_mapping[from_field["value"]]
                GmailAutoBouncer._logger.info(
                    "sender of unread message %s found in reply mapping"
                    % from_field["value"])
                # collects metadata about the original message
                date_field, to_field, subject_field, message_body = \
                    self.__process_message(message)
                # retrieves a dictionary of the response and metadata
                raw_reply = self.__construct_reply(
                    from_field, date_field, to_field, subject_field,
                    message_body, reply_attributes)
                # determines if multiple replies are to be sent in response
                if "multiple" in reply_attributes:
                    GmailAutoBouncer._logger.debug(
                        "Sending %s replies." % reply_attributes["multiple"])
                    # creates a pool to send replies in parallel
                    with gmailautobouncer.utilities.NonDaemonicPool(
                            processes=self.__pool_size) as pool:
                        pool.starmap(
                            self.send_reply,
                            [(service, raw_reply,
                              reply_attributes["keep_reply"]
                              if "keep_reply" in reply_attributes else False,
                              i) for i in range(reply_attributes["multiple"])])
                    GmailAutoBouncer._logger.debug(
                        "Sent %s replies." % reply_attributes["multiple"])
                else:
                    # sends a response to the original message
                    self.send_reply(
                        service, raw_reply,
                        reply_attributes["keep_reply"]
                        if "keep_reply" in reply_attributes else False, 0)
                # removes the original message from the corresponding box
                service.users().messages().delete(
                    userId="me", id=message_id["id"]).execute()
            GmailAutoBouncer._logger.debug(
                "processed message ID %s" % message_id["id"])
        GmailAutoBouncer._logger.info("executed automatic message bouncing")


if __name__ == '__main__':
    pass
