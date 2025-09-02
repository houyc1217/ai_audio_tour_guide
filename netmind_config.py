import os
import requests
from typing import Optional, Dict, Any
from openai import OpenAI, AsyncOpenAI

class NetMindConfig:
    """
    NetMind API configuration class for managing NetMind inference API connections and settings
    """
    
    def __init__(self, api_key: Optional[str] = None):
        if not api_key:
            raise ValueError("NetMind API key is required")
        self.api_key = api_key
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
    


# Global NetMind configuration instance
netmind_config = NetMindConfig()

# Setup default NetMind API configuration
def setup_netmind_api(api_key: Optional[str] = None):
    """
    Setup NetMind API configuration
    """
    global netmind_config
    if api_key:
        netmind_config = NetMindConfig(api_key)
    
    return netmind_config

# Convenience function to get NetMind configuration
def get_netmind_config() -> NetMindConfig:
    """
    Get configured NetMind configuration instance
    """
    return netmind_config

# Convenience function to get NetMind model
def get_netmind_model():
    """
    Get configured AsyncOpenAI client for agents library
    """
    return AsyncOpenAI(
        base_url=netmind_config.base_url,
        api_key=netmind_config.api_key
    )

def get_netmind_model_name() -> str:
    """
    Get NetMind model name string
    """
    return netmind_config.get_model_name()

def get_netmind_tts_model() -> str:
    """
    Get NetMind TTS model name
    """
    return netmind_config.get_tts_model()

def create_tts_audio(text, api_key=None, progress_callback=None):
    """
    Create TTS audio using NetMind API
    Implements retry mechanism and optimized network configuration to resolve timeout issues
    """
    import time
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    
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
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Try multiple times with no timeout limit per attempt
    max_attempts = 3
    
    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            if progress_callback:
                progress_callback(f"TTS attempt {attempt}/{max_attempts} (no timeout limit)", (attempt-1) * 0.3)
            print(f"TTS attempt {attempt}/{max_attempts} (no timeout limit per attempt)")
            
            # 发送请求
            if progress_callback:
                progress_callback("Calling TTS API...", attempt * 0.3 + 0.1)
            response = session.post(
                url, 
                headers=headers, 
                data=payload, 
                timeout=None,  # No timeout limit - wait indefinitely
                stream=False
            )
            
            if response.status_code == 200:
                # NetMind API returns JSON format containing download URL
                try:
                    import json
                    response_data = json.loads(response.text)
                    download_url = response_data.get('result_download_url')
                    
                    if download_url:
                        # Download actual audio file
                        if progress_callback:
                            progress_callback("Downloading audio file...", attempt * 0.3 + 0.2)
                        print(f"Got download URL, downloading audio file...")
                        audio_response = session.get(download_url, timeout=None)  # No timeout limit
                        
                        if audio_response.status_code == 200:
                            if progress_callback:
                                progress_callback("Audio generation completed", 1.0)
                            print(f"TTS generated successfully, audio size: {len(audio_response.content)} bytes")
                            session.close()
                            return audio_response.content
                        else:
                            last_error = f"Audio download failed: {audio_response.status_code}"
                            print(f"Attempt {attempt} failed: {last_error}")
                    else:
                        last_error = f"Download URL not found in API response: {response.text}"
                        print(f"Attempt {attempt} failed: {last_error}")
                        
                except json.JSONDecodeError as e:
                    last_error = f"API response JSON parsing failed: {str(e)}"
                    print(f"Attempt {attempt} failed: {last_error}")
            else:
                last_error = f"TTS request failed: {response.status_code} - {response.text}"
                print(f"Attempt {attempt} failed: {last_error}")
                
        except requests.exceptions.Timeout as e:
            last_error = f"TTS request timeout (attempt {attempt}): {str(e)}"
            print(last_error)
            if attempt < max_attempts:
                time.sleep(2)  # Wait before retry
                
        except requests.exceptions.RequestException as e:
            last_error = f"TTS network request failed (attempt {attempt}): {str(e)}"
            print(last_error)
            if attempt < max_attempts:
                time.sleep(1)  # Wait before retry
    
    # All attempts failed
    session.close()
    raise Exception(last_error or "TTS service unavailable after multiple attempts")