from dotenv import load_dotenv
import os
from langchain_openai import AzureChatOpenAI

def llm_model() -> AzureChatOpenAI:
    """
    Create and return an AzureChatOpenAI LLM instance.
    """
    return AzureChatOpenAI(
        deployment_name="call-automation-openai-gpt-4o-mini",
        temperature=0.1,  # could also load from env if needed
        api_version="2025-01-01-preview",
        azure_endpoint="https://call-automation-openai.openai.azure.com/",
        api_key="FsUF4JAg0SbHFchYIFNjxIEUPOmnt9i5uA6UMcf49TrPk7qFbrphJQQJ99BDACYeBjFXJ3w3AAABACOGX1Nm",
    )
