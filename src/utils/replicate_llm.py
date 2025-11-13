"""
Custom LangChain LLM wrapper for Replicate API
Allows using Replicate's models as drop-in replacement for OpenAI
"""

import replicate
import os
from typing import Any, List, Optional
from langchain_core.language_models.llms import LLM
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.callbacks.manager import CallbackManagerForLLMRun


class ReplicateLLM(LLM):
    """Custom LLM wrapper for Replicate API"""

    model: str = "openai/gpt-4o-mini"
    temperature: float = 0.0
    max_tokens: int = 2000
    api_token: Optional[str] = None

    def __init__(self, model: str = "openai/gpt-4o-mini", temperature: float = 0.0, **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.temperature = temperature

        # Set API token from parameter or environment
        if self.api_token:
            os.environ["REPLICATE_API_TOKEN"] = self.api_token
        elif "REPLICATE_API_TOKEN" not in os.environ:
            raise ValueError("REPLICATE_API_TOKEN not found in environment or parameters")

    @property
    def _llm_type(self) -> str:
        return "replicate"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call Replicate API"""

        input_params = {
            "prompt": prompt,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        # Add system prompt if provided
        if "system_prompt" in kwargs:
            input_params["system_prompt"] = kwargs["system_prompt"]

        # Stream response and collect
        response_text = ""
        try:
            for event in replicate.stream(self.model, input=input_params):
                response_text += str(event)

                # Call callbacks if provided
                if run_manager:
                    run_manager.on_llm_new_token(str(event))
        except Exception as e:
            raise ValueError(f"Replicate API error: {str(e)}")

        return response_text

    def invoke(self, messages: List[BaseMessage], **kwargs) -> AIMessage:
        """
        LangChain compatibility method - converts messages to prompt
        """
        # Extract system prompt and user prompt from messages
        system_prompt = ""
        user_prompt = ""

        for message in messages:
            if isinstance(message, SystemMessage):
                system_prompt = message.content
            elif isinstance(message, HumanMessage):
                user_prompt = message.content

        # Combine system and user prompts
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nUser: {user_prompt}"
            kwargs["system_prompt"] = system_prompt
        else:
            full_prompt = user_prompt

        # Call the API
        response_text = self._call(full_prompt, **kwargs)

        # Return as AIMessage for LangChain compatibility
        return AIMessage(content=response_text)


class ReplicateChatModel:
    """
    Chat model wrapper that mimics OpenAI's ChatOpenAI interface
    Drop-in replacement for langchain_openai.ChatOpenAI
    """

    def __init__(
        self,
        model: str = "openai/gpt-4o-mini",
        temperature: float = 0.0,
        api_token: Optional[str] = None,
        **kwargs
    ):
        self.model = model
        self.temperature = temperature
        self.llm = ReplicateLLM(
            model=model,
            temperature=temperature,
            api_token=api_token
        )

    def invoke(self, messages: List[BaseMessage], **kwargs) -> AIMessage:
        """Invoke the model with messages"""
        return self.llm.invoke(messages, **kwargs)

    def __call__(self, messages: List[BaseMessage], **kwargs) -> AIMessage:
        """Allow calling the model directly"""
        return self.invoke(messages, **kwargs)
