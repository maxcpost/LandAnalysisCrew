#!/usr/bin/env python3
"""
LLM utility module that provides a standardized interface to the Llama model via Ollama.
This centralizes all LLM integration logic in one place for better maintainability.
"""

import os
import sys
import time
import requests
import json
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

# Import formatting utilities
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from src.utils.formatting import print_header, print_info, print_warning, print_error, print_success
from src.utils.system import check_ollama_installed, check_ollama_running, setup_ollama_model

class LlamaLLM:
    """
    A unified interface for interacting with Llama models via Ollama.
    This class ensures compatibility with CrewAI and provides multiple fallback mechanisms.
    """
    
    def __init__(
        self, 
        model_name: str = "llama3", 
        base_url: str = "http://localhost:11434",
        temperature: float = 0.7,
        timeout: int = 120,
        retry_count: int = 3,
        retry_delay: int = 2,
        verbose: bool = True
    ):
        """
        Initialize the LlamaLLM interface.
        
        Args:
            model_name: The name of the Llama model to use (without provider prefix)
            base_url: Base URL for the Ollama API
            temperature: Sampling temperature (0.0 to 1.0)
            timeout: Request timeout in seconds
            retry_count: Number of retries for failed requests
            retry_delay: Delay between retries in seconds
            verbose: Whether to print detailed information
        """
        self.model_name = model_name
        self.base_url = base_url.rstrip('/')
        self.temperature = temperature
        self.timeout = timeout
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.verbose = verbose
        
        # For langchain/crewai compatibility
        self.model = model_name
        
        if verbose:
            print_info(f"Initializing LlamaLLM with model={model_name}, temperature={temperature}")
        
        # Check if model is available
        self._verify_model_availability()
    
    def _verify_model_availability(self) -> bool:
        """Check if the model is available in Ollama and try to load it if not."""
        # Check Ollama installation
        if not check_ollama_installed():
            print_error("Ollama is not installed. Please install from https://ollama.com")
            return False
            
        # Check if Ollama service is running
        if not check_ollama_running():
            print_error("Ollama service is not running. Please start with 'ollama serve'")
            return False
        
        try:
            # Check if model is available
            response = requests.get(f"{self.base_url}/api/tags", timeout=self.timeout)
            if response.status_code != 200:
                print_error(f"Failed to get list of available models. Status: {response.status_code}")
                return False
                
            models = response.json().get("models", [])
            available_models = [model.get("name") for model in models]
            
            if self.model_name not in available_models:
                print_warning(f"Model '{self.model_name}' not found in available models")
                print_info(f"Available models: {', '.join(available_models)}")
                
                # Try to pull the model
                if self.verbose:
                    print_info(f"Attempting to pull model '{self.model_name}'...")
                
                pull_response = requests.post(
                    f"{self.base_url}/api/pull",
                    json={"name": self.model_name},
                    timeout=300  # Longer timeout for model pulling
                )
                
                if pull_response.status_code != 200:
                    print_error(f"Failed to pull model '{self.model_name}'. Status: {pull_response.status_code}")
                    return False
                
                print_success(f"Successfully pulled model '{self.model_name}'")
            else:
                if self.verbose:
                    print_success(f"Model '{self.model_name}' is available")
                
            return True
            
        except requests.exceptions.ConnectionError:
            print_error(f"Cannot connect to Ollama service at {self.base_url}")
            print_info("Make sure Ollama is running with 'ollama serve'")
            return False
        except Exception as e:
            print_error(f"Error verifying model availability: {str(e)}")
            return False
    
    def _direct_ollama_completion(
        self, 
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> Optional[str]:
        """
        Send a completion request directly to the Ollama API.
        This is the most direct method that bypasses LangChain/LiteLLM.
        
        Args:
            prompt: The user prompt to send to the model
            system_prompt: Optional system prompt to set context
            
        Returns:
            The model's response text or None if request failed
        """
        for attempt in range(self.retry_count):
            try:
                request_body = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "temperature": self.temperature,
                    "stream": False
                }
                
                if system_prompt:
                    request_body["system"] = system_prompt
                
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json=request_body,
                    timeout=self.timeout
                )
                
                if response.status_code != 200:
                    print_error(f"Ollama API error. Status: {response.status_code}")
                    if attempt < self.retry_count - 1:
                        print_info(f"Retrying ({attempt+2}/{self.retry_count})...")
                        time.sleep(self.retry_delay)
                        continue
                    return None
                
                result = response.json()
                return result.get("response", "")
                
            except requests.exceptions.Timeout:
                print_error(f"Request timed out after {self.timeout} seconds")
                if attempt < self.retry_count - 1:
                    print_info(f"Retrying ({attempt+2}/{self.retry_count})...")
                    time.sleep(self.retry_delay)
                    continue
                return None
                
            except Exception as e:
                print_error(f"Error during completion request: {str(e)}")
                if attempt < self.retry_count - 1:
                    print_info(f"Retrying ({attempt+2}/{self.retry_count})...")
                    time.sleep(self.retry_delay)
                    continue
                return None
                
        return None
    
    def _format_messages(self, messages: List[Dict[str, str]]) -> str:
        """
        Format a list of messages into a single prompt string.
        This is used for compatibility with the direct Ollama API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            
        Returns:
            A formatted prompt string
        """
        formatted_prompt = ""
        system_prompt = None
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                system_prompt = content
                continue
                
            if role == "assistant":
                formatted_prompt += f"Assistant: {content}\n\n"
            elif role == "user":
                formatted_prompt += f"User: {content}\n\n"
            else:
                formatted_prompt += f"{role.capitalize()}: {content}\n\n"
                
        # Add a final assistant prefix to prompt the model to respond
        formatted_prompt += "Assistant: "
        
        return formatted_prompt, system_prompt

    def _langchain_ollama_completion(self, prompt: str) -> Optional[str]:
        """
        Send a completion request using LangChain's OllamaLLM integration.
        This is a fallback method if direct API calls fail.
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            The model's response text or None if request failed
        """
        try:
            from langchain_ollama import OllamaLLM
            
            llm = OllamaLLM(
                model=self.model_name,
                base_url=self.base_url,
                temperature=self.temperature
            )
            
            return llm.invoke(prompt)
            
        except ImportError:
            print_error("langchain_ollama package not installed")
            print_info("Try installing with: pip install langchain-ollama")
            return None
            
        except Exception as e:
            print_error(f"Error using LangChain OllamaLLM: {str(e)}")
            return None
    
    def _litellm_ollama_completion(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """
        Send a completion request using LiteLLM's integration.
        This is another fallback method if other methods fail.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            The model's response text or None if request failed
        """
        try:
            import litellm
            
            # Set a dummy API key to satisfy LiteLLM's validation
            os.environ["OPENAI_API_KEY"] = "ollama-dummy-key"
            
            # Configure LiteLLM
            litellm.set_verbose = False
            
            # Use the ollama/ prefix required by LiteLLM
            response = litellm.completion(
                model=f"ollama/{self.model_name}",
                messages=messages,
                temperature=self.temperature,
                api_base=f"{self.base_url}"
            )
            
            return response.choices[0].message.content
            
        except ImportError:
            print_error("litellm package not installed")
            print_info("Try installing with: pip install litellm")
            return None
            
        except Exception as e:
            print_error(f"Error using LiteLLM for Ollama: {str(e)}")
            return None
    
    # Interface methods for different libraries
    
    def completion(self, **kwargs):
        """LiteLLM-compatible completion method."""
        messages = kwargs.get("messages", [])
        if not messages:
            return {"choices": [{"message": {"content": "No input provided"}}]}
        
        # Format messages for direct Ollama call
        formatted_prompt, system_prompt = self._format_messages(messages)
        
        # Try direct Ollama API first (most reliable)
        response = self._direct_ollama_completion(formatted_prompt, system_prompt)
        
        if response is not None:
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": response
                        }
                    }
                ]
            }
        
        # If direct call fails, try LangChain
        response = self._langchain_ollama_completion(formatted_prompt)
        
        if response is not None:
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": response
                        }
                    }
                ]
            }
            
        # If LangChain also fails, try LiteLLM
        response = self._litellm_ollama_completion(messages)
        
        if response is not None:
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": response
                        }
                    }
                ]
            }
            
        # If all methods fail, return an error message
        return {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Error: Unable to generate a response using any available method."
                    }
                }
            ]
        }
    
    def call(self, **kwargs):
        """CrewAI-compatible call method."""
        messages = kwargs.get("messages", [])
        
        if not messages:
            # If no messages provided, use prompt parameter if available
            prompt = kwargs.get("prompt", "")
            if prompt:
                messages = [{"role": "user", "content": prompt}]
            else:
                return "Error: No input provided"
        
        # Format messages for direct Ollama call
        formatted_prompt, system_prompt = self._format_messages(messages)
        
        # Try direct Ollama API first
        response = self._direct_ollama_completion(formatted_prompt, system_prompt)
        
        if response is not None:
            return response
            
        # Try LangChain next
        response = self._langchain_ollama_completion(formatted_prompt)
        
        if response is not None:
            return response
            
        # Try LiteLLM last
        response = self._litellm_ollama_completion(messages)
        
        if response is not None:
            return response
            
        # If all methods fail, return error message
        return "Error: Unable to generate a response using any available method."
    
    def invoke(self, prompt, **kwargs):
        """LangChain-compatible invoke method."""
        return self.call(prompt=prompt, **kwargs)
    
    def generate(self, prompts, **kwargs):
        """LangChain-compatible generate method."""
        responses = []
        for prompt in prompts:
            response = self.call(prompt=prompt, **kwargs)
            responses.append(response)
        return responses
    
    def __call__(self, prompt, **kwargs):
        """Make the class callable for compatibility with some frameworks."""
        return self.call(prompt=prompt, **kwargs)


