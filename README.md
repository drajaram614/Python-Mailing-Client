# Python Mailing Client with OAuth2

## Overview

This project is a Python-based mailing client that utilizes the Gmail API for sending emails with attachments. It employs OAuth2 for secure authentication, allowing users to send emails programmatically from their Gmail accounts. The client can read email content from a text file and attach images or other files to the email.

## Features

- **OAuth2 Authentication**: Securely authenticate with Google to access Gmail API.
- **Email Composition**: Read email body from a text file.
- **File Attachment**: Attach files (e.g., `images`) to the email.
- **Input Validation**:

Email addresses are validated using regular expressions to ensure they conform to standard email formats, reducing the risk of processing `malicious` or `invalid input`.
- **HTML Sanitization**:

If the email body contains HTML content, it is sanitized using the `bleach` library. This ensures that only allowed tags (like `<b>`, `<i>`, and `<a>`) are included, preventing Cross-Site Scripting (XSS) attacks.
- **Error Handling**:

Throughout the code, try-except blocks capture and handle errors, ensuring that issues (e.g., `missing files`, `invalid credentials`) do not crash the program. All errors are logged for analysis, helping to identify potential problems in the application flow.
- **Logging**:

Logs are maintained for every action taken by the program (such as `authentication`, `email sending`, `errors`, etc.), providing a detailed trace of the client’s activities. This is essential for auditing, troubleshooting, and detecting abnormal behaviors.
- **Content Filtering**:

The email body is scanned for malicious URLs or potentially dangerous code (like `exec`, `eval`, `os.system`) using regex patterns. This helps block malicious content from being sent through the client, mitigating the risk of `phishing` or `malicious code injection`.

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
