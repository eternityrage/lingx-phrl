"""
YouTube Upload Script - Lingexa Phrasal
"""

import os
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

load_dotenv()

CHANNEL_NAME = "Lingexa Phrasal"

def get_authenticated_service():
    client_id = (os.getenv('YOUTUBE_CLIENT_ID') or os.getenv('YT_CLIENT_ID', '')).strip()
    client_secret = (os.getenv('YOUTUBE_CLIENT_SECRET') or os.getenv('YT_CLIENT_SECRET', '')).strip()
    refresh_token = (os.getenv('YOUTUBE_REFRESH_TOKEN') or os.getenv('YT_REFRESH_TOKEN', '')).strip()
    if not all([client_id, client_secret, refresh_token]):
        raise ValueError("Missing YouTube credentials!")
    creds = Credentials(None, refresh_token=refresh_token, token_uri="https://oauth2.googleapis.com/token", client_id=client_id, client_secret=client_secret, scopes=["https://www.googleapis.com/auth/youtube"])
    creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)

def generate_video_metadata(words_data, reel_data=None):
    if not words_data:
        return f"Phrasal Verbs - {CHANNEL_NAME}", f"Master phrasal verbs with {CHANNEL_NAME}!", ["phrasal verbs", "english grammar", CHANNEL_NAME.replace(' ', '')]
    first_words = [w.get("word", "") for w in words_data[:3]]
    words_count = len(words_data)
    title = f"Learn {words_count} Phrasal Verbs - {', '.join(first_words)} | English Grammar"
    lines = [f"📚 Master {words_count} English phrasal verbs with {CHANNEL_NAME}!", f"", f"=== TODAY'S PHRASAL VERBS ===", f""]
    for i, w in enumerate(words_data, 1):
        word = w.get("word", "")
        definition = w.get("definition", "")
        example = w.get("example", "")
        synonyms = w.get("synonyms", [])
        fun_fact = w.get("fun_fact", "")
        lines.append(f"{i}. {word}")
        lines.append(f"   Definition: {definition}")
        lines.append(f"   Example: {example}")
        if synonyms:
            lines.append(f"   Similar: {', '.join(synonyms[:3])}")
        if fun_fact:
            lines.append(f"   💡 Tip: {fun_fact}")
        lines.append(f"")
    lines.extend([f"=== ABOUT {CHANNEL_NAME.upper()} ===", f"", f"Master English phrasal verbs every day!", f"🔔 Subscribe for daily lessons!", f"", f"=== HASHTAGS ===", f"#LingexaPhrasal #PhrasalVerbs #EnglishGrammar #LearnEnglish #EnglishVocabulary #ESL #EnglishTips #Grammar #Shorts"])
    return title, "\n".join(lines), ["phrasal verbs", "english grammar", "learn english", "english vocabulary", "phrasal verbs list", "esl", "english tips", CHANNEL_NAME.replace(' ', '').lower()] + [w.get("word", "").lower() for w in words_data[:5]]

def upload_to_youtube(video_path, title, description, tags=None, category_id='27'):
    if tags is None:
        tags = ['phrasal verbs', 'english grammar', CHANNEL_NAME.replace(' ', '').lower()]
    youtube = get_authenticated_service()
    body = {'snippet': {'title': title, 'description': description, 'tags': tags, 'categoryId': category_id}, 'status': {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False}}
    media = MediaFileUpload(video_path, chunksize=1024*1024, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
    video_id = response.get('id')
    print(f"[youtube] Uploaded! Video ID: {video_id}")
    return {"status": "success", "video_id": video_id, "title": title}
