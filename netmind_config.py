import os
import requests
from typing import Optional, Dict, Any
from openai import OpenAI, AsyncOpenAI

class NetMindConfig:
    """
    NetMind API configuration class for managing NetMind inference API connections and settings
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('NETMIND_API_KEY')
        if not self.api_key:
            raise ValueError("NetMind API key is required. Please set NETMIND_API_KEY environment variable or pass api_key parameter.")
        self.base_url = "https://api.netmind.ai/inference-api/openai/v1"
        self.model_name = "openai/gpt-oss-20b"
        self.tts_model = "ResembleAI/Chatterbox"  # NetMind TTS model
        
    def get_headers(self) -> Dict[str, str]:
        """
        Get NetMind API request headers
        """
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def chat_completion(self, messages: list, **kwargs) -> Dict[str, Any]:
        """
        Call NetMind chat completion API
        """
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model_name,
            "messages": messages,
            **kwargs
        }
        
        response = requests.post(url, headers=self.get_headers(), json=payload, timeout=60)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")
    
    def get_model_name(self) -> str:
        """
        Return NetMind supported model name
        """
        return self.model_name
    
    def get_tts_model(self) -> str:
        """
        Get TTS model name
        """
        return self.tts_model
    


# Global NetMind configuration instance - will be initialized when API key is provided
netmind_config = None

# Setup default NetMind API configuration
def setup_netmind_api(api_key: Optional[str] = None):
    """
    Setup NetMind API configuration
    """
    global netmind_config
    netmind_config = NetMindConfig(api_key)
    return netmind_config

# Convenience function to get NetMind configuration
def get_netmind_config() -> NetMindConfig:
    """
    Get configured NetMind configuration instance
    """
    if netmind_config is None:
        raise ValueError("NetMind API not configured. Please call setup_netmind_api() first.")
    return netmind_config

# Convenience function to get NetMind model
def get_netmind_model():
    """
    Get configured AsyncOpenAI client for agents library
    """
    if netmind_config is None:
        raise ValueError("NetMind API not configured. Please call setup_netmind_api() first.")
    return AsyncOpenAI(
        base_url=netmind_config.base_url,
        api_key=netmind_config.api_key
    )

def get_netmind_model_name() -> str:
    """
    Get NetMind model name string
    """
    if netmind_config is None:
        raise ValueError("NetMind API not configured. Please call setup_netmind_api() first.")
    return netmind_config.get_model_name()

def get_netmind_tts_model() -> str:
    """
    Get NetMind TTS model name
    """
    if netmind_config is None:
        raise ValueError("NetMind API not configured. Please call setup_netmind_api() first.")
    return netmind_config.get_tts_model()

class TTSError(Exception):
    """Base exception for TTS operations"""
    pass

class TTSConnectionError(TTSError):
    """Network connection issues"""
    pass

class TTSTimeoutError(TTSError):
    """Request timeout issues"""
    pass

class TTSAPIError(TTSError):
    """API response errors"""
    pass

class TTSQuotaError(TTSError):
    """API quota exceeded"""
    pass

def create_tts_audio(text, api_key=None, progress_callback=None):
    """
    Create TTS audio using NetMind API with robust error handling
    Implements retry mechanism and optimized network configuration to resolve timeout issues
    
    Args:
        text (str): Text to convert to speech
        api_key (str, optional): NetMind API key
        progress_callback (callable, optional): Optional callback for progress updates
    
    Returns:
        bytes: Audio content in MP3 format
    
    Raises:
        TTSConnectionError: Network connection issues
        TTSTimeoutError: Request timeout issues
        TTSAPIError: API response errors
        TTSQuotaError: API quota exceeded
        TTSError: General TTS operation failures
    """
    import time
    import logging
    import json
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    from requests.exceptions import (
        ConnectionError, 
        Timeout, 
        RequestException, 
        HTTPError,
        TooManyRedirects
    )
    
    # Configure logging for TTS operations
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    config = netmind_config if api_key is None else NetMindConfig(api_key)
    
    # Use API endpoint from official documentation
    url = "https://api.netmind.ai/inference-api/openai/v1/audio/speech"
    
    payload = {
        "model": config.get_tts_model(),
        "input": text
    }
    
    headers = {
        'Authorization': f'Bearer {config.api_key}',
        'Connection': 'keep-alive'
    }
    
    # Create session and configure retry strategy
    session = requests.Session()
    
    # Enhanced retry strategy with exponential backoff and jitter
    retry_strategy = Retry(
        total=5,  # Increased retry attempts
        backoff_factor=2,  # Exponential backoff: 2, 4, 8, 16 seconds
        status_forcelist=[429, 500, 502, 503, 504, 520, 521, 522, 523, 524],
        allowed_methods=["POST", "GET"],  # Allow retries for POST requests
        raise_on_status=False,  # Don't raise on HTTP errors, handle manually
        respect_retry_after_header=True  # Respect server's retry-after header
    )
    
    # Create adapter with optimized connection pooling
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,  # Connection pool size
        pool_maxsize=20,     # Max connections in pool
        pool_block=False     # Don't block when pool is full
    )
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Configure session-level timeouts
    session.timeout = (30, 300)  # (connect_timeout, read_timeout)
    
    # Try multiple times with enhanced retry mechanism
    max_attempts = 5  # Increased from 3 to 5
    
    last_error = None
    import random
    
    for attempt in range(1, max_attempts + 1):
        try:
            if progress_callback:
                progress_callback(f"TTS attempt {attempt}/{max_attempts}", (attempt-1) * 0.2)
            logger.info(f"TTS attempt {attempt}/{max_attempts}")
            
            # Add jitter to prevent thundering herd
            if attempt > 1:
                jitter = random.uniform(0.5, 1.5)
                base_delay = min(300, (2 ** (attempt - 2)) * 2)  # Cap at 5 minutes
                delay = base_delay * jitter
                logger.info(f"Waiting {delay:.1f}s before retry {attempt}")
                if progress_callback:
                    progress_callback(f"Waiting {int(delay)}s before retry...", (attempt-1) * 0.2 + 0.05)
                time.sleep(delay)
            
            # Send request with configured timeouts
            if progress_callback:
                progress_callback("Calling TTS API...", attempt * 0.2 + 0.1)
            logger.info("Sending TTS request to NetMind API")
            
            response = session.post(
                url, 
                headers=headers, 
                data=payload, 
                timeout=(30, 300),  # (connect_timeout, read_timeout)
                stream=False
            )
            
            if response.status_code == 200:
                # NetMind API returns JSON format containing download URL
                try:
                    import json
                    response_data = json.loads(response.text)
                    download_url = response_data.get('result_download_url')
                    
                    if download_url:
                        # Download actual audio file with progress tracking
                        if progress_callback:
                            progress_callback("Downloading audio file...", attempt * 0.2 + 0.15)
                        logger.info(f"Downloading audio from: {download_url[:50]}...")
                        
                        # Use longer timeout for file download
                        audio_response = session.get(
                            download_url, 
                            timeout=(30, 600),  # 10 minutes for large audio files
                            stream=True  # Stream download for large files
                        )
                        
                        if audio_response.status_code == 200:
                            # Collect audio content
                            audio_content = b''
                            total_size = int(audio_response.headers.get('content-length', 0))
                            downloaded = 0
                            
                            for chunk in audio_response.iter_content(chunk_size=8192):
                                if chunk:
                                    audio_content += chunk
                                    downloaded += len(chunk)
                                    
                                    # Update progress during download
                                    if total_size > 0 and progress_callback:
                                        download_progress = downloaded / total_size
                                        overall_progress = attempt * 0.2 + 0.15 + (download_progress * 0.05)
                                        progress_callback(f"Downloaded {downloaded//1024}KB/{total_size//1024}KB", overall_progress)
                            
                            if progress_callback:
                                progress_callback("Audio generation completed", 1.0)
                            logger.info(f"TTS generated successfully, audio size: {len(audio_content)} bytes")
                            session.close()
                            return audio_content
                        else:
                            last_error = f"Audio download failed: HTTP {audio_response.status_code} - {audio_response.reason}"
                            logger.warning(f"Attempt {attempt} failed: {last_error}")
                    else:
                        last_error = f"Download URL not found in API response: {response.text[:200]}..."
                        logger.warning(f"Attempt {attempt} failed: {last_error}")
                        
                except json.JSONDecodeError as e:
                    last_error = f"API response JSON parsing failed: {str(e)}"
                    logger.error(f"Attempt {attempt} failed: {last_error}")
                    logger.debug(f"Raw response: {response.text[:500]}...")
            else:
                last_error = f"TTS request failed: HTTP {response.status_code} - {response.reason}"
                logger.warning(f"Attempt {attempt} failed: {last_error}")
                logger.debug(f"Response headers: {dict(response.headers)}")
                logger.debug(f"Response body: {response.text[:500]}...")
                
        except Timeout as e:
            last_error = f"TTS request timeout (attempt {attempt}): {str(e)}"
            logger.warning(last_error)
            if attempt < max_attempts:
                time.sleep(2)  # Wait before retry
            else:
                raise TTSTimeoutError(f"TTS service timeout after {max_attempts} attempts: {str(e)}")
                
        except ConnectionError as e:
            last_error = f"TTS connection failed (attempt {attempt}): {str(e)}"
            logger.warning(last_error)
            if attempt < max_attempts:
                time.sleep(2)  # Wait before retry
            else:
                raise TTSConnectionError(f"Unable to connect to TTS service after {max_attempts} attempts: {str(e)}")
                
        except RequestException as e:
            last_error = f"TTS network request failed (attempt {attempt}): {str(e)}"
            logger.warning(last_error)
            if attempt < max_attempts:
                time.sleep(1)  # Wait before retry
            else:
                raise TTSError(f"TTS request failed after {max_attempts} attempts: {str(e)}")
    
    # All attempts failed
    session.close()
    
    # Determine appropriate exception type based on last error
    if "timeout" in str(last_error).lower():
        raise TTSTimeoutError(last_error or "TTS service timeout after multiple attempts")
    elif "connection" in str(last_error).lower():
        raise TTSConnectionError(last_error or "TTS connection failed after multiple attempts")
    elif "quota" in str(last_error).lower() or "429" in str(last_error):
        raise TTSQuotaError(last_error or "TTS API quota exceeded")
    elif any(code in str(last_error) for code in ["400", "401", "403", "404", "500", "502", "503"]):
        raise TTSAPIError(last_error or "TTS API error after multiple attempts")
    else:
        raise TTSError(last_error or "TTS service unavailable after multiple attempts")