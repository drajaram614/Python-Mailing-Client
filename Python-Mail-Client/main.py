import os  #interacting with the operating system such as checking files.
import base64  #encoding messages so that Gmail can understand.
import json  # working with JSON data for Google API responses.
import re  # handle regular expressions to check email format.
import logging  # for logging errors and debugging.
from google.oauth2.credentials import Credentials  # for OAuth2 credentials.
from google_auth_oauthlib.flow import InstalledAppFlow  # OAuth flow to get user permissions.
from google.auth.transport.requests import Request  # for sending requests during the OAuth process.
from googleapiclient.discovery import build  # builds the service for interacting with Gmail.
from email.mime.text import MIMEText  # creating email messages with plain text.
from email.mime.multipart import MIMEMultipart  # create multi-part messages (like attachments).
from email.mime.base import MIMEBase  # adding attachments.
from email import encoders  # encode attachments.
from bleach import clean  # HTML sanitization to keep our emails safe.

# scopes for Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.send']  # This tells Google what permissions we need.

# Configure logging
logging.basicConfig(level=logging.INFO, filename='email_client.log', format='%(asctime)s - %(levelname)s - %(message)s')  # Set up logging format and file.

def is_valid_email(email):
    """Validating email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'  # Regex pattern to check if the email looks good.
    return re.match(pattern, email) is not None  # If the email matches the pattern, it's valid; otherwise, it's not.

def contains_malicious_content(message_text):
    """Check for potentially malicious links or attachments in the email message."""
    malicious_patterns = [
        r'(https?://[^\s]+)',  # This looks for links.
        r'(?i)\b(?:exec|eval|system|shell|os\.system|subprocess|popen|import|open|os\.environ)\b'  # checks for dangerous functions.
    ]
    for pattern in malicious_patterns:  # go through each pattern.
        if re.search(pattern, message_text):  # if we find any match
            logging.warning("Malicious content detected in the message.")  # then log warning about it.
            return True  # return True if anything's suspicious.
    return False  # if nothing bad was found, return False.

def authenticate_gmail():
    """Authenticates user using OAuth2, returns Gmail API service."""
    creds = None  # Start with no credentials.

    # Checking if token.json file exists, which stores user credentials
    if os.path.exists('token.json'):  # If we already have a token file
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)  # then load the credentials from it.

    # if there are no valid credentials, go through the OAuth flow
    if not creds or not creds.valid:  # If there is no creds or they're invalid
        if creds and creds.expired and creds.refresh_token:  # if expired, refresh them...
            creds.refresh(Request())  # refresh credentials.
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)  # set up flow for OAuth.
            creds = flow.run_local_server(port=0)  # run the local server for user authentication.
        # Save the credentials for the next run
        with open('token.json', 'w') as token:  # Open token.json to write the new creds.
            token.write(creds.to_json())  # Saving credentials in JSON format.

    service = build('gmail', 'v1', credentials=creds)  # Create the Gmail API service.
    return service  #return service to use later.

def create_message(sender, to, subject, message_text):
    """Creating message for an email."""
    message = MIMEMultipart()  # Create multi-part email message.
    message['From'] = sender  # sender's email.
    message['To'] = to  # recipient's email.
    message['Subject'] = subject  # email subject.

    # Reading the email body from a file
    try:
        with open('message.txt', 'r') as f:  # Try to open the message.txt file to read the email body.
            body = f.read()  # Read contents of the file.
            # Sanitize HTML content
            body = clean(body, tags=['b', 'i', 'u', 'a'], strip=True)  # Use bleach to clean HTML and allow only certain tags.
            if contains_malicious_content(body):  # Check if the cleaned body has any bad stuff.
                logging.error("Email body contains potentially malicious content.")  # if so, then Log error.
                print("Error: Email body contains potentially malicious content.")  # Print error message.
                return None  # Exit if there's a problem.
        message.attach(MIMEText(body, 'html'))  # Attach the body as HTML to the email.
    except FileNotFoundError:  # If can't find the message.txt file
        logging.error("The message.txt file was not found.")  # then log the error.
        print("Error: The message body file is missing.")  # print error message.
        return None  #exit

    # Handle attachments
    filename = 'car.jpg'  # file to attach.
    try:
        with open(filename, 'rb') as attachment:  # try to open the attachment file in binary mode.
            part = MIMEBase('application', 'octet-stream')  # Create a base MIME part for the attachment.
            part.set_payload(attachment.read())  # Read the attachment file content.
        encoders.encode_base64(part)  # Encode the part to base64 to make it safe for email.
        part.add_header('Content-Disposition', f'attachment; filename={filename}')  # Add header to tell the email client it’s an attachment.
        message.attach(part)  # Attach encoded file to email.
    except FileNotFoundError:  # If the attachment isn't found
        logging.error(f"File {filename} not found.")  # then log error.
        print(f"Error: The file {filename} was not found.")  # Print error message.
        return None  #exit

    # Encode message to be sent
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()  # Convert message to a base64 string to send via Gmail.
    return {'raw': raw_message}  # Return encoded message as a dictionary.

def send_message(service, sender, to, subject):
    """Send email message."""
    if not is_valid_email(sender):  # Check the sender's email is valid.
        logging.error(f"Invalid sender email: {sender}")  # Log error if it's not valid.
        print("Error: Invalid sender email.")  # Print error message.
        return  #exit

    if not is_valid_email(to):  # check the recipient's email is valid.
        logging.error(f"Invalid recipient email: {to}")  # Log error if it's not valid.
        print("Error: Invalid recipient email.")  # Print error message
        return  # exit

    message = create_message(sender, to, subject, '')  #create  email message using the provided details.
    if message is None:  # If message creation failed
        return  #then exit
    
    try:
        sent_message = service.users().messages().send(userId="me", body=message).execute()  # Send message via the Gmail API.
        logging.info(f"Message sent: {sent_message['id']}")  # Log the sent message ID.
        print(f"Message sent: {sent_message['id']}")  # Print the sent message ID.
    except Exception as error:  # If there's an error during sending
        logging.error(f"An error occurred: {error}")  # then log error.
        print(f"An error occurred: {error}")  # Print error message.

# Authenticate with Gmail and send email
if __name__ == '__main__':  #checks if this script is being run directly (not imported).
    service = authenticate_gmail()  #authenticate and get the Gmail API service.
    
    sender = "testingmaliclient6819@gmail.com"  #set the sender's email.
    recipient = "danraj23@gmail.com"  #set the recipient's email.
    subject = "Testing Python Mail Client"  #set the subject of the email.

    send_message(service, sender, recipient, subject)  #call the function to send the email.
