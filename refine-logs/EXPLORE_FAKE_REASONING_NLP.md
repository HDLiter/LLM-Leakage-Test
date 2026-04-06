# Fake Reasoning and Context: NLP View

1. **If the final serialized prefix is identical, there is no extra "self-generated" memory.** In a standard autoregressive transformer, next-token logits are a function of the prefix tokens, positions, and chat-template tokens. The KV cache built while generating a prefix is the same cache you would get by prefilling that same prefix. So, in theory, self-generated vs injected context differ only when the actual serialized input differs.

2. **So A-real and B-real collapse if and only if the model sees the exact same token sequence with the same role markup.** Under greedy decoding they should match exactly; under sampling they should define the same distribution. If they do not, the cause is usually implementation-level: different chat roles, separators, truncation, hidden system/tool text, or nondeterministic serving.

3. **The subtlety is provenance formatting, not hidden residual computation.** In chat models, "assistant previously wrote X" and "user provides X" are different prefixes because role tokens differ. The model can also respond differently to cues like "your prior analysis," "quoted note," or "draft." So your 2x2 is only nontrivial if A and B differ in serialization or discourse role. If you literalize the same analysis into the same prefix, the A/B distinction disappears.

4. **For S3, this makes decomposition mainly a context-engineering hypothesis.** Least-to-Most and context-faithful prompting fit this well: an earlier grounded step helps because its output becomes conditioning context for the later decision. A strong "computational forcing" claim is too much for black-box prompt chaining unless some hidden scratchpad or architectural bottleneck exists. In that sense, your current 2x2 is really `content quality (real vs sham) x provenance/format`, not `context x computation`.

5. **This is why the faithfulness literature matters.** Turpin et al. show that visible CoT can be unfaithful: the model may emit plausible authority analysis and still answer from parametric memory. By contrast, Lei et al. and FRESH are stronger because the rationale is causally tied to prediction; the downstream classifier only sees the selected evidence or rationale. So an S3-style prompt can show that decomposition steers behavior, but not that the model genuinely reasoned through that decomposition.

6. **A better experiment has three parts.**
- Run an **equivalence control**: generated-prefix vs injected-prefix with identical serialized tokens. They should match.
- Then vary only **provenance/role**: same analysis string as prior assistant turn, user-supplied note, or inline appendix. This measures discourse-format effects.
- To test **computation beyond context**, use a **causal bottleneck**: an extractor produces evidence spans or slots, and the predictor sees only those outputs, not the full article. Stronger still, with a white-box model, hold visible context fixed and vary an unexposed scratchpad or use activation patching. That is the real computation-vs-context test.
