# Load your env variables
from dotenv import load_dotenv
load_dotenv()
# Import your dependencies
import os
from nylas import APIClient

def send_mail(name, recipient_email, subject, message):
    # Initialize your Nylas API client
    nylas = APIClient(
        os.environ.get("CLIENT_ID"),
        os.environ.get("CLIENT_SECRET"),
        os.environ.get("ACCESS_TOKEN"),
    )
    # Draft your email
    draft = nylas.drafts.create()
    draft.subject = subject
    draft.body = message
    draft.to = [{"name": name, "email": recipient_email}]
    # Send your email!
    draft.send()
    
    
