"""
LLM integration for lazygit-ai.

Provides AI enhancement for commit messages using various LLM providers
including OpenAI, Anthropic, and local models via Ollama.
"""

import os
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

import requests

from .analyzer import GitAnalysis
from ..utils.config import ConfigManager


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, config: ConfigManager) -> None:
        """Initialize LLM provider with configuration."""
        self.config = config
        self.ai_config = config.get_ai_config()
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM provider is available."""
        pass
    
    @abstractmethod
    def enhance_message(self, analysis: GitAnalysis, rule_message: str) -> Optional[str]:
        """Enhance a commit message using AI."""
        pass
    
    def _format_diff_for_prompt(self, analysis: GitAnalysis) -> str:
        """Format git diff for LLM prompt."""
        if not analysis.staged_diff:
            return "No staged changes"
        
        # Clean up the diff for better LLM processing
        lines = analysis.staged_diff.split("\n")
        cleaned_lines = []
        
        for line in lines:
            # Skip binary files and very long lines
            if "Binary files" in line or len(line) > 200:
                continue
            
            # Limit the number of lines to avoid token limits
            if len(cleaned_lines) >= 100:
                cleaned_lines.append("... (truncated)")
                break
            
            cleaned_lines.append(line)
        
        return "\n".join(cleaned_lines)
    
    def _create_prompt(self, analysis: GitAnalysis, rule_message: str) -> str:
        """Create a prompt for the LLM."""
        diff = self._format_diff_for_prompt(analysis)
        
        prompt = f"""You are an expert at writing clear, concise commit messages that follow conventional commit standards.

Context:
- Branch: {analysis.branch_name}
- Files changed: {', '.join(analysis.staged_files[:5])}{'...' if len(analysis.staged_files) > 5 else ''}
- Change summary: {analysis.change_summary}

Git diff:
```
{diff}
```

A rule-based system generated this commit message: "{rule_message}"

Please enhance this commit message to be more specific, clear, and meaningful. Follow these guidelines:
1. Use conventional commit format: <type>(<scope>): <description>
2. Keep it under 72 characters
3. Use imperative mood (e.g., "add" not "added")
4. Be specific about what changed
5. Focus on the "why" not just the "what"
6. If the rule-based message is already good, return it unchanged

