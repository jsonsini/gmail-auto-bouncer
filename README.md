# Gmail Auto Bouncer
Gmail Auto Bouncer is an open source package for performing automatic message bouncing with GMail accounts so that after setting up the configuration for a specific sender the user does not have the hassle of dealing with unwanted messages in the future and no trace of the message or reply (if configured) will exist in the associated account.  How many replies are sent, individual response messages, forwarding addresses, and the option of keeping the replies are all configurable wth no limitation on the number of from addresses to bounce.  This utility is designed to be executed in conjunction with a scheduler such as cron on a daily or hourly basis to minimize the inconvenience of repetitive spam messages from specific senders.

### Installation
To install Gmail Auto Bouncer, simply execute the following command from the download directory:
```bash
sudo python setup.py install
```

To execute Gmail Auto Bouncer from the command line run the following:
```bash
gmail-auto-bouncer /full/path/to/configuration/file.json
```

### Glossary of configuration properties:
Name | Description
--- | ---
credentials_file | Full path of JSON based credentials downloaded from account console
default_prefix | Standard response prepended to messages found in the reply mapping
delete_delay | Number of seconds to wait after sending before deleting the reply message
logging_config | Formatters, handlers, and level specifications for logging
pool_size | Maximum number of processes in parallel for concurrent replies
reply_mapping | Custom parameters for each from address to override defaults
scopes | URL associated with group of GMail API permissions
token_file | Full path of OAuth 2.0 token in JSON format

### Glossary of reply_mapping properties:
Name | Description
--- | ---
keep_reply | Flag to retain reply messages in sent box for record keeping purposes
multiple | Number of reply messages to send to specified recipient
prefix | Custom response to prepend to original message body in reply
to | Address to send reply to in case sender cannot receive incoming messages

### Steps to set up the gmail-auto-bouncer project:
1. Login to the desired Google account here:  [https://accounts.google.com/ServiceLogin](https://accounts.google.com/ServiceLogin)
2. Follow the instructions here:  [https://cloud.google.com/resource-manager/docs/creating-managing-projects#creating_a_project](https://cloud.google.com/resource-manager/docs/creating-managing-projects#creating_a_project) to create a new "gmailautobouncer" project via the console
  * Note:  The default "No organization" can be used for the Location field when creating the project
3. Follow the instructions here:  [https://cloud.google.com/resource-manager/docs/creating-managing-projects#get_an_existing_project](https://cloud.google.com/resource-manager/docs/creating-managing-projects#get_an_existing_project) to select the created project via the console dashboard
4. Expand the "API & Services" menu in the left hand column and select the "Library" item
5. Select the "GMail API" button under the "Google Workspace" list and then select the "ENABLE" button on the resulting page
6. Select the "OAuth consent screen" item in the left hand column 
7. Select the "External" radio button and then select the "CREATE" button
8. Configure the OAuth consent screen as follows, then select the "SAVE AND CONTINUE" button:
  * App Name = gmail-auto-bouncer
  * User support email = *[your email address here]*
  * Developer contact information = *[your email address here]*
9. Select the "ADD OR REMOVE SCOPES" button to expand the right hand menu
10. Select the Gmail API and [https://mail.google.com/](https://mail.google.com/) API/Scope combination and then select the "UPDATE" button
11. Select the "SAVE AND CONTINUE" button
12. Select the "+ ADD USERS" button and type in your email address before selecting the "ADD" button
13. Select the "SAVE AND CONTINUE" button then select the "BACK TO DASHBOARD" button
14. Select the "Credentials" item in the left hand column
15. Expand the "+ CREATE CREDENTIALS" menu and select the "OAuth client ID" item
16. Configure the OAuth client ID as follows, then select the "CREATE" button:
  * Application type = Desktop app
  * Name = gmail-auto-bouncer
17. Select the "DOWNLOAD JSON" link at the bottom of the resulting dialog and save the file as gmail_auto_bouncer_credentials.json
18. Select "OK" to close the dialog

### Known Limitations
With a personal (non Google Workspace) account the gmail_auto_bouncer_credentials.json file downloaded from the OAuth consent screen is only valid for seven days as documented here:  [https://developers.google.com/identity/protocols/oauth2#expiration](https://developers.google.com/identity/protocols/oauth2#expiration) so steps 15 to 18 will need to be repeated to update the related authorization code.  Users can choose to publish their application by selecting "PUBLISH APP" from the OAUth consent screen configuration referenced in step 6 above to remove this limitation, the criteria to verify the application are listed below:

The OAuth consent screen has a "PUBLISH APP" button that requires:
 * An official link to your app's Privacy Policy
 * A YouTube video showing how you plan to use the Google user data you get from scopes
 * A written explanation telling Google why you need access to sensitive and/or restricted user data
 * All your domains verified in Google Search Console

### Additional Information
Limits for the GMail API are documented here:  [https://developers.google.com/gmail/api/reference/quota](https://developers.google.com/gmail/api/reference/quota).  In a typical case of sending one reply and deleting both the original message and the automated response 225 units are used so roughly 4.5 million spam messages can be handled but care should be taken when configuring the multiple parameter.  Also the pool_size and delete_delay parameters should be configured to respect the 250 units per second limitation.

### License Information
Gmail Auto Bouncer is distributed under the [GNU Affero General Public License v3](https://www.gnu.org/licenses/agpl.html) as open source software with attribution required.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the [GNU Affero General Public License v3](https://www.gnu.org/licenses/agpl.html) for more details.

Copyright (C) 2022 John Sonsini.  All rights reserved.  Source code available under the AGPLv3.
