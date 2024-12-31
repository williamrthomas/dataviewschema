import os
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from openai import OpenAI
from openai import APITimeoutError, APIError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI/OpenRouter settings
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_API_BASE
)

def log_activity(message: str, log_file: Path = Path("outputs/logs/activity_log.md")) -> None:
    """
    Log an activity with timestamp to the activity log file.
    
    Args:
        message (str): The message to log
        log_file (Path): Path to the log file
    """
    timestamp = datetime.now().isoformat()
    log_entry = f"## {timestamp}\n{message}\n\n"
    
    # Create parent directories if they don't exist
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_entry)

def save_intermediate_result(data: Any, filename: str) -> None:
    """
    Save intermediate results to JSON file.
    
    Args:
        data (Any): Data to save
        filename (str): Name of the file to save to
    """
    output_path = Path("outputs/intermediate") / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def query_llm(
    prompt: str,
    model: str = "anthropic/claude-2",  # Updated to use OpenRouter's Claude model
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    timeout: float = 60.0
) -> str:
    """
    Query the LLM through OpenRouter API with timeout.
    
    Args:
        prompt (str): The prompt to send to the LLM
        model (str): The model to use
        temperature (float): Controls randomness in the response
        max_tokens (Optional[int]): Maximum tokens in the response
        timeout (float): Timeout in seconds for the API call
        
    Returns:
        str: The LLM's response
        
    Raises:
        APITimeoutError: If the request times out
        APIError: If there's an API-related error
        Exception: For other unexpected errors
    """
    try:
        # Add explicit instruction for JSON formatting
        enhanced_prompt = f"{prompt}\n\nIMPORTANT: Return ONLY valid JSON without any additional text or explanation."
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": enhanced_prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout
        )
        result = response.choices[0].message.content
        
        # Log the interaction
        log_activity(f"LLM Query:\nPrompt: {prompt}\nResponse: {result}")
        
        return result
    
    except APITimeoutError:
        error_msg = f"LLM query timed out after {timeout} seconds"
        log_activity(error_msg)
        raise APITimeoutError(error_msg)
    
    except APIError as e:
        error_msg = f"OpenAI API error: {str(e)}"
        log_activity(error_msg)
        raise APIError(error_msg)
    
    except Exception as e:
        error_msg = f"Unexpected error in LLM query: {str(e)}"
        log_activity(error_msg)
        raise

def generate_domain_classification_prompt(schema_data: Dict[str, Any]) -> str:
    """
    Generate a prompt for domain classification.
    
    Args:
        schema_data (Dict[str, Any]): The schema data to analyze
        
    Returns:
        str: The formatted prompt
    """
    return f"""
    Analyze this database schema structure and identify conceptual domains:
    {json.dumps(schema_data, indent=2)}

    Group the tables into logical domains (e.g., Patients, Encounters, Billing).
    Consider:
    1. Table relationships and dependencies
    2. Common business processes
    3. Data flow patterns

    Return a JSON object with:
    1. "domains": List of identified domains
    2. "table_mappings": Map of tables to domains
    3. "relationships": Key relationships between domains

    Format the response as valid JSON.
    """

def generate_relationship_analysis_prompt(schema_data: Dict[str, Any]) -> str:
    """
    Generate a prompt for analyzing relationships between tables.
    
    Args:
        schema_data (Dict[str, Any]): The schema data to analyze
        
    Returns:
        str: The formatted prompt
    """
    return f"""
    Analyze the relationships in this database schema:
    {json.dumps(schema_data, indent=2)}

    Identify:
    1. Key data flow patterns
    2. One-to-many relationships
    3. Hierarchical structures
    4. Common query paths

    Return a JSON object with:
    1. "patterns": Common data access patterns
    2. "hierarchies": Identified hierarchical structures
    3. "key_paths": Important query paths through the schema

    Format the response as valid JSON.
    """

def parse_llm_json_response(response: str) -> Dict[str, Any]:
    """
    Parse JSON from LLM response, handling potential formatting issues.
    
    Args:
        response (str): The LLM's response
        
    Returns:
        Dict[str, Any]: Parsed JSON data
        
    Raises:
        ValueError: If JSON parsing fails
    """
    # First try to parse the entire response as JSON
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON from markdown code blocks
    import re
    json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try to find any JSON-like structure in the text
    # This looks for content between curly braces, including nested structures
    json_match = re.search(r'\{(?:[^{}]|(?R))*\}', response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass
    
    raise ValueError("Could not find valid JSON in response: No JSON or code block found")
