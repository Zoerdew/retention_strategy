import os
import json
import datetime
from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- Flask setup ---
app = Flask(__name__)

# --- Load credentials from env variable ---
SCOPES = ['https://www.googleapis.com/auth/drive']
service_account_info = json.loads(os.environ["SERVICE_ACCOUNT_JSON"])
creds = service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)

# --- Google Drive + Docs setup ---
DRIVE = build('drive', 'v3', credentials=creds)
DOCS = build('docs', 'v1', credentials=creds)

TEMPLATE_ID = '1vO4MGHF_q4ATTE0Qe4snCuGALmBUgJdmiZjmiQQqlFc'  # Your template doc ID
FOLDER_ID = '1m0E2RqE0U9TbEvLYDLN2KzLzy1Th93_C'                # Your target folder ID

@app.route('/trigger', methods=['POST'])
def generate_strategy_doc():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    customer_name = data.get("customer_name", "Unnamed")
    title = f"{customer_name} | Loyalty & Retention Strategy"

    # Step 1: Copy the template
    copied_file = DRIVE.files().copy(
        fileId=TEMPLATE_ID,
        body={
            'name': title,
            'parents': [FOLDER_ID]
        }
    ).execute()

    document_id = copied_file.get('id')

    # Step 2: Format replacement requests
    requests = []
    for key, value in data.items():
        placeholder = f"{{{{{key}}}}}"  # double curly braces
        requests.append({
            'replaceAllText': {
                'containsText': {
                    'text': placeholder,
                    'matchCase': True
                },
                'replaceText': value
            }
        })

    # Step 3: Apply replacements
    if requests:
        DOCS.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}
        ).execute()

    return jsonify({
        "message": "Document created successfully.",
        "document_id": document_id,
        "document_url": f"https://docs.google.com/document/d/{document_id}/edit"
    })

if __name__ == '__main__':
    app.run(debug=True)
