# AI Call Tree Explorer

## Description

The AI Call Tree Explorer is an automated system designed to discover and map out conversation trees or decision graphs through simulated phone calls. It uses AI-powered agents to conduct conversations, transcribe the calls, and generate decision trees based on the interactions.


## Prerequisites

- Python 3.7+
- OpenAI API key
- Ngrok account (for webhook tunneling)
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

## Usage

1. Run the main script:
   ```
   python main.py
   ```

2. The script will:
   - Start a Flask web server
   - Create an Ngrok tunnel for webhook handling
   - Initiate the first call and begin the exploration process

3. The exploration will continue automatically, making new calls as needed to explore unknown paths in the decision tree.

4. To stop the exploration, use Ctrl+C. A summary of the exploration, including call recording URLs and the final decision tree, will be printed.

## Configuration

You can modify the following files to customize the behavior:

- `config.py`: Contains API endpoints and other configuration variables
- `prompts.py`: Defines the prompts used for the AI agents and decision tree generation

## Output

- Decision trees are saved as JSON files in the `dt_json` folder
- A summary of the exploration is printed at the end, including call recording URLs and the final decision tree