class MockLLM:
    """
    Mock implementation of an LLM for testing without actual API calls.
    This mimics the interface of LlamaLLM but returns pre-defined responses.
    """
    
    def __init__(self, model_name="llama3", temperature=0.7):
        self.model_name = model_name
        self.temperature = temperature
        print_info(f"[MockLLM] Initialized with model={model_name}, temperature={temperature}")
        
        # For langchain/crewai compatibility
        self.model = model_name
    
    def completion(self, **kwargs):
        """Mock completion method that returns a pre-defined response."""
        messages = kwargs.get("messages", [])
        
        print_info(f"[MockLLM] Processing {len(messages)} messages")
        time.sleep(0.5)  # Simulate processing time
        
        # Extract the last message content to generate a relevant response
        last_message = messages[-1]['content'] if messages else ""
        topic = "property analysis"
        
        if "zoning" in last_message.lower():
            topic = "zoning"
        elif "utility" in last_message.lower() or "infrastructure" in last_message.lower():
            topic = "utilities"
        elif "environmental" in last_message.lower():
            topic = "environmental factors"
        
        # Return a mock response based on the topic
        content = self._get_mock_response(topic)
        
        return {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": content
                    }
                }
            ]
        }
    
    def call(self, **kwargs):
        """CrewAI-compatible call method."""
        messages = kwargs.get("messages", [])
        
        if not messages and "prompt" in kwargs:
            messages = [{"role": "user", "content": kwargs["prompt"]}]
        
        response = self.completion(messages=messages)
        return response["choices"][0]["message"]["content"]
    
    def invoke(self, prompt, **kwargs):
        """LangChain-compatible invoke method."""
        return self.call(prompt=prompt, **kwargs)
    
    def generate(self, prompts, **kwargs):
        """LangChain-compatible generate method."""
        responses = []
        for prompt in prompts:
            response = self.call(prompt=prompt, **kwargs)
            responses.append(response)
        return responses
    
    def __call__(self, prompt, **kwargs):
        """Make the class callable for compatibility with some frameworks."""
        return self.call(prompt=prompt, **kwargs)
    
    def _get_mock_response(self, topic):
        """Get a mock response based on the topic."""
        responses = {
            "property analysis": """
Based on my research, here's what I found about the property:

## Property Analysis Summary
- Currently zoned as Agricultural/Residential
- Approximately 100 acres of mostly flat, usable land
- Good access to utilities (water, electricity, gas)
- Located near growing suburban area with strong demographics
- Potential for residential development at 4-6 units per acre

## Development Potential
- Estimated capacity: 250-300 housing units
- Best use case: Mid-density townhomes or single-family homes
- ROI potential: 18-22% with proper development plan

## Challenges
- Sewer infrastructure needs extension
- Some rezoning may be required
- Stormwater management needed for parts of the property

Overall, this property shows excellent potential for residential development with strong market fundamentals and good physical characteristics.
""",
            "zoning": """
## Zoning Analysis

The property is currently zoned Agricultural/Residential (AR) which allows:
- Single-family homes on large lots (1+ acre)
- Agricultural uses
- Limited commercial farm-related activities

For higher-density development, a rezoning would be required to:
- Residential (R-2): Would allow 2-4 units per acre
- Residential (R-3): Would allow 4-8 units per acre
- PUD (Planned Unit Development): Flexible density with amenities

Based on the comprehensive plan and recent approvals in the area, rezoning has a reasonable chance of approval with proper planning. The municipality has indicated support for additional housing development in this growth corridor.

Timeline for rezoning process: approximately 4-6 months
Estimated cost for rezoning application and process: $15,000-25,000
""",
            "utilities": """
## Utility Infrastructure Assessment

Water: Public water available at the road with good pressure (65 PSI)
Electricity: 3-phase power available along main road
Natural Gas: Available on adjacent property, extension required (approximately 500 feet)
Sewer: Public sewer is 1.2 miles away, extension required or on-site system needed
Internet: High-speed fiber available with 1Gbps service
Stormwater: Several natural drainage swales exist but formal retention system needed

Critical infrastructure needs:
1. Sewer solution (est. cost $1.2-1.8M for extension)
2. Internal road network (est. cost $2.5-3.0M)
3. Stormwater management system (est. cost $800K-1.2M)

All utilities have sufficient capacity for a development of 300+ residential units.
""",
            "environmental factors": """
## Environmental Assessment

The property shows favorable environmental conditions:
- Not in a FEMA flood zone (Zone X - minimal flood hazard)
- No wetlands identified on main development area (small 3-acre wetland in SW corner)
- Soils are primarily well-draining sandy loam suitable for development
- No known contamination or hazardous conditions
- No endangered species habitat identified
- Phase I Environmental Site Assessment shows clean history

Recommendations:
1. Wetland delineation to confirm boundaries of potential wetland
2. Geotechnical investigation for foundation requirements
3. Standard Phase I ESA for lender requirements

Overall environmental risk profile: LOW
Development constraints from environmental factors: MINIMAL
"""
        }
        
        return responses.get(topic, responses["property analysis"])


