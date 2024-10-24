import requests
import threading
import time
import uuid
import json
import os
from typing import Dict
import openai
from pyngrok import ngrok
from web_server import create_app, run_flask_app
from config import API_TOKEN, OPENAI_API_KEY, TEST_PHONE_NUMBER, START_CALL_ENDPOINT, GET_RECORDING_ENDPOINT
from prompts import INITIAL_AGENT_PROMPT, DECISION_TREE_PROMPT, MERGE_TREES_PROMPT, generate_new_agent_prompt


class CallTreeExplorer:
    """
    Automates the call tree/graph discovery process.

    Methods:
        start_exploration(): Starts the exploration process.
    """
    def __init__(self, agent_prompt: str):
        self.agent_prompt = agent_prompt
        self.session = requests.Session()
        self.session.headers.update({'Authorization': f'Bearer {API_TOKEN}'})
        self.active_calls = {}
        self.conversation_tree = {}
        self.ngrok_tunnel = self.create_ngrok_tunnel()
        self.webhook_url = f"{self.ngrok_tunnel.public_url}/webhook"
        self.max_depth = 3
        openai.api_key = OPENAI_API_KEY
        self.call_recordings = []  # New attribute to store call recording URLs

    def create_ngrok_tunnel(self):
        """
        Creates an ngrok tunnel to expose the local server.

        Returns:
            NgrokTunnel: The created ngrok tunnel.
        """
        try:
            # You may need to set your ngrok auth token here if you haven't done it before
            # ngrok.set_auth_token("YOUR_NGROK_AUTH_TOKEN")
            return ngrok.connect(5000)
        except Exception as e:
            print(f"Failed to create ngrok tunnel: {str(e)}")
            raise

    def start_exploration(self):
        """
        Starts the conversation exploration process.
        """
        print("Starting conversation exploration...")
        self.initiate_call()


    def initiate_call(self):
        """
        Initiates a call with a given customer input.

        Args:
            customer_input (str): The customer's initial input.
        """
        call_id = str(uuid.uuid4())
        data = {
            'phone_number': TEST_PHONE_NUMBER,
            'prompt': self.agent_prompt,
            'webhook_url': self.webhook_url,
        }
        print(self.webhook_url)
        response = self.session.post(START_CALL_ENDPOINT, json=data)
        if response.status_code == 200:
            call_response = response.json()
            self.active_calls[call_response['id']] = {
                'call_id': call_id,
                'conversation': []
            }
            print(f"Call initiated with ID: {call_response['id']}")
        else:
            print(f"Failed to initiate call: {response.text}")

    def handle_webhook(self, payload: Dict):
        """
        Handles the webhook notifications.

        Args:
            payload (Dict): The webhook payload.
        """
        call_id = payload['id']
        status = payload['status']
        recording_available = payload.get('recording_available', False)
        print(f"Received webhook for call ID: {call_id}, Status: {status}")

        if recording_available:
            print(f"Recording available for call ID: {call_id}")
            self.retrieve_and_process_recording(call_id)

    def retrieve_and_process_recording(self, call_id: str):
        """
        Retrieves and processes the call recording.

        Args:
            call_id (str): The call ID.
        """
        params = {'id': call_id}
        response = self.session.get(GET_RECORDING_ENDPOINT, params=params)
        if response.status_code == 200:
            audio_content = response.content
            transcript = self.transcribe_audio(audio_content)
            print(transcript)
            dt = self.create_decision_tree(transcript)
            self.conversation_tree = self.merge_decision_trees_with_openai(self.conversation_tree, dt)
            print("Merged Decision Tree:")
            print(json.dumps(self.conversation_tree, indent=2))
            
            # Store the recording URL
            recording_url = f"{GET_RECORDING_ENDPOINT}?id={call_id}"
            self.call_recordings.append(recording_url)
            
            if self.find_unknowns_in_tree(self.conversation_tree):
                print("Decision tree contains unknown paths. Initiating another call.")
                self.call_agent_with_new_prompt(self.conversation_tree)
                return
            else:
                print("Tree complete")
                self.print_summary()
        else:
            print(f"Failed to retrieve recording: {response.text}")

    def find_unknowns_in_tree(self, decision_tree, current_path=None):
        """
        Recursively searches the decision tree for any nodes with the value 'Unknown'.
        
        Args:
            decision_tree (dict): The decision tree represented as a nested dictionary.
            current_path (list): The path taken through the tree to reach the current node.
            
        Returns:
            list: A list of paths where 'Unknown' is found. Each path is a list of keys leading to the 'Unknown' value.
        """
        if current_path is None:
            current_path = []
        
        unknown_paths = []

        for key, value in decision_tree.items():
            # If the value is "Unknown", add the current path + key to the list of unknown paths
            if value == "Unknown":
                unknown_paths.append(current_path + [key])
            # If the value is a dictionary, recursively search through it
            elif isinstance(value, dict):
                unknown_paths.extend(self.find_unknowns_in_tree(value, current_path + [key]))

        return unknown_paths

    def transcribe_audio(self, audio_content: bytes) -> str:
        """
        Transcribes the audio content using OpenAI's Whisper model.

        Args:
            audio_content (bytes): The audio content.

        Returns:
            str: The transcribed text.
        """
        with open('temp_audio.mp3', 'wb') as f:
            f.write(audio_content)

        try:
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            with open('temp_audio.mp3', 'rb') as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
            return transcript.text
        except Exception as e:
            print(f"Transcription error: {str(e)}")
            return ""
        finally:
            os.remove('temp_audio.mp3')

    def create_decision_tree(self, transcribed_text: str) -> dict:
        """
        Creates a decision tree from the transcribed text using OpenAI's GPT model.

        Args:
            transcribed_text (str): The transcribed conversation.

        Returns:
            dict: A decision tree representation of the conversation.
        """
        try:
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            prompt = DECISION_TREE_PROMPT.format(transcribed_text=transcribed_text)

            response = client.chat.completions.create(
                model="gpt-4o",
                response_format={
                    "type": "json_object"
                },
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates decision trees from conversations."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Print the response for debugging
            decision_tree_str = response.choices[0].message.content.strip()
            print("Response from OpenAI:", decision_tree_str)

            # Attempt to parse the response as JSON
            decision_tree = json.loads(decision_tree_str)
            # Remove "Unknown" keys from the decision tree
            def remove_unknown_and_other_keys(tree):
                if isinstance(tree, dict):
                    return {k: remove_unknown_and_other_keys(v) for k, v in tree.items() if k not in ["Unknown", "Other"]}
                elif isinstance(tree, list):
                    return [remove_unknown_and_other_keys(item) for item in tree]
                else:
                    return tree

            decision_tree = remove_unknown_and_other_keys(decision_tree)
            # Save the decision tree
            self.save_decision_tree(decision_tree)

            return decision_tree
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            return {}
        except Exception as e:
            print(f"Error creating decision tree: {str(e)}")
            return {}

    def save_decision_tree(self, decision_tree: dict):
        """
        Saves the decision tree to a file in the dt_json folder.

        Args:
            decision_tree (dict): The decision tree to save.
        """
        # Create the dt_json folder if it doesn't exist
        os.makedirs('dt_json', exist_ok=True)
        
        filename = f"dt_json/decision_tree_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(decision_tree, f, indent=4)
        print(f"Decision tree saved to {filename}")

    def call_agent_with_new_prompt(self, dt):
        """
        Calls the agent with a new prompt for decision change.

        Args:
            prompt (str): The prompt for the decision change.
        """
        agent_prompt = generate_new_agent_prompt(dt)
        self.agent_prompt = agent_prompt
        self.initiate_call()
        

    def merge_decision_trees_with_openai(self, existing_tree: dict, new_tree: dict) -> dict:
        """
        Merges a new decision tree with an existing one using OpenAI.

        Args:
            existing_tree (dict): The existing decision tree.
            new_tree (dict): The new decision tree to merge.

        Returns:
            dict: The merged decision tree.
        """
        try:
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            prompt = MERGE_TREES_PROMPT.format(existing_tree=existing_tree, new_tree=new_tree)

            response = client.chat.completions.create(
                model="gpt-4o",
                response_format={
                    "type": "json_object"
                },
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that merges decision trees."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Parse the response as JSON
            merged_tree_str = response.choices[0].message.content.strip()
            merged_tree = json.loads(merged_tree_str)

            return merged_tree
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            return existing_tree
        except Exception as e:
            print(f"Error merging decision trees: {str(e)}")
            return existing_tree

    def print_summary(self):
        """
        Prints a summary of the exploration, including call recording URLs and the final decision tree.
        """
        print("\n=== Exploration Summary ===")
        print("Call Recording URLs:")
        for i, url in enumerate(self.call_recordings, 1):
            print(f"Call {i}: {url}")
        
        print("\nFinal Decision Tree:")
        print(json.dumps(self.conversation_tree, indent=2))
        print("=== End of Summary ===\n")

def main():
    """
    Main function to start the conversation exploration.
    """
    global explorer
    explorer = CallTreeExplorer(agent_prompt=INITIAL_AGENT_PROMPT)

    # Create Flask app
    app = create_app(explorer)

    # Start Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask_app, args=(app,))
    flask_thread.daemon = True
    flask_thread.start()

    # Wait for the Flask app to start
    time.sleep(2)

    # Start conversation exploration
    explorer.start_exploration()

    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        explorer.print_summary()  # Print summary before shutting down
        ngrok.kill()  # Make sure to kill the ngrok process on exit

if __name__ == "__main__":
    main()
