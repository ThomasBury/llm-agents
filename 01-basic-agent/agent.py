import openai
from openai import OpenAI
import requests
from dotenv import load_dotenv
from datetime import datetime
import json
import os

# Load environment variables
load_dotenv()

# OpenAI and Notion API setup
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
notion_api_key = os.getenv('NOTION_API_KEY')
notion_page_id = os.getenv('NOTION_PAGE_ID')
openai_model = os.getenv('OPENAI_MODEL')

headers = {
    "Authorization": f"Bearer {notion_api_key}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def insert_haiku(haiku: str) -> str:
    """
    Inserts a haiku as a new page in Notion under a specified parent page.

    Parameters
    ----------
    haiku : str
        The haiku content to be inserted into Notion.

    Returns
    -------
    str
        The result of the API call. If successful, a confirmation message
        is returned; otherwise, an error message is returned.
    """
    
    haiku_body = {
        "parent": {"page_id": notion_page_id},
        "properties": {
            "title": {  # Correct title property for Notion API
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": haiku
                        }
                    }
                ]
            }
        }
    }

    response = requests.post('https://api.notion.com/v1/pages', headers=headers, json=haiku_body)

    if response.status_code == 200:
        return "Haiku successfully inserted in Notion!"
    else:
        return f"Failed to insert haiku: {response.status_code}, {response.text}"


def get_tools() -> list:
    """
    Provides a list of tools (functions) that the LLM can invoke.

    Returns
    -------
    list
        A list of tools with their name, description, and parameters that
        can be used by the OpenAI agent.
    """
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "insert_haiku",
                "description": "Insert a haiku",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "haiku": {
                            "type": "string",
                            "description": "The haiku to be inserted"
                        },
                    },
                    "required": ["haiku"]
                },
            },
        },
    ]
    return tools

def prompt_ai(messages: list) -> str:
    """
    Handles user messages and determines if a tool needs to be called by
    the OpenAI model.

    Parameters
    ----------
    messages : list
        A list of conversation messages between the user and the assistant.

    Returns
    -------
    str
        The assistant's response after processing the message or invoking
        a function.
    """
    # First, prompt the AI with the latest user message
    completion = client.chat.completions.create(
        model=openai_model,  # Make sure to specify the correct model
        messages=messages,  # No need for a separate 'prompt' parameter
        tools=get_tools()
    )

    response_message = completion.choices[0].message
    tool_calls = response_message.tool_calls

    # Second, see if the AI decided it needs to invoke a tool
    if tool_calls:
        # If the AI decided to invoke a tool, invoke it
        available_functions = {
            "insert_haiku": insert_haiku,
        }

        # Add the tool request to the list of messages so the AI knows later it invoked the tool
        messages.append(response_message)

        # Next, for each tool the AI wanted to call, call it and add the tool result to the list of messages
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(**function_args)

            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response
            })

        # Call the AI again so it can produce a response with the result of calling the tool(s)
        second_response = client.chat.completions.create(
            model=openai_model,
            messages=messages,
        )

        return second_response.choices[0].message.content

    return response_message.content


# Example main function
def main():
    messages = [
        {"role": "system", "content": f"You are an assistant that creates haikus. The current date is: {datetime.now().date()}"}
    ]

    while True:
        user_input = input("Chat with AI (q to quit): ").strip()
        if user_input.lower() == 'q':
            break

        messages.append({"role": "user", "content": user_input})
        ai_response = prompt_ai(messages)
        print(ai_response)
        messages.append({"role": "assistant", "content": ai_response})

if __name__ == "__main__":
    main()
