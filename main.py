from flask import Flask, request, jsonify
import json
import google.auth
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from googleapiclient.errors import HttpError

app = Flask(__name__)

# Google Drive and Docs setup
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/documents']
SERVICE_ACCOUNT_FILE = 'service_account.json'

TEMPLATE_DOCUMENT_ID = '1vO4MGHF_q4ATTE0Qe4snCuGALmBUgJdmiZjmiQQqlFc'
DESTINATION_FOLDER_ID = '1m0E2RqE0U9TbEvLYDLN2KzLzy1Th93_C'

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
docs_service = build('docs', 'v1', credentials=creds)
drive_service = build('drive', 'v3', credentials=creds)

@app.route('/trigger', methods=['POST'])
def trigger():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Missing JSON data'}), 400

    try:
        # Copy template
        copied_file = drive_service.files().copy(
            fileId=TEMPLATE_DOCUMENT_ID,
            body={
                'name': f"Loyalty Strategy – {data.get('primary_loyalty_style', 'Untitled')}",
                'parents': [DESTINATION_FOLDER_ID]
            }
        ).execute()

        document_id = copied_file['id']

        # Replace placeholders
        requests = []
        for placeholder, value in data.items():
            requests.append({
                'replaceAllText': {
                    'containsText': {
                        'text': f"{{{{{placeholder}}}}}",
                        'matchCase': True
                    },
                    'replaceText': value
                }
            })

        docs_service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}
        ).execute()

        doc_link = f"https://docs.google.com/document/d/{document_id}/edit"
        return jsonify({'status': 'success', 'doc_link': doc_link})

    except HttpError as error:
        return jsonify({'error': f"❌ Google API error: {error}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