class CrewAILlamaAdapter:
    """
    Adapter class to make our LlamaLLM fully compatible with CrewAI.
    This addresses the specific requirements CrewAI has for LLM integration.
    """
    
    def __init__(self, model_name="llama3", base_url="http://localhost:11434", temperature=0.7, verbose=True):
        # Initialize our real LLM implementation
        self.llm = LlamaLLM(
            model_name=model_name,
            base_url=base_url,
            temperature=temperature,
            verbose=verbose
        )
        
        # Properties required by CrewAI
        self.model = f"ollama/{model_name}"  # Use the prefixed model name for LiteLLM compatibility
        self.temperature = temperature
        
    def chat(self, messages):
        """LangChain/LiteLLM-compatible chat method."""
        try:
            return self.llm.call(messages=messages)
        except Exception as e:
            print_error(f"Error in CrewAI adapter chat method: {str(e)}")
            return "Error generating response. Please try again."
    
    def complete(self, prompt):
        """LangChain-compatible complete method."""
        try:
            return self.llm.call(prompt=prompt)
        except Exception as e:
            print_error(f"Error in CrewAI adapter complete method: {str(e)}")
            return "Error generating response. Please try again."
    
    def generate(self, prompts):
        """LangChain-compatible generate method."""
        responses = []
        for prompt in prompts:
            response = self.complete(prompt)
            responses.append(response)
        return responses
    
    def call(self, **kwargs):
        """CrewAI-compatible call method."""
        if "messages" in kwargs:
            return self.chat(kwargs["messages"])
        elif "prompt" in kwargs:
            return self.complete(kwargs["prompt"])
        else:
            return "Error: No valid input provided in call method."
    
    def invoke(self, prompt, **kwargs):
        """LangChain-compatible invoke method."""
        return self.complete(prompt)
    
    def completion(self, **kwargs):
        """LiteLLM-compatible completion method required by CrewAI."""
        messages = kwargs.get("messages", [])
        if "model" in kwargs:
            # This is a direct LiteLLM call with model specified - use prefixed model name
            model = kwargs["model"]
            if not model.startswith("ollama/"):
                model = f"ollama/{model.split('/')[-1]}"
                kwargs["model"] = model
        
        response = self.llm.call(messages=messages)
        
        # Format as LiteLLM response
        return {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": response
                    }
                }
            ]
        }
    
    def __call__(self, prompt, **kwargs):
        """Make the class callable."""
        return self.complete(prompt)


