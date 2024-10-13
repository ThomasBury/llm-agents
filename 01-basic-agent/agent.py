import openai
import requests
from dotenv import load_dotenv
from datetime import datetime
import json
import os

# Load environment variables
load_dotenv()

# OpenAI and Notion API setup
openai.api_key = os.getenv('OPENAI_API_KEY')
notion_api_key = os.getenv('NOTION_API_KEY')
notion_database_id = os.getenv('NOTION_DATABASE_ID')

headers = {
    "Authorization": f"Bearer {notion_api_key}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def create_notion_task(task_name: str, due_on: str = "today") -> str:
    """
    Creates a task in Notion with a given name and due date.
    
    Parameters
    ----------
    task_name : str
        The name of the task to be created in Notion.
    due_on : str, optional
        The due date for the task in YYYY-MM-DD format. If not specified,
        the current date is used by default (default is "today").
        
    Returns
    -------
    str
        The result of the API call. If successful, a confirmation message
        is returned; otherwise, an error message is returned.
        
    Example
    -------
    >>> create_notion_task("Finish project", "2024-10-15")
    'Task successfully created in Notion!'
    """
    if due_on == "today":
        due_on = str(datetime.now().date())
    
    task_body = {
        "parent": {"database_id": notion_database_id},
        "properties": {
            "Name": {"title": [{"text": {"content": task_name}}]},
            "Due": {"date": {"start": due_on}}
        }
    }

    response = requests.post('https://api.notion.com/v1/pages', 
                             headers=headers, json=task_body)

    if response.status_code == 200:
        return "Task successfully created in Notion!"
    return f"Failed to create task: {response.text}"

def get_notion_tasks() -> list:
    """
    Retrieves a list of tasks from the connected Notion database.
    
    Returns
    -------
    list
        A list of task names and their due dates. If there are no tasks or 
        an error occurs, an appropriate message is returned.
        
    Example
    -------
    >>> get_notion_tasks()
    ['Task 1 - Due: 2024-10-15', 'Task 2 - Due: 2024-10-20']
    """
    url = f"https://api.notion.com/v1/databases/{notion_database_id}/query"
    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        tasks = response.json()
        task_list = []
        for result in tasks["results"]:
            task_name = result["properties"]["Name"]["title"][0]["text"]["content"]
            due_date = result["properties"].get("Due", {}).get("date", {}).get("start", "No due date")
            task_list.append(f"{task_name} - Due: {due_date}")
        return task_list
    return f"Failed to retrieve tasks: {response.text}"

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
                "name": "create_notion_task",
                "description": "Creates a task in Notion given the name of the task and due date",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_name": {
                            "type": "string",
                            "description": "The name of the task in Notion"
                        },
                        "due_on": {
                            "type": "string",
                            "description": "The date the task is due in the format YYYY-MM-DD"
                        },
                    },
                    "required": ["task_name"]
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_notion_tasks",
                "description": "Retrieves a list of tasks from Notion",
            },
        }
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
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        functions=get_tools()
    )

    response_message = completion['choices'][0]['message']
    tool_calls = response_message.get('function_call')

    if tool_calls:
        available_functions = {
            "create_notion_task": create_notion_task,
            "get_notion_tasks": get_notion_tasks
        }

        # Execute the tool function
        function_name = tool_calls['name']
        function_args = json.loads(tool_calls['arguments'])
        function_response = available_functions[function_name](**function_args)

        # Add tool call result to conversation
        messages.append({"role": "assistant", "content": function_response})
        return function_response

    return response_message['content']

def main():
    """
    Main entry point for interacting with the task management assistant.
    
    Continuously accepts user input to create or retrieve tasks until the
    user decides to quit.
    """
    messages = [
        {
            "role": "system",
            "content": f"You are a task management assistant connected to Notion. The current date is: {datetime.now().date()}"
        }
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
