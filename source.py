from dataclasses import fields
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
from dotenv import load_dotenv

load_dotenv()

cred = credentials.ApplicationDefault()

firebase_admin.initialize_app(cred, {
    'projectId': os.environ['GCP_PROJECT_ID']
})

db = firestore.client()

doc_ref = db.collection('users').document(os.environ['USER'])

artist_uris = doc_ref.get(field_paths = ['artists_uri']).to_dict()