Enhanced commit message:"""
        
        return prompt


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider for commit message enhancement."""
    
    def __init__(self, config: ConfigManager) -> None:
        """Initialize OpenAI provider."""
        super().__init__(config)
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        return bool(self.api_key)
    
    def enhance_message(self, analysis: GitAnalysis, rule_message: str) -> Optional[str]:
        """Enhance commit message using OpenAI GPT."""
        if not self.is_available():
            return None
        
        try:
            import openai
            
            # Configure OpenAI client
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.ai_config["timeout"]
            )
            
            prompt = self._create_prompt(analysis, rule_message)
            
            response = client.chat.completions.create(
                model=self.ai_config["model"],
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at writing clear, concise commit messages that follow conventional commit standards."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.ai_config["max_tokens"],
                temperature=self.ai_config["temperature"],
            )
            
            enhanced_message = response.choices[0].message.content.strip()
            
            # Clean up the response
            enhanced_message = self._clean_response(enhanced_message)
            
            return enhanced_message if enhanced_message != rule_message else None
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return None
    
    def _clean_response(self, response: str) -> str:
        """Clean up the LLM response."""
        # Remove quotes if present
        response = response.strip('"\'')
        
        # Remove markdown code blocks
        response = response.replace("```", "").strip()
        
        # Take only the first line (commit message should be one line)
        response = response.split("\n")[0].strip()
        
        return response


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider for commit message enhancement."""
    
    def __init__(self, config: ConfigManager) -> None:
        """Initialize Anthropic provider."""
        super().__init__(config)
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    def is_available(self) -> bool:
        """Check if Anthropic is available."""
        return bool(self.api_key)
    
    def enhance_message(self, analysis: GitAnalysis, rule_message: str) -> Optional[str]:
        """Enhance commit message using Anthropic Claude."""
        if not self.is_available():
            return None
        
        try:
            import anthropic
            
            client = anthropic.Anthropic(
                api_key=self.api_key,
                timeout=self.ai_config["timeout"] * 1000  # Convert to milliseconds
            )
            
            prompt = self._create_prompt(analysis, rule_message)
            
            response = client.messages.create(
                model=self.ai_config["model"],
                max_tokens=self.ai_config["max_tokens"],
                temperature=self.ai_config["temperature"],
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            enhanced_message = response.content[0].text.strip()
            enhanced_message = self._clean_response(enhanced_message)
            
            return enhanced_message if enhanced_message != rule_message else None
            
        except Exception as e:
            print(f"Anthropic API error: {e}")
            return None
    
    def _clean_response(self, response: str) -> str:
        """Clean up the LLM response."""
        # Remove quotes if present
        response = response.strip('"\'')
        
        # Remove markdown code blocks
        response = response.replace("```", "").strip()
        
        # Take only the first line
        response = response.split("\n")[0].strip()
        
        return response


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider for commit message enhancement."""
    
    def __init__(self, config: ConfigManager) -> None:
        """Initialize Ollama provider."""
        super().__init__(config)
        self.base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    
    def is_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def enhance_message(self, analysis: GitAnalysis, rule_message: str) -> Optional[str]:
        """Enhance commit message using Ollama."""
        if not self.is_available():
            return None
        
        try:
            prompt = self._create_prompt(analysis, rule_message)
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.ai_config["model"],
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.ai_config["temperature"],
                        "num_predict": self.ai_config["max_tokens"],
                    }
                },
                timeout=self.ai_config["timeout"]
            )
            
            if response.status_code == 200:
                result = response.json()
                enhanced_message = result.get("response", "").strip()
                enhanced_message = self._clean_response(enhanced_message)
                
                return enhanced_message if enhanced_message != rule_message else None
            else:
                print(f"Ollama API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Ollama API error: {e}")
            return None
    
    def _clean_response(self, response: str) -> str:
        """Clean up the LLM response."""
        # Remove quotes if present
        response = response.strip('"\'')
        
        # Remove markdown code blocks
        response = response.replace("```", "").strip()
        
        # Take only the first line
        response = response.split("\n")[0].strip()
        
        return response


class LLMProvider:
    """Main LLM provider that manages different backends."""
    
    def __init__(self, config: ConfigManager) -> None:
        """Initialize LLM provider with configuration."""
        self.config = config
        self.ai_config = config.get_ai_config()
        
        # Initialize available providers
        self.providers = {
            "openai": OpenAIProvider(config),
            "anthropic": AnthropicProvider(config),
            "ollama": OllamaProvider(config),
        }
        
        self.current_provider = self.ai_config["provider"]
    
    def is_available(self) -> bool:
        """Check if any LLM provider is available."""
        if self.current_provider == "none":
            return False
        
        provider = self.providers.get(self.current_provider)
        return provider and provider.is_available()
    
    def enhance_message(self, analysis: GitAnalysis, rule_message: str) -> Optional[str]:
        """Enhance commit message using the configured LLM provider."""
        if not self.is_available():
            return None
        
        provider = self.providers.get(self.current_provider)
        if not provider:
            return None
        
        try:
            enhanced_message = provider.enhance_message(analysis, rule_message)
            return enhanced_message
        except Exception as e:
            print(f"LLM enhancement error: {e}")
            return None
    
    def get_available_providers(self) -> List[str]:
        """Get list of available LLM providers."""
        available = []
        
        for name, provider in self.providers.items():
            if provider.is_available():
                available.append(name)
        
        return available
    
    def test_provider(self, provider_name: str) -> bool:
        """Test if a specific provider is working."""
        provider = self.providers.get(provider_name)
        if not provider:
            return False
        
        try:
            from dataclasses import dataclass
            
            @dataclass
            class TestAnalysis:
                branch_name: str = "test-branch"
                staged_files: List[str] = ["test.py"]
                staged_diff: str = "+ def test_function():\n+     pass"
                change_summary: str = "1 file (code)"
            
            test_analysis = TestAnalysis()
            result = provider.enhance_message(test_analysis, "test: add test function")
            
            return result is not None
            
        except Exception:
            return False 