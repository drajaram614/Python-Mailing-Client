import os
import base64
import json
import re
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from bleach import clean  # Import bleach for HTML sanitization

# Define the scopes for Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Configure logging
logging.basicConfig(level=logging.INFO, filename='email_client.log', 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def is_valid_email(email):
    """Validate the email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def contains_malicious_content(message_text):
    """Check for potentially malicious links or attachments in the message text."""
    malicious_patterns = [
        r'(https?://[^\s]+)',  # URLs
        r'(?i)\b(?:exec|eval|system|shell|os\.system|subprocess|popen|import|open|os\.environ)\b'  # Dangerous functions
    ]
    for pattern in malicious_patterns:
        if re.search(pattern, message_text):
            logging.warning("Malicious content detected in the message.")
            return True
    return False

def authenticate_gmail():
    """Authenticates user using OAuth2, returns Gmail API service."""
    creds = None

    # Check if token.json file exists, which stores user credentials
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no valid credentials, go through the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service

def create_message(sender, to, subject, message_text):
    """Create a message for an email."""
    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = to
    message['Subject'] = subject

    # Reading the email body from a file
    try:
        with open('message.txt', 'r') as f:
            body = f.read()
            # Sanitize HTML content
            body = clean(body, tags=['b', 'i', 'u', 'a'], strip=True)  # Allow basic formatting tags
            if contains_malicious_content(body):
                logging.error("Email body contains potentially malicious content.")
                print("Error: Email body contains potentially malicious content.")
                return None
        message.attach(MIMEText(body, 'html'))  # Change to 'html' if using HTML content
    except FileNotFoundError:
        logging.error("The message.txt file was not found.")
        print("Error: The message body file is missing.")
        return None

    # Handle attachment
    filename = 'car.jpg'
    try:
        with open(filename, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={filename}')
        message.attach(part)
    except FileNotFoundError:
        logging.error(f"File {filename} not found.")
        print(f"Error: The file {filename} was not found.")
        return None

    # Encode the message to be sent
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

def send_message(service, sender, to, subject):
    """Send an email message."""
    if not is_valid_email(sender):
        logging.error(f"Invalid sender email: {sender}")
        print("Error: Invalid sender email.")
        return
    
    if not is_valid_email(to):
        logging.error(f"Invalid recipient email: {to}")
        print("Error: Invalid recipient email.")
        return

    message = create_message(sender, to, subject, '')
    if message is None:
        return  # Early exit if the message creation failed
    
    try:
        sent_message = service.users().messages().send(userId="me", body=message).execute()
        logging.info(f"Message sent: {sent_message['id']}")
        print(f"Message sent: {sent_message['id']}")
    except Exception as error:
        logging.error(f"An error occurred: {error}")
        print(f"An error occurred: {error}")

# Authenticate with Gmail and send email
if __name__ == '__main__':
    service = authenticate_gmail()
    
    sender = "testingmaliclient6819@gmail.com"
    recipient = "danraj23@gmail.com"
    subject = "Testing Python Mail Client"

    send_message(service, sender, recipient, subject)
