import httpx
from ..config import settings
from typing import Optional
import asyncio


class VoiceService:
    # @staticmethod
    # async def transcribe_with_deepgram(audio_data: bytes) -> Optional[str]:
    #     """Send audio to Deepgram and get transcription"""
    #     try:
    #         async with httpx.AsyncClient() as client:
    #             response = await client.post(
    #                 "https://api.deepgram.com/v1/listen",
    #                 headers={
    #                     "Authorization": f"Token {settings.DEEPGRAM_API_KEY}",
    #                     "Content-Type": "audio/wav"
    #                 },
    #                 content=audio_data,
    #                 timeout=30.0
    #             )
    #
    #             if response.status_code == 200:
    #                 result = response.json()
    #                 transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
    #                 return transcript.strip()
    #             return None
    #     except Exception as e:
    #         print(f"Deepgram error: {e}")
    #         return None

    @staticmethod
    async def speak_with_elevenlabs(text: str) -> Optional[bytes]:
        """Convert text to speech with ElevenLabs"""
        try:
            print(f"ElevenLabs TTS - Text: '{text}'")

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{settings.ELEVENLABS_VOICE_ID}",
                    headers={
                        "xi-api-key": settings.ELEVENLABS_API_KEY,
                        "Content-Type": "application/json"
                    },
                    json={
                        "text": text,
                        "model_id": "eleven_turbo_v2_5",
                        "voice_settings": {
                            "stability": 0.5,
                            "similarity_boost": 0.75
                        }
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    audio_bytes = response.content
                    print(f"Successfully got {len(audio_bytes)} bytes from ElevenLabs")
                    return audio_bytes
                else:
                    print(f"ElevenLabs error: {response.status_code} - {response.text}")
                    return None

        except Exception as e:
            print(f"ElevenLabs exception: {e}")
            return None