class CrewAIMockAdapter:
    """
    Adapter class to make our MockLLM fully compatible with CrewAI.
    This mimics the CrewAILlamaAdapter but uses the mock implementation.
    """
    
    def __init__(self, model_name="llama3", temperature=0.7):
        # Initialize our mock LLM
        self.llm = MockLLM(
            model_name=model_name,
            temperature=temperature
        )
        
        # Properties required by CrewAI
        self.model = f"ollama/{model_name}"  # Use the prefixed model name for LiteLLM compatibility
        self.temperature = temperature
    
    def chat(self, messages):
        """LangChain/LiteLLM-compatible chat method."""
        return self.llm.call(messages=messages)
    
    def complete(self, prompt):
        """LangChain-compatible complete method."""
        return self.llm.call(prompt=prompt)
    
    def generate(self, prompts):
        """LangChain-compatible generate method."""
        responses = []
        for prompt in prompts:
            response = self.complete(prompt)
            responses.append(response)
        return responses
    
    def call(self, **kwargs):
        """CrewAI-compatible call method."""
        if "messages" in kwargs:
            return self.chat(kwargs["messages"])
        elif "prompt" in kwargs:
            return self.complete(kwargs["prompt"])
        else:
            return "Error: No valid input provided in call method."
    
    def invoke(self, prompt, **kwargs):
        """LangChain-compatible invoke method."""
        return self.complete(prompt)
    
    def completion(self, **kwargs):
        """LiteLLM-compatible completion method required by CrewAI."""
        return self.llm.completion(**kwargs)
    
    def __call__(self, prompt, **kwargs):
        """Make the class callable."""
        return self.complete(prompt)


