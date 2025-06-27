from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
import json

SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive'
]

def main():
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)

    # Save the credentials to token.json
    with open('token.json', 'w') as token_file:
        token_file.write(creds.to_json())
    print("✅ Auth complete. New token.json saved with correct scopes.")

if __name__ == '__main__':
    main()
