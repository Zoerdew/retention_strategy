import os
import sys
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Constants
TEMPLATE_DOCUMENT_ID = "1vO4MGHF_q4ATTE0Qe4snCuGALmBUgJdmiZjmiQQqlFc"
DESTINATION_FOLDER_ID = "1m0E2RqE0U9TbEvLYDLN2KzLzy1Th93_C"

# Scope required
SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']

def authenticate():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    else:
        print("❌ No token.json found. Please run the authentication flow again.")
        sys.exit(1)

    try:
        docs_service = build("docs", "v1", credentials=creds)
        drive_service = build("drive", "v3", credentials=creds)
        return docs_service, drive_service
    except Exception as e:
        print(f"❌ Failed to authenticate: {e}")
        sys.exit(1)

def copy_template(drive_service, name):
    copied_file = {
        'name': name,
        'parents': [DESTINATION_FOLDER_ID]
    }

    try:
        file = drive_service.files().copy(
            fileId=TEMPLATE_DOCUMENT_ID,
            body=copied_file
        ).execute()
        return file['id']
    except HttpError as error:
        print(f"❌ Error copying template: {error}")
        sys.exit(1)

def replace_placeholders(docs_service, document_id, replacements):
    requests = []

    for placeholder, replacement in replacements.items():
        requests.append({
            'replaceAllText': {
                'containsText': {
                    'text': f'{{{{{placeholder}}}}}',
                    'matchCase': True
                },
                'replaceText': replacement
            }
        })

    try:
        docs_service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}
        ).execute()
    except HttpError as error:
        print(f"❌ Error updating document: {error}")
        sys.exit(1)

def main():
    print("Paste the full document content with placeholder values as JSON (e.g., {'primary_loyalty_style': 'Claire is a Fixer...', ...})")
    print("Press Enter, then Ctrl+D (or Ctrl+Z on Windows) when done.\n")

    try:
        input_data = sys.stdin.read()
        replacements = json.loads(input_data)
    except Exception as e:
        print(f"❌ Failed to parse JSON input: {e}")
        sys.exit(1)

    docs_service, drive_service = authenticate()

    # Create filename for new doc
    name = f"Loyalty Strategy - {replacements.get('primary_loyalty_style', 'Untitled')[:30]}"
    new_doc_id = copy_template(drive_service, name)

    # Replace placeholders
    replace_placeholders(docs_service, new_doc_id, replacements)

    print(f"\n✅ Document created successfully: https://docs.google.com/document/d/{new_doc_id}/edit")

if __name__ == "__main__":
    main()