def setup_llm(use_mock=False, for_crewai=False, **kwargs):
    """
    Set up the language model based on environment variables or parameters.
    
    Args:
        use_mock: Whether to use the mock implementation
        for_crewai: Whether to return a CrewAI-compatible adapter
        **kwargs: Additional arguments to pass to the LLM constructor
        
    Returns:
        An instance of LlamaLLM, MockLLM, or a CrewAI adapter
    """
    # Check if mock mode is enabled via environment variable
    if os.getenv("USE_MOCK_LLM", "false").lower() == "true" or use_mock:
        print_info("Using mock LLM for testing")
        
        if for_crewai:
            return CrewAIMockAdapter(
                model_name=os.getenv("OLLAMA_MODEL", kwargs.get("model_name", "llama3")),
                temperature=float(os.getenv("CREW_TEMPERATURE", str(kwargs.get("temperature", 0.7))))
            )
        else:
            return MockLLM(
                model_name=os.getenv("OLLAMA_MODEL", kwargs.get("model_name", "llama3")),
                temperature=float(os.getenv("CREW_TEMPERATURE", str(kwargs.get("temperature", 0.7))))
            )
    
    # Set up the real LlamaLLM
    if for_crewai:
        return CrewAILlamaAdapter(
            model_name=os.getenv("OLLAMA_MODEL", kwargs.get("model_name", "llama3")),
            base_url=os.getenv("OLLAMA_API_BASE", kwargs.get("base_url", "http://localhost:11434")),
            temperature=float(os.getenv("CREW_TEMPERATURE", str(kwargs.get("temperature", 0.7)))),
            verbose=kwargs.get("verbose", True)
        )
    else:
        return LlamaLLM(
            model_name=os.getenv("OLLAMA_MODEL", kwargs.get("model_name", "llama3")),
            base_url=os.getenv("OLLAMA_API_BASE", kwargs.get("base_url", "http://localhost:11434")),
            temperature=float(os.getenv("CREW_TEMPERATURE", str(kwargs.get("temperature", 0.7)))),
            timeout=int(os.getenv("OLLAMA_TIMEOUT", str(kwargs.get("timeout", 120)))),
            retry_count=int(os.getenv("OLLAMA_RETRY_COUNT", str(kwargs.get("retry_count", 3)))),
            retry_delay=int(os.getenv("OLLAMA_RETRY_DELAY", str(kwargs.get("retry_delay", 2)))),
            verbose=kwargs.get("verbose", True)
        )


def test_llm_integration():
    """
    Test function to verify that the LLM integration is working.
    This function tests both the mock and real integrations.
    
    Returns:
        bool: True if tests pass, False otherwise
    """
    print_header("TESTING LLM INTEGRATION")
    
    # Test the mock LLM
    print_info("Testing Mock LLM...")
    mock_llm = MockLLM()
    mock_response = mock_llm.call(prompt="Tell me about this property")
    
    if not mock_response:
        print_error("Mock LLM test failed: No response")
        return False
        
    print_info("Mock LLM response received successfully")
    
    # Test the real LLM if Ollama is available
    if check_ollama_installed() and check_ollama_running():
        print_info("Testing actual Llama integration...")
        
        # Create a real LLM instance with short timeout for testing
        llm = LlamaLLM(timeout=30, retry_count=1)
        
        try:
            response = llm.call(prompt="Hello, are you working? Respond in one sentence.")
            
            if not response:
                print_warning("Llama integration test: No response received")
                return False
                
            print_success("Llama integration test passed!")
            print_info(f"Response: {response.strip()[:100]}...")
            return True
            
        except Exception as e:
            print_error(f"Llama integration test failed: {str(e)}")
            return False
    else:
        print_warning("Skipping real Llama test: Ollama not available")
        return True
    
    return True


if __name__ == "__main__":
    # Run the test if this file is executed directly
    success = test_llm_integration()
    sys.exit(0 if success else 1) 