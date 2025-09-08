import os
import requests
from abc import ABC, abstractmethod
from dotenv import load_dotenv
from models.api_models import PooledResponse
import time

load_dotenv()

class LLMProvider(ABC):
    def __init__(self, baseurl: str, token: str):
        self.baseurl = baseurl
        self.token = token

    
    @abstractmethod
    def initiateResponse(self, input_text: str, instructions: str = "", model: str = "gpt-3.5-turbo") -> str:
        """
        Initiate an LLM response request.
        
        Args:
            input_text: The input text to process
            instructions: Instructions for the LLM
            model: Model to use
        
        Returns:
            str: Response ID from the provider
        """
        pass
    
    @abstractmethod
    def getPooledResponse(self, response_id: str) -> PooledResponse:
        """
        Get the response for a given response ID.
        
        Args:
            response_id: The response ID returned by initiateResponse
        
        Returns:
            PooledResponse: Response data from the provider
        """
        pass

from typing import Tuple

class OpenAiLLMProvider(LLMProvider):
    def __init__(self, token: str = '', baseurl: str = ''):
        super().__init__(
            baseurl or os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1'),
            token or os.getenv('OPENAI_API_KEY') or ""
        )
    
    def initiateResponse(self, input_text: str, instructions: str = "", model: str = "gpt-5-nano") -> str:
        payload = {
            "background": True,
            "model": model,
            "input": input_text
        }
        
        if instructions:
            payload["instructions"] = instructions
        
        response = requests.post(
            f"{self.baseurl}/responses",
            json=payload,
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("id", "")
        else:
            raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
    
    def getPooledResponse(self, response_id: str) -> PooledResponse:
        isCompleted = False
        attempts = 30
        while isCompleted != True and attempts > 0:
            attempts -= 1
            response = requests.get(
            f"{self.baseurl}/responses/{response_id}",
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=30)
            response = PooledResponse(**response.json())
            if response.status == "completed":
                isCompleted = True
                return response
            time.sleep(5)
        raise Exception("OpenAI API error: Response not completed in time")



class LocalLLMProvider(LLMProvider):
    def __init__(self, baseurl: str = "http://localhost:8000", token: str = ""):
        super().__init__(baseurl, token)
    
    def initiateResponse(self, input_text: str, instructions: str = "", model: str = "local-model") -> str:
        payload = {
            "input": input_text,
            "background": True
        }
        
        if instructions:
            payload["instructions"] = instructions
        if model != "local-model":
            payload["model"] = model
        
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        response = requests.post(
            f"{self.baseurl}/generate",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("id", "")
        else:
            raise Exception(f"Local API error: {response.status_code} - {response.text}")
    
    def getPooledResponse(self, response_id: str) -> PooledResponse:
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        response = requests.get(
            f"{self.baseurl}/responses/{response_id}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Local API error: {response.status_code} - {response.text}")
