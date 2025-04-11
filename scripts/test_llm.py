#!/usr/bin/env python3
"""
Test script for validating the LLM integration.
Run this script to test if Ollama is correctly set up and integrated.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Import project modules
from src.utils.llm import setup_llm, test_llm_integration, LlamaLLM, MockLLM
from src.utils.formatting import print_header, print_info, print_success, print_error, print_warning

def main():
    """Run LLM integration tests."""
    print_header("LLAMA MODEL INTEGRATION TEST")
    
    # Run the built-in test function
    success = test_llm_integration()
    
    if not success:
        print_error("LLM integration test failed")
        return 1
    
    # Try a real conversation with the model
    print_header("TESTING CONVERSATION WITH LLM")
    
    # Force using the real LLM for this test, not the mock
    os.environ["USE_MOCK_LLM"] = "false"
    use_mock = False
    
    # Create the LLM instance with appropriate settings
    llm = setup_llm(
        use_mock=use_mock,
        temperature=0.7,
        timeout=60,  # Shorter timeout for testing
        retry_count=2,
        verbose=True
    )
    
    try:
        # Test with a property analysis question
        prompt = """
        I'm considering developing a property for residential use. It's 100 acres, 
        currently zoned as agricultural. What factors should I consider for rezoning 
        and development?
        """
        
        print_info("Sending prompt to the model...")
        print_info(f"Prompt: {prompt[:100]}...")
        
        # Use the call method to get a response
        response = llm.call(prompt=prompt)
        
        if not response:
            print_error("No response received from LLM")
            return 1
            
        print_success("Successfully received response!")
        print_header("MODEL RESPONSE")
        print(response.strip())
        
        # Additional test with message-style input
        print_header("TESTING MESSAGES FORMAT")
        messages = [
            {"role": "system", "content": "You are a helpful property development assistant."},
            {"role": "user", "content": "What are the key environmental factors to check before buying land?"}
        ]
        
        print_info("Sending messages to model...")
        response = llm.call(messages=messages)
        
        if not response:
            print_error("No response received from LLM for messages input")
            return 1
            
        print_success("Successfully received response for messages input!")
        print_header("MODEL RESPONSE (MESSAGES)")
        print(response.strip())
        
        return 0
        
    except Exception as e:
        print_error(f"Error during conversation test: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 