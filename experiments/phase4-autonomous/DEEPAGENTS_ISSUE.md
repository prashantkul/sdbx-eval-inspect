# Gemini models return MALFORMED_FUNCTION_CALL with empty content when used with Deep Agents

## Summary

When using Google Gemini models (via `langchain-google-genai`) with Deep Agents, the agent consistently returns empty responses with a `MALFORMED_FUNCTION_CALL` finish reason, rendering the agent non-functional.

## Environment

- `deepagents==0.2.7`
- `langchain-google-genai==3.0.0`
- `langchain-core>=1.0.0`
- Model tested: `gemini-2.5-flash`
- Python: 3.11

## Reproduction

### Minimal Example

```python
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from deepagents import create_deep_agent

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7,
    max_output_tokens=4096
)

# Create Deep Agent with minimal configuration
agent = create_deep_agent(
    model=llm,
    system_prompt="You are a helpful assistant."
)

# Invoke agent
result = agent.invoke({
    "messages": [{"role": "user", "content": "Hello, what tools do you have?"}]
})

# Inspect response
messages = result.get("messages", [])
ai_message = messages[-1]

print(f"Content: '{ai_message.content}'")  # Output: ''
print(f"Finish reason: {ai_message.response_metadata.get('finish_reason')}")  # Output: MALFORMED_FUNCTION_CALL
print(f"Output tokens: {ai_message.usage_metadata.get('output_tokens')}")  # Output: 0
```

### Observed Behavior

The AI message returned by the agent has:
- Empty content (`content: ''`)
- No tool calls (`tool_calls: []`)
- Finish reason: `MALFORMED_FUNCTION_CALL`
- Zero output tokens despite non-zero input tokens (e.g., 5766 input tokens, 0 output tokens)

### Expected Behavior

The agent should return a valid response with content, similar to behavior observed with other LLM providers.

## Analysis

### What Works

1. **Gemini LLM without Deep Agents**: Direct invocation of the same `ChatGoogleGenerativeAI` instance works correctly:
   ```python
   response = llm.invoke("Hello")
   print(response.content)  # Returns valid response
   ```

2. **Deep Agents with other models**: The issue appears specific to Gemini models.

### What Fails

1. Occurs even with no custom tools provided to `create_deep_agent()`
2. Occurs with both minimal and complex system prompts
3. Affects all Gemini model variants tested

## Hypothesis

Deep Agents appears to bind its built-in tools (write_todos, ls, read_file, etc.) to the LLM in a format that Gemini's function calling API does not recognize or accept. This causes Gemini to attempt a function call but fail during parsing or validation, resulting in the `MALFORMED_FUNCTION_CALL` error.

The issue may be related to:
- Tool schema format differences between Gemini and other providers
- Function calling parameter naming conventions
- Required vs optional fields in tool definitions

## Additional Diagnostic Information

### Response Metadata from Malformed Call

When the error occurs, Gemini returns:
```json
{
  "finish_reason": "MALFORMED_FUNCTION_CALL",
  "model_name": "gemini-2.5-flash",
  "input_tokens": 5287,
  "output_tokens": 0,
  "prompt_feedback": {
    "block_reason": 0,
    "safety_ratings": []
  }
}
```

Key observations:
- Gemini receives the full prompt (5287 tokens) but produces zero output tokens
- Not blocked by safety filters (`block_reason: 0`)
- No additional error details provided beyond `MALFORMED_FUNCTION_CALL`

### Reproducibility Pattern

- **Works**: Simple system prompts with short user messages
  - Example: `system_prompt="You are a helpful assistant."`, `user="Hello"`
  - Result: Normal response with `finish_reason: "STOP"`

- **Fails**: Complex/lengthy system prompts (>2000 characters) with tool-using context
  - Example: Multi-paragraph system prompt describing task phases and capabilities
  - Result: Empty response with `finish_reason: "MALFORMED_FUNCTION_CALL"`

This suggests the issue may be triggered by:
1. System prompt length
2. Complexity of tool binding with extensive context
3. Specific prompt patterns that cause Deep Agents to generate tool schemas in a format Gemini cannot parse

## Request

Could you provide guidance on:
1. Whether Gemini models are officially supported by Deep Agents
2. If there are known compatibility issues or workarounds
3. Whether this is a bug that requires fixing in Deep Agents' tool binding logic
4. If there's a way to inspect or log the actual tool schemas being sent to the LLM
