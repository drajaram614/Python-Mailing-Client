# Python Mailing Client with OAuth2

## Overview

This project is a Python-based mailing client that utilizes the Gmail API for sending emails with attachments. It employs OAuth2 for secure authentication, allowing users to send emails programmatically from their Gmail accounts. The client can read email content from a text file and attach images or other files to the email.

## Features

- **OAuth2 Authentication**: Securely authenticate with Google to access Gmail API.
- **Email Composition**: Read email body from a text file.
- **File Attachment**: Attach files (e.g., images) to the email.
- **Error Handling**: Handles file not found errors gracefully.

## Prerequisites

Before running this project, ensure you have the following:

- Python 3.x installed.
- Google Cloud Project with Gmail API enabled.
- OAuth2 credentials downloaded in `credentials.json`.
- Required Python packages for google api, google auth

  
## Project Structure
├── car.jpg             # Image file to be attached to the email
├── credentials.json     # OAuth2 credentials file
├── message.txt          # Text file containing the email body
├── mailing_client.py     # Main script for the mailing client
└── token.json           # Token file to store user credentials
