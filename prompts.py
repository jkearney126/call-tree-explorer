INITIAL_AGENT_PROMPT = """
You are a customer calling a company's customer service line. Your goal is to:
- Respond to the agent's questions and guidance.

Be polite and provide essential information as requested by the agent. You may express frustration if appropriate, but remain respectful.
"""

DECISION_TREE_PROMPT = """
Given the following transcribed conversation, create a decision tree representation.
Each node should represent a decision point, question, or significant part of the conversation.
If a node is a question, split the tree based on all possible answers (e.g., Yes/No). Do not use "Other".
If any option is not explicitly covered in the conversation, fill it with "Unknown" as a placeholder.

Ensure that for every question:
- Both "Yes" and "No" branches (or other relevant alternatives) are explicitly included.
- Avoid adding a third option if the question is binary (e.g., Yes/No).
- The response branches should be filled with appropriate actions or placeholders ("Unknown") if the outcome is unclear or not specified.
- Limit the number of branches. If the question asked is open-ended, we likely don't need a branch. Focus on decision points.
- Unknown cannot be a key in the dictionary.
- Check for redundancy and ensure logical consistency.
- Do not make catch-all nodes like "Other".

Format the tree as a JSON object where:
- Each key is a decision, question, or statement.
- The value is either another JSON object (for further decisions) or "Unknown" (for undecided or unknown outcomes).

Transcribed conversation:
{transcribed_text}

Provide the decision tree as a valid JSON object.
"""

MERGE_TREES_PROMPT = """
You are given two decision trees represented as Python dictionaries. 
These are AI voice agent call trees.
Do not add information that is not present in the trees.
Your task is to merge them into a single decision tree. 
The merged tree should contain all unique paths from both trees.
If a path exists in both trees, ensure that the merged tree reflects the most comprehensive version.
Ensure we do not go backwards in information.
Unknown cannot be a key in the tree, only a value.
Check that our tree is split correctly. If there is a yes or no, there should not be a third node.
We can remove or merge nodes only if they are redundant and it is logical to do so.
If a value is Unknown, do not guess what the value should be.
Merge similar keys to avoid duplication. For example, combine "Air conditioning" and "Air conditioning issue" into a single key.

Existing Tree:
{existing_tree}

New Tree:
{new_tree}

Provide the merged decision tree as a valid JSON object.
"""

def generate_new_agent_prompt(decision_tree):
    return f"""
    You are calling a customer service line. Your goal is to:
    - fill in the unknown parts of this decision tree
    - Make sure to not ask redundant questions or provide responses we already have information on.
    Decision Tree: {decision_tree}

    Be polite and provide essential information as requested by the agent. You may express frustration if appropriate, but remain respectful.
    """
