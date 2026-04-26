"""Provider adapters for R5A operators.

Adapters live here per plan §5.3 step 1 ("instead of forcing every provider
through the existing LLMClient"). Each backend reads its config from the
fleet/runtime files; semantic prompts come from the operators package.

Stub-only at WS0 freeze; concrete adapters are populated in WS1 (vllm
completion + offline HF) and WS2 (openai-compatible, openai-native,
anthropic-native).
"""
