# Context Management Solution for Token Usage

## Problem

Deep Agents were experiencing token explosion, growing from ~7K to ~105K tokens during execution due to large tool outputs accumulating in the message history.

## Root Cause

As identified in the Deep Agents documentation:
> "Context engineering is a main challenge in building effective agents. This is particularly difficult when using tools that return variable-length results (for example, web_search and rag), as long tool results can quickly fill your context window."

Tool outputs (especially bash commands, file reads, API responses) were being kept in full in the conversation history, causing exponential context growth.

## Solution

We implemented a **three-tier context management strategy**:

### 1. Agent Education (System Prompt)

Updated the system prompt to teach the agent best practices:
- **Write large outputs to files immediately** using `write_file()`
- **Read files selectively** with line limits
- **Keep only summaries in conversation**, store raw data in files
- **Use descriptive filenames** for easy reference

**Example pattern taught to agent:**
```
1. Run: bash("ps aux")
2. Immediately: write_file("process_list.txt", <output>)
3. Continue with: "Saved to process_list.txt. Found 47 processes..."
```

### 2. Intelligent Output Management (Tool Level)

Created `manage_large_output()` function that:

- **Small outputs (<2K chars)**: Pass through unchanged
- **Medium outputs (2K-4K chars)**: Add helpful tip suggesting file storage
- **Large outputs (>4K chars)**: Auto-summarize:
  - Show first 2000 characters
  - Show last 1000 characters
  - Display statistics (char count, line count)
  - Prompt agent to save full output with `write_file()`

This preserves agent's ability to see results while preventing context explosion.

### 3. Message History Trimming (LangGraph Middleware)

Implemented `trim_messages_middleware` using LangGraph's `@before_model` decorator:
- Keeps first message (system prompt)
- Keeps last 20 messages (configurable)
- Removes older messages to prevent unbounded growth

## Files Modified

1. **`autonomous_agent.py`**
   - Updated system prompt with context management guidelines
   - Integrated context middleware

2. **`custom_tools.py`**
   - Added `manage_large_output()` function
   - Applied to `bash()` and `fetch_url()` tools

3. **`context_middleware.py`** (new)
   - Message trimming middleware
   - Output summarization utilities

4. **`test_context_management.py`** (new)
   - Test suite to verify context management works

## Expected Results

- **Token usage**: Should stay under ~15K tokens (vs. 105K before)
- **Agent capability**: Preserved - agent still sees tool results (summarized)
- **Guidance**: Agent receives clear prompts to save large outputs to files
- **Scalability**: Message history trimming prevents unbounded growth

## Configuration

Tunable parameters in `custom_tools.py`:
```python
LARGE_OUTPUT_THRESHOLD = 2000  # When to start suggesting file storage
MAX_OUTPUT_CHARS = 4000        # When to force summarization
```

Tunable parameters in `context_middleware.py`:
```python
MAX_MESSAGES_IN_CONTEXT = 20   # How many messages to keep
```

## Testing

Run the test suite:
```bash
python test_context_management.py
```

This will show:
- Message size distribution
- Whether large outputs were properly managed
- Total context size
- Warnings for any issues

## Future Enhancements

1. **LLM-based summarization**: Use a fast model (gpt-4o-mini) to intelligently summarize large outputs instead of simple truncation
2. **Selective trimming**: Keep important messages (errors, key findings) even if old
3. **Compression**: Compress large text outputs before storing
4. **Command prevention**: Detect and warn about potentially verbose commands upfront
