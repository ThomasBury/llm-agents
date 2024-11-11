# Notion Haiku Agent

This simple agent inserts a haiku into a Notion page using the Notion API and OpenAI's GPT models. Follow the steps below to set it up.

## Setup Instructions

### 1. Create a New Page on Notion
- Start by creating a new page in your Notion workspace. This is where your haikus will be inserted.

### 2. Create a Notion Integration
- Go to the [Notion Developer Dashboard](https://www.notion.so/my-integrations) and create a new integration.
- Give your integration a name, and select the workspace where your new Notion page is located.
- After creating the integration, **copy your API token**. You’ll need this for your `.env` file (see step 5).
  
### 3. Set Up Permissions
- Go to the page you created in step 1.
- Click on the `...` menu in the top-right corner of the page.
- Select **"Add Connections"**, then search for and select the integration you created in step 2. This will allow the integration to access the page.

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

### 6. Run the Agent
- In your terminal, navigate to the project directory and run the following command:
  ```bash
  python agent.py
  ```
- Once the agent is running, you can ask it to generate and insert a haiku. For example:
  ```
  Please insert a haiku about cats.
  ```

### Notes
- **Security**: Keep your API tokens secret. Do not push them to your repository.
- The agent will use OpenAI’s models to generate a haiku and insert it into your Notion page.
