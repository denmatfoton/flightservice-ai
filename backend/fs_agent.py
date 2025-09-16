import os
import asyncio
from typing import Dict, Optional
from azure.ai.projects.aio import AIProjectClient
from azure.ai.agents.models import ListSortOrder
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class FlightServiceAgent:
    """Azure AI Agent for flight data analysis and briefing generation"""
    
    def __init__(self):
        """Initialize the FlightServiceAgent with Azure AI configuration"""
        self._validate_environment()
        
        self._agent_id = os.environ["AGENT_ID"]
        self._timeout = int(os.environ.get("API_TIMEOUT", 30))
        
        self._endpoint = os.environ["PROJECT_ENDPOINT"]
        self._credential: Optional[DefaultAzureCredential] = None
        self._client: Optional[AIProjectClient] = None
        self._client_lock = asyncio.Lock()
    
    def _validate_environment(self):
        """Validate that all required environment variables are present"""
        required_vars = ["PROJECT_ENDPOINT", "AGENT_ID"]
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        
        if missing_vars:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing_vars)}. "
                "Please run './setup_environment.sh' to configure your environment."
            )
    
    async def analyze_flight_data(self, flight_info_dict: Dict) -> str:
        """Analyze flight data using Azure AI Agent with explicit workflow (thread -> message -> run -> messages -> cleanup)."""
        await self._ensure_client()
        flight_data_text = self._build_prompt(flight_info_dict)

        thread = None
        try:
            # 1. Create thread
            thread = await self._client.agents.threads.create()

            # 2. Send user message
            await self._client.agents.messages.create(
                thread_id=thread.id,
                role="user",
                content=flight_data_text
            )

            # 3. Create and process run
            run = await self._client.agents.runs.create_and_process(
                thread_id=thread.id,
                agent_id=self._agent_id
            )

            if run.status == "failed":
                return f"Run failed: {run.last_error}"

            # 4. Collect messages (stream style iteration)
            result_text = await self._gather_run_response(thread.id, run.id)
            return result_text or "No response generated."
        except Exception as e:
            return f"Error during analysis workflow: {e}"
        finally:
            # 5. Cleanup thread
            try:
                if thread is not None:
                    await self._client.agents.threads.delete(thread.id)
            except Exception:
                pass
    
    async def _ensure_client(self):
        """Lazily create credential and client (support reuse across requests)."""
        if self._client is not None:
            return
        async with self._client_lock:
            if self._client is None:  # double-checked locking
                self._credential = DefaultAzureCredential()
                self._client = AIProjectClient(
                    endpoint=self._endpoint,
                    credential=self._credential,
                )

    def _build_prompt(self, flight_info_dict: Dict) -> str:
        """Compose the analysis prompt from structured flight info."""
        return self._format_flight_data(flight_info_dict)
    
    def _format_flight_data(self, flight_info_dict: Dict) -> str:
        """Format flight data for agent analysis"""
        return f"""
Please analyze the following flight information and provide a comprehensive flight briefing:

PILOT PROVIDED DATA:
{self._format_dict(flight_info_dict.get('pilot_data', {}))}

ONLINE RESOURCES (Weather, Airport Info, PIREPs):
{self._format_dict(flight_info_dict.get('online_resources', {}))}

Please provide:
1. Weather analysis and recommendations
2. Route analysis and potential issues  
3. Risk assessment
4. Alternate airport recommendations
5. Overall flight briefing summary

Focus on safety considerations and provide actionable recommendations for the pilot.
"""
    
    def _format_dict(self, data_dict: Dict, indent: int = 0) -> str:
        """Format dictionary data for readable display"""
        if not data_dict:
            return "No data available"
        
        formatted = ""
        indent_str = "  " * indent
        
        for key, value in data_dict.items():
            if isinstance(value, dict):
                formatted += f"{indent_str}{key}:\n{self._format_dict(value, indent + 1)}\n"
            elif isinstance(value, list):
                formatted += f"{indent_str}{key}: {len(value)} items\n"
                for i, item in enumerate(value[:3]):  # Show first 3 items
                    formatted += f"{indent_str}  [{i}]: {str(item)[:100]}...\n"
            else:
                formatted += f"{indent_str}{key}: {value}\n"
        
        return formatted
    
    async def _gather_run_response(self, thread_id: str, run_id: str) -> Optional[str]:
        """Iterate messages for the given run in ascending order and collect assistant text."""
        messages = self._client.agents.messages.list(
            thread_id=thread_id,
            order=ListSortOrder.ASCENDING
        )
        collected: list[str] = []
        async for message in messages:
            if message.run_id == run_id and getattr(message, "text_messages", None):
                # The last text message chunk holds the complete value for this message
                collected.append(message.text_messages[-1].text.value)
        return "\n".join(collected).strip() if collected else None
    
    # Legacy methods (_extract_response, _wait_for_completion) removed in favor of direct run processing + message iteration.
    
    def sync_analyze_flight_data(self, flight_info_dict: Dict) -> str:
        """
        Synchronous wrapper for the async analyze_flight_data function
        
        Args:
            flight_info_dict: Dictionary containing complete flight information
            
        Returns:
            str: AI analysis and briefing
        """
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.analyze_flight_data(flight_info_dict))
        except RuntimeError:
            # If no event loop is running, create a new one
            return asyncio.run(self.analyze_flight_data(flight_info_dict))
    
    async def close(self):
        """Close the async client and credential."""
        try:
            if self._client is not None:
                await self._client.close()
            if self._credential is not None:
                await self._credential.close()
        finally:
            self._client = None
            self._credential = None