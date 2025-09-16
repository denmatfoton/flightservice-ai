import os
import asyncio
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder
from dotenv import load_dotenv

load_dotenv()

async def test_agent():
    async with DefaultAzureCredential() as credential:
        async with AIProjectClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=credential,
        ) as project_client:

            _agent_id = os.environ["AGENT_ID"]

            print("Creating message thread")
            thread = await project_client.agents.threads.create()

            print("Creating message")
            await project_client.agents.messages.create(
                thread_id=thread.id,
                role="user",
                content="Hello, how are you?"
            )

            print("Creating and processing run")
            run = await project_client.agents.runs.create_and_process(
                thread_id=thread.id,
                agent_id=_agent_id
            )

            if run.status == "failed":
                print(f"Run failed: {run.last_error}")
                return

            print("Messages:")
            messages = project_client.agents.messages.list(
                thread_id=thread.id,
                order=ListSortOrder.ASCENDING
            )

            async for message in messages:
                if message.run_id == run.id and message.text_messages:
                    print(f"{message.role}: {message.text_messages[-1].text.value}")

            # Clean up the thread
            await project_client.agents.threads.delete(thread.id)

if __name__ == "__main__":
    asyncio.run(test_agent())
