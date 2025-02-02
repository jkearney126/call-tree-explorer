# AI Call Tree Explorer

## Description

The AI Call Tree Explorer is an automated system designed to discover and map out conversation trees or decision graphs through simulated phone calls. It uses AI-powered agents to conduct conversations, transcribe the calls, and generate decision trees based on the interactions.


## Prerequisites

- Python 3.7+
- OpenAI API key
- Ngrok account (for webhook tunneling during local development)
- API token for the call initiation service

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/jkearney126/call-tree-explorer.git
   cd call-tree-explorer
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables in a `.env` file:
   - `API_TOKEN`: Your API token for the call service
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `TEST_PHONE_NUMBER`: The phone number to use for test calls
   - `START_CALL_ENDPOINT`: The URL to start a call
   - `GET_RECORDING_ENDPOINT`: The URL to get a recording

### Optional Step to Set OpenAI Model in config.py

You can set the OpenAI model to be used for generating decision trees in the `config.py` file. This allows you to customize the model based on your requirements.

I tested with gpt-4o, but if you have access to o1-mini, it might be worth trying that for fun.

1. Open the `config.py` file.
2. Set the `OPENAI_MODEL` variable to the desired model name. For example:
   ```python
   OPENAI_MODEL = "gpt-3.5-turbo"
   ```

This will ensure that the specified model is used for generating decision trees during the exploration process.

## Usage

1. Run the main script:
   ```
   python main.py
   ```

2. The script will:
   - Start a Flask web server
   - Create an Ngrok tunnel for webhook handling (if enabled)
   - Initiate the first call and begin the exploration process

3. The exploration will continue automatically, making new calls as needed to explore unknown paths in the decision tree.

4. To stop the exploration, use Ctrl+C. A summary of the exploration, including call recording URLs and the final decision tree, will be printed.

### Seeding with an Existing Decision Tree

You can seed the exploration with an existing decision tree by providing a JSON file using the `--seed` argument. This is useful for continuing previous explorations or testing with known data.

Sometimes the decision tree will get stuck in a loop. If this happens, you can seed the exploration with a known good decision tree to continue the exploration.

```
python main.py --seed path/to/decision_tree.json
```

- `path/to/decision_tree.json`: Replace this with the path to your JSON file containing the initial decision tree.

## Configuration

You can modify the following files to customize the behavior:

- `config.py`: Contains API endpoints and other configuration variables
- `prompts.py`: Defines the prompts used for the AI agents and decision tree generation

## Webhooks and Ngrok

The AI Call Tree Explorer uses webhooks to receive updates about call status and recordings. For local development, we use Ngrok to create a secure tunnel to your localhost. In production environments, you can use your own webhook URL.

### Local Development with Ngrok

1. Make sure you have an Ngrok account and have installed the Ngrok CLI.
2. In `config.py`, set `USE_NGROK = True`.
3. Run the script as usual. It will automatically create an Ngrok tunnel and use it for webhooks.

### Production Environment

1. In `config.py`, set `USE_NGROK = False`.
2. Set the `WEBHOOK_URL` variable in `config.py` to your production webhook URL:
   ```python
   WEBHOOK_URL = "https://your-production-url.com/webhook"
   ```
3. Ensure that your production server is set up to handle POST requests to the `/webhook` endpoint.

By configuring these settings, you can easily switch between using Ngrok for local development and your production URL for deployment.

## Output

- call ids, transcripts, and decision trees are saved as JSON files in the `data` folder
- A summary of the exploration is printed at the end, including call recording URLs and the final decision tree
