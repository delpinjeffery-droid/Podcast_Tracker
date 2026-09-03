import os
from fastapi import FastAPI, HTTPException
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

app = FastAPI(title="YouTube Transcript Extractor Microservice")

@app.get("/transcript/{video_id}")
def get_transcript(video_id: str):
    """
    Fetches the plain-text English transcript for a given YouTube Video ID.
    """
    if not video_id or len(video_id) != 11:
        raise HTTPException(status_code=400, detail="Invalid YouTube Video ID format.")

    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        try:
            transcript = transcript_list.find_manually_created_transcript(['en'])
        except NoTranscriptFound:
            transcript = transcript_list.find_generated_transcript(['en'])

        full_data = transcript.fetch()
        merged_text = " ".join([entry['text'] for entry in full_data])

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
