"""
Groq API Client
Handles LLM chat completions using Groq with Llama models
"""

import os
from typing import List, Dict, Optional
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class GroqClient:
    """Client for Groq API interactions"""
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize Groq client
        
        Args:
            api_key: Groq API key (defaults to env variable)
            model: Model name (defaults to env variable or llama-3.1-70b-versatile)
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model or os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=self.api_key)
        
    def chat_completion(
        self,
        user_question: str,
        context: str = None,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> Dict:
        """
        Generate chat completion with optional context
        
        Args:
            user_question: User's question
            context: Retrieved context from vector store
            system_prompt: Custom system prompt (optional)
            temperature: Response creativity (0-1)
            max_tokens: Maximum response length
            
        Returns:
            Dictionary with response and metadata
        """
        # Default system prompt
        if system_prompt is None:
            system_prompt = """You are a helpful restaurant assistant. Answer questions based ONLY on the provided context.
If the answer is not in the context, politely say you don't have that information.
Be friendly, concise, and accurate. Keep responses natural and conversational."""
        
        # Build messages
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add context if provided
        if context:
            user_message = f"""Context from restaurant documents:
{context}

Customer Question: {user_question}

Please answer the question based on the context provided above."""
        else:
            user_message = user_question
        
        messages.append({"role": "user", "content": user_message})
        
        try:
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extract response
            assistant_message = response.choices[0].message.content
            
            return {
                "response": assistant_message,
                "model": self.model,
                "tokens_used": {
                    "prompt": response.usage.prompt_tokens,
                    "completion": response.usage.completion_tokens,
                    "total": response.usage.total_tokens
                },
                "finish_reason": response.choices[0].finish_reason
            }
            
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")
    
    def chat_with_history(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> Dict:
        """
        Generate chat completion with conversation history
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Response creativity (0-1)
            max_tokens: Maximum response length
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            assistant_message = response.choices[0].message.content
            
            return {
                "response": assistant_message,
                "model": self.model,
                "tokens_used": {
                    "prompt": response.usage.prompt_tokens,
                    "completion": response.usage.completion_tokens,
                    "total": response.usage.total_tokens
                },
                "finish_reason": response.choices[0].finish_reason
            }
            
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")
    
    def test_connection(self) -> bool:
        """
        Test Groq API connection
        
        Returns:
            True if connection successful
        """
        try:
            response = self.chat_completion(
                user_question="Hello, are you working?",
                max_tokens=50
            )
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False


# Testing
if __name__ == "__main__":
    print("Testing Groq API Client...")
    
    try:
        client = GroqClient()
        print(f"✓ Client initialized with model: {client.model}")
        
        # Test connection
        print("\nTesting connection...")
        if client.test_connection():
            print("✓ Connection successful!")
            
            # Test with context
            print("\nTesting with context...")
            context = "Our restaurant is open from 11 AM to 11 PM daily. We serve Italian cuisine."
            response = client.chat_completion(
                user_question="What are your opening hours?",
                context=context
            )
            
            print(f"\nResponse: {response['response']}")
            print(f"Tokens used: {response['tokens_used']['total']}")
        else:
            print("❌ Connection failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure to:")
        print("1. Set GROQ_API_KEY in .env file")
        print("2. Get your API key from: https://console.groq.com")