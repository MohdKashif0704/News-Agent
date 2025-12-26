import langchain
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from elevenlabs import ElevenLabs
from fastapi import HTTPException
import os 
import fal_client
from dotenv import load_dotenv
import tempfile

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
FALAI_API_KEY = os.getenv("FALAI_API_KEY")

fal_client.api_key = FALAI_API_KEY


@tool(name_or_callable="video_generator")
def video_generator(text: str):
    """Convert text to speech using ElevenLabs and generate a talking-head video
    
    Args:
        text (str): Text to synthesize.
        
    Returns:
        dict: Generated video URL .
    """
    
    
    client = ElevenLabs(
        api_key=ELEVENLABS_API_KEY,
        base_url="https://api.elevenlabs.io/",
    )

    response = client.text_to_speech.convert(
        voice_id="nXIYu9FT5meibkBbZFT7",
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
        text="Hello Kalix",
    )
    audio_bytes = b"".join(response)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        f.write(audio_bytes)
        audio_path = f.name
    audio_url = fal_client.upload_file(audio_path)
    try:
        result = fal_client.subscribe(
            "fal-ai/bytedance/omnihuman/v1.5",
            arguments={
                "image_url": "https://etimg.etb2bimg.com/photo/101664286.cms",
                "audio_url": audio_url,
                "duration": 5
            },
        )
        return {
        "video_url": result["video"]["url"]
    }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")
    finally:
       
        if "audio_path" in locals() and os.path.exists(audio_path):
            os.remove(audio_path)




    

