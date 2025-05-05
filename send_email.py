import os, base64, mimetypes
from mailjet_rest import Client
from dotenv import load_dotenv
from flask import current_app

load_dotenv()

def send_email(recipient: str, file_paths: list[str]):
    mailjet = Client(auth=(os.getenv("MJ_APIKEY_PUBLIC"), os.getenv("MJ_APIKEY_SECRET")), version="v3.1")

    attachments = []
    for rel_path in file_paths:
        full_path = os.path.join(current_app.static_folder, rel_path)
        with open(full_path, 'rb') as f:
            encoded = base64.b64encode(f.read()).decode()
        attachments.append({
            "ContentType": mimetypes.guess_type(full_path)[0] or "application/octet-stream",
            "Filename": os.path.basename(full_path),
            "Base64Content": encoded
        })

    data = {
        'Messages': [
            {
                "From": {
                    "Email": "dylannguyen2331@gmail.com",
                    "Name": "ByteMarket"
                },
                "To": [
                    {
                        "Email": recipient,
                        "Name": recipient
                    }
                ],
                "Subject": "Thank you for your purchase at ByteMarket!",
                "TextPart": "Thank you for sure purchase. Attached are your files!",
                "Attachments": attachments
            }
        ]
    }

    result = mailjet.send.create(data=data)
    print(result.status_code)
    print(result.json())