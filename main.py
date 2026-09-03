import os
from fastapi import FastAPI, HTTPException
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
)
from youtube_transcript_api.proxies import WebshareProxyConfig

app = FastAPI(title="YouTube Transcript Extractor Microservice")

WEBSHARE_USERNAME = os.environ.get("WEBSHARE_PROXY_USERNAME")
WEBSHARE_PASSWORD = os.environ.get("WEBSHARE_PROXY_PASSWORD")

def get_api_client():
    if WEBSHARE_USERNAME and WEBSHARE_PASSWORD:
        return YouTubeTranscriptApi(
            proxy_config=WebshareProxyConfig(
                proxy_username=WEBSHARE_USERNAME,
                proxy_password=WEBSHARE_PASSWORD,
            )
        )
    return YouTubeTranscriptApi()

@app.get("/transcript/{video_id}")
def get_transcript(video_id: str):
    if not video_id or len(video_id) != 11:
        raise HTTPException(status_code=400, detail="Invalid YouTube Video ID format.")

    try:
        client = get_api_client()
        transcript_list = client.list(video_id)

        try:
            transcript = transcript_list.find_manually_created_transcript(['en'])
        except NoTranscriptFound:
            transcript = transcript_list.find_generated_transcript(['en'])

        full_data = transcript.fetch()
        merged_text = " ".join([snippet.text for snippet in full_data])

        return {
            "video_id": video_id,
            "character_count": len(merged_text),
            "transcript": merged_text,
        }

    except TranscriptsDisabled:
        raise HTTPException(status_code=404, detail="Transcripts are disabled for this video.")
    except NoTranscriptFound:
        raise HTTPException(status_code=404, detail="No English transcripts found for this video.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected transcription error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
