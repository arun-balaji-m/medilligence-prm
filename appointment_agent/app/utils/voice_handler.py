import os
import httpx
from typing import Optional

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")


class VoiceHandler:
    def __init__(self):
        self.current_transcript = ""
        self.is_processing = False

    async def text_to_speech(self, text: str) -> Optional[bytes]:
        """Convert text to speech using ElevenLabs"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
                    headers={
                        "xi-api-key": ELEVENLABS_API_KEY,
                        "Content-Type": "application/json",
                        "Accept": "audio/mpeg"
                    },
                    json={
                        "text": text,
                        "model_id": "eleven_turbo_v2_5",
                        "voice_settings": {
                            "stability": 0.5,
                            "similarity_boost": 0.75,
                            "use_speaker_boost": True
                        }
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    return response.content
                return None

        except Exception as e:
            print(f"[VoiceHandler] ElevenLabs error: {e}")
            return None
