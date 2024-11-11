import os
import requests
from datetime import datetime
from typing import List, Dict, Any, Union, Callable
from dataclasses import dataclass
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import instructor
import litellm

# Load environment variables
load_dotenv()

@dataclass
class AgentConfig:
    """Configuration for the AI Assistant.

    Attributes
    ----------
    openai_api_key : str
        The OpenAI API key for accessing language models.
    notion_api_key : str
        The Notion API key for accessing the Notion API.
    notion_page_id : str
        The Notion page ID where data will be inserted.
    openai_model : str
        The OpenAI model to use for completions.
    """
    openai_api_key: str = os.getenv('OPENAI_API_KEY')
    notion_api_key: str = os.getenv('NOTION_API_KEY')
    notion_page_id: str = os.getenv('NOTION_PAGE_ID')
    openai_model: str = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')  # Default model

# Action models
class HaikuRequest(BaseModel):
    """Model for a request to create a haiku.

    Attributes
    ----------
    text : str
        The text of the haiku to insert into Notion.
    title : str, optional
        The title for the haiku in Notion, defaults to "Haiku".
    """
    text: str = Field(..., description="The haiku text to insert into Notion")
    title: str = Field("Haiku", description="Title for the haiku in Notion")

class WeatherRequest(BaseModel):
    """Model for a request to retrieve weather data.

    Attributes
    ----------
    location : str
        The location for which to retrieve the weather data.
    """
    location: str = Field(..., description="The location to retrieve the weather for")

# Parent model to support multiple actions
class ActionModel(BaseModel):
    """Parent model to handle multiple actions in a single request.

    Attributes
    ----------
    actions : list of Union[HaikuRequest, WeatherRequest]
        List of requested actions to be performed by the assistant.
    """
    actions: List[Union[HaikuRequest, WeatherRequest]] = Field(
        ..., description="List of requested actions"
    )

# Handler functions for each action
def handle_haiku_request(request: HaikuRequest, notion_api_key: str, notion_page_id: str) -> str:
    """Handles a request to insert a haiku into Notion.

    Parameters
    ----------
    request : HaikuRequest
        The request object containing the haiku text and title.
    notion_api_key : str
        The Notion API key used for authorization.
    notion_page_id : str
        The Notion page ID where the haiku should be inserted.

    Returns
    -------
    str
        A message indicating success or failure of the insertion.
    """
    headers = {
        "Authorization": f"Bearer {notion_api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    haiku_body = {
        "parent": {"page_id": notion_page_id},
        "properties": {
            "title": {
                "title": [
                    {
                        "type": "text",
                        "text": {"content": request.text}
                    }
                ]
            }
        }
    }
    response = requests.post('https://api.notion.com/v1/pages', headers=headers, json=haiku_body)
    return "Haiku successfully inserted in Notion!" if response.status_code == 200 else f"Failed to insert haiku: {response.status_code}"

def handle_weather_request(request: WeatherRequest) -> str:
    """Handles a request to retrieve weather data.

    Parameters
    ----------
    request : WeatherRequest
        The request object containing the location for weather data.

    Returns
    -------
    str
        A message with the retrieved weather data.
    """
    # Placeholder for actual weather API integration
    return f"Retrieved weather data for {request.location}."

class AIAssistant:
    """AI Assistant that interacts with OpenAI's API and handles multiple actions.

    Attributes
    ----------
    config : AgentConfig
        The configuration object containing API keys and model settings.
    actions_dispatch : dict
        A dictionary mapping action models to their handler functions.
    """

    def __init__(self, config: AgentConfig):
        self.config = config
        self._instructor_client = None
        self.actions_dispatch: Dict[type, Callable[[BaseModel], str]] = {
            HaikuRequest: lambda action: handle_haiku_request(action, self.config.notion_api_key, self.config.notion_page_id),
            WeatherRequest: handle_weather_request,
        }
    
    @property
    def instructor_client(self):
        """Lazily initializes and returns the instructor client.

        Returns
        -------
        InstructorClient
            The client for interacting with Instructor API.
        """
        if self._instructor_client is None:
            self._instructor_client = instructor.from_litellm(litellm.completion)
        return self._instructor_client

    def prompt_ai(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Processes user messages and invokes actions based on AI responses.

        Parameters
        ----------
        messages : list of dict
            The conversation history between the user and the assistant.

        Returns
        -------
        list of str
            List of responses from the assistant after processing actions.
        """
        completion = self.instructor_client.chat.completions.create(
            model=self.config.openai_model,
            messages=messages,
            response_model=ActionModel  # Accepts multiple actions
        )

        results = []
        for action in completion.actions:
            action_type = type(action)
            if action_type in self.actions_dispatch:
                results.append(self.actions_dispatch[action_type](action))
            else:
                results.append(f"No handler found for action type: {action_type.__name__}")
        return results

def main():
    """Main function to initialize the assistant and handle user interactions."""
    config = AgentConfig()
    assistant = AIAssistant(config)
    messages = [
        {
            "role": "system",
            "content": f"You are an assistant that can create haikus and retrieve weather data. The current date is: {datetime.now().date()}"
        }
    ]

    while True:
        user_input = input("Chat with AI (q to quit): ").strip()
        if user_input.lower() == 'q':
            break

        messages.append({"role": "user", "content": user_input})
        ai_responses = assistant.prompt_ai(messages)
        for response in ai_responses:
            print(response)
            messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
