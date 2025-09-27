import os
import time
import requests
from abc import ABC, abstractmethod
from typing import Optional
from dotenv import load_dotenv
import logging

load_dotenv()

class TTSProvider(ABC):
    """Abstract base class for TTS providers"""

    @abstractmethod
    def generate_speech(self, voice: str, instructions: str, input_text: str,
                       folder: str, chunk_index: int, chunk_id: str) -> str:
        """
        Generate speech from text and save to filesystem

        Args:
            mode: TTS mode/model to use
            instructions: Voice instructions/tone
            input_text: Text to convert to speech
            folder: Output folder path
            chunk_index: Index of the chunk for filename
            chunk_id: Unique chunk identifier for filename

        Returns:
            str: Path to the generated audio file
        """
        pass


class OpenAiTTSProvider(TTSProvider):
    """OpenAI TTS provider implementation"""

    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _create_output_directory(self, folder: str) -> None:
        """Create output directory if it doesn't exist"""
        os.makedirs(folder, exist_ok=True)

    def _generate_filename(self, chunk_index: int, chunk_id: str) -> str:
        """Generate standardized filename"""
        return f"{chunk_index:03d}_{chunk_id}.wav"

    def _make_tts_request(self, voice: str, instructions: str, input_text: str) -> requests.Response:
        """Make TTS API request to OpenAI"""
        url = f"{self.base_url}/audio/speech"

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

        data = {
            "model": "gpt-4o-mini-tts",
            "voice": voice,
            "instructions": instructions,
            "input": input_text,
            "response_format": "wav"
        }

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response

    def _standardize_audio_format(self, audio_data: bytes) -> bytes:
        """
        Standardize audio format (placeholder for future audio processing)
        Currently returns audio as-is, but can be extended for:
        - Sample rate normalization
        - Volume normalization
        - Format conversion
        """
        # TODO: Add audio processing with libraries like pydub if needed
        return audio_data

    def generate_speech(self, voice: str, instructions: str, input_text: str,
                       folder: str, chunk_index: int, chunk_id: str) -> str:
        """
        Generate speech using OpenAI TTS API with retry logic

        Returns:
            str: Path to the generated audio file
        """
        self._create_output_directory(folder)
        filename = self._generate_filename(chunk_index, chunk_id)
        file_path = os.path.join(folder, filename)

        last_exception = None

        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"Generating audio for chunk {chunk_index}_{chunk_id}, attempt {attempt + 1}")

                # Make API request
                response = self._make_tts_request(voice, instructions, input_text)

                # Standardize audio format
                audio_data = self._standardize_audio_format(response.content)

                # Save to filesystem
                with open(file_path, 'wb') as f:
                    f.write(audio_data)

                self.logger.info(f"Successfully generated audio: {file_path}")
                return file_path

            except requests.exceptions.HTTPError as e:
                last_exception = e
                if e.response.status_code == 429:  # Rate limit
                    wait_time = self.retry_delay * (2 ** attempt)
                    self.logger.warning(f"Rate limit hit for chunk {chunk_id}, waiting {wait_time}s")
                    time.sleep(wait_time)
                elif e.response.status_code >= 500:  # Server error
                    wait_time = self.retry_delay * (2 ** attempt)
                    self.logger.warning(f"Server error for chunk {chunk_id}, waiting {wait_time}s")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"HTTP error for chunk {chunk_id}: {e}")
                    break

            except requests.exceptions.RequestException as e:
                last_exception = e
                wait_time = self.retry_delay * (2 ** attempt)
                self.logger.warning(f"Request error for chunk {chunk_id}, waiting {wait_time}s: {e}")
                time.sleep(wait_time)

            except Exception as e:
                last_exception = e
                self.logger.error(f"Unexpected error for chunk {chunk_id}: {e}")
                break

        # All retries failed
        error_msg = f"Failed to generate audio for chunk {chunk_id} after {self.max_retries} attempts"
        if last_exception:
            error_msg += f": {str(last_exception)}"

        self.logger.error(error_msg)
        raise Exception(error_msg)