import langchain
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from elevenlabs import ElevenLabs
from fastapi import HTTPException
import os 
import fal_client
from dotenv import load_dotenv
import asyncio
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
FALAI_API_KEY = os.getenv("FALAI_API_KEY")

fal_client.api_key = "FALAI_API_KEY"





@tool(name_or_callable="video_generator")
def video_generator(text: str, voice_id:str="nXIYu9FT5meibkBbZFT7", format:str="mp3_44100_128"):
    """Convert text to speech using ElevenLabs and generate a talking-head video
    using the FAL OmniHuman model.
    
    Args:
        text (str): Text to synthesize.
        voice_id (str, optional): ElevenLabs voice ID.
        format (str, optional): Audio output format.

    Returns:
        dict: Generated video URL and execution logs.
        """
    client = ElevenLabs(
        api_key=ELEVENLABS_API_KEY,
        base_url="https://api.elevenlabs.io/",
    )

    response = client.text_to_speech.convert(
        voice_id=voice_id,
        model_id="eleven_multilingual_v2",
        output_format=format,
        text=text,
    )
    audio_bytes = b"".join(response)
    try:
        handler = fal_client.subscribe(
            "fal-ai/bytedance/omnihuman/v1.5",
            arguments={
                "image_url": "https://etimg.etb2bimg.com/photo/101664286.cms",
                "audio_url": audio_bytes,
                "duration": 5
            },
        )

        

        result =  handler.get()
        video_url = result.get("video", {}).get("url")

        if not video_url:
            raise HTTPException(status_code=500, detail="Video URL not found in FAL API response")

        return {"video": {"url": video_url}}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")




    

