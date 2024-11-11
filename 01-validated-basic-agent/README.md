# Notion Agent

This AI-powered agent generates haikus and inserts them into a Notion page. You can extend it to any interaction implemented in the Notion API.
The upgraded version uses `LiteLLM` for flexible language model handling, `Instructor` and `Pydantic` for input validation, and `UV` to manage dependencies and execution environments (optinal but extremely convenient).

## Setup Instructions
- **Security**: Keep your API tokens secret. **Do not push them to your repository**.

### 1. Create a New Page on Notion
- Start by creating a new page in your Notion workspace. This is where your haikus will be inserted.

### 2. Create a Notion Integration
- Go to the [Notion Developer Dashboard](https://www.notion.so/my-integrations) and create a new integration.
- Name your integration and select the workspace where your Notion page is located.
- After creating the integration, **copy your API token**. You’ll need this for your `.env` file (see step 5).

### 3. Set Up Permissions
- Go to the Notion page you created in step 1.
- Click on the `...` menu in the top-right corner of the page.
- Select **"Add Connections"**, then find and add the integration you created in step 2. This allows the integration to access the page.

### 4. Obtain the Page ID
- In the URL of your Notion page, look for the part that follows this format:
  ```
  https://www.notion.so/yourworkspace/<PAGE_NAME>-<PAGE_ID>
  ```
- The `<PAGE_ID>` is a UUID in the format `8-4-4-4-12` (e.g., `123e4567-e89b-12d3-a456-426614174000`).
- Copy the `<PAGE_ID>` and save it for later.

### 5. Set Up the `.env` File
- Create a `.env` file in the project root directory.
- Add the following environment variables:
  ```bash
  OPENAI_API_KEY=your_openai_api_key_here
  NOTION_API_KEY=your_notion_api_key_here
  NOTION_PAGE_ID=your_notion_page_id_here
  OPENAI_MODEL=gpt-3.5-turbo  # or gpt-4, depending on your preference
  ```

### 6. Project management using UV
For smooth and easy dependency management and reproducible environments, I recommend using `UV`. This optional step ensures all required dependencies are installed consistently across environments.

1. Intialise the project `uv init`
2. Install the python version you want `uv python install 3.11`
3. Add the dependencies: `uv add requests python-dotenv openai litellm instructor pydantic`
4. Run the agent with:
   ```bash
   uv run agent.py
   ```

### 7. Run the Agent
If not using `UV`, simply install the dependencies manually:
   ```bash
   pip install -r requirements.txt
   ```
Then, run the agent:
   ```bash
   python agent.py
   ```

### Using the Enhanced Agent

Once the agent is running, you can ask it to generate and insert a haiku by entering:
```
Please insert a haiku about cats.
```

The upgraded agent now supports multiple actions and is validated for input correctness. For example, you could later add actions such as retrieving weather data by expanding the action models.

---

## REM

### 1. Provider Flexibility with `LiteLLM`
`LiteLLM` abstracts the language model provider, allowing you to switch models without changing core code. This abstraction supports flexibility and scalability as you add more functionalities or providers.

### 2. Input Validation with `Instructor` and `Pydantic`
Using `Instructor` with `Pydantic` models allows the agent to validate inputs before processing them. This validation ensures that all data sent to Notion (or other future tools) adheres to predefined schemas, improving data quality and robustness.

### 3. Simplified Dependency Management with `UV`
Using `UV` simplifies setting up dependencies and running the agent in consistent, isolated environments. This helps maintain reproducibility and minimizes dependency conflicts.


