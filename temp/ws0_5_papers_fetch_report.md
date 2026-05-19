# WS0.5 Round-0 Papers Fetch Report

**Timestamp:** 2026-05-19T05:44:48-07:00  
**Source sweep:** `temp/ws0_5_autotune_sota_search.md`

## Summary

- Paper PDFs requested: 22
- Successfully fetched and validated: 22
- Failed paper fetches: 0
- Existing-library duplicates skipped: 0
- Industry/docs/blog references skipped as PDFs and added as `REFERENCED_ONLY`: 9
- PDF count: 136 -> 158 (+22)
- `PAPER_INDEX.md` line count: 265 -> 317 (+52)
- Machine catalog: `related papers/notes/_paper_catalog.json` now has `paper_count=158` and 158 paper records.

Transport note: Windows `curl.exe` failed locally with a Schannel credential error before HTTP response. Python `urllib` fetched the same URLs successfully; every saved paper passed `%PDF-` header validation and sha256 hashing.

## Added PDF Records

| Filename | Source URL | sha256 |
|---|---|---|
| `DSPy Declarative LM Pipelines.pdf` | https://arxiv.org/pdf/2310.03714.pdf | `5309836325c3a580b6c176242f49f21ca40e413b0acd514e74b67e16bb1b56bc` |
| `MIPRO Instructions Demonstrations LM Programs.pdf` | https://arxiv.org/pdf/2406.11695.pdf | `f00093af256c7b3e5168c2e98fbb8c4847232a8838c91baad4540cb4f19c91f7` |
| `GEPA Reflective Prompt Evolution.pdf` | https://arxiv.org/pdf/2507.19457.pdf | `ab3a5139bac83f192ad67529368d77b84b0d807e95a8e4fd0daa8d45fd046bec` |
| `TextGrad Automatic Differentiation via Text.pdf` | https://arxiv.org/pdf/2406.07496.pdf | `9cbfd5c78ad69e2a8363e76d6774f3e6b5e68f46b409d8b560e98276a985b428` |
| `ProTeGi Automatic Prompt Optimization.pdf` | https://arxiv.org/pdf/2305.03495.pdf | `90ed9bd62d8e8c1f5bb810c7749c8272f2de4cac037cb75306746c9c9cfcb094` |
| `OPRO Large Language Models as Optimizers.pdf` | https://arxiv.org/pdf/2309.03409.pdf | `61c8493c964f6d4436f69ae63ff52d3a91540708e9387615f3a8f034bab081c0` |
| `PromptWizard Task Aware Prompt Optimization.pdf` | https://arxiv.org/pdf/2405.18369.pdf | `63b977a57c34a77b6a688b5a35a9bcdc077266b4824c7ee8c6f7ded5396e6620` |
| `EvoPrompt Evolutionary Prompt Optimizers.pdf` | https://arxiv.org/pdf/2309.08532.pdf | `776a3f4ac1f2a321761eae0332320773d08ba7a260939296d8a979f67d82a627` |
| `Automatic Prompt Engineer Human Level Prompt Engineers.pdf` | https://arxiv.org/pdf/2211.01910.pdf | `b4162f38101db7511e6292a2577c66514c757824ddd21f8426a6276485355e81` |
| `Auto-CoT Automatic Chain of Thought Prompting.pdf` | https://arxiv.org/pdf/2210.03493.pdf | `aab4ba4d574c32c61a7c4136d89d60b07baf368b63f86b852d620ef4e5a64909` |
| `Reusable Holdout Adaptive Data Analysis.pdf` | https://arxiv.org/pdf/1506.02629.pdf | `dcfbb9aa401c62949123be2d74787c4f9cca48597f18860760ef1580ddb4bc71` |
| `Generic Holdout Adaptive Data Science.pdf` | https://arxiv.org/pdf/1809.05596.pdf | `2c64529b9e5381fa7a2d39f2c6920e45d98370ce1a7534e4ef5985372b92799d` |
| `Ladder Reliable Leaderboard.pdf` | https://proceedings.mlr.press/v37/blum15.pdf | `196fd444c506199c321e973ca101f4715055972a42ba77fd0de43324f9b974d7` |
| `Always Valid Inference AB Testing.pdf` | https://arxiv.org/pdf/1512.04922.pdf | `5c2d29ac484612920373cb6c0f3896456260883e97a833dadb5cb1ac0be9590c` |
| `Hitchhikers Guide Statistical Significance NLP.pdf` | https://aclanthology.org/P18-1128.pdf | `e3b6e07cf7e404443e4b516db9b2a72c5d24a38285a9a6691ed2e3b01b02235b` |
| `Error Bars to Evals.pdf` | https://arxiv.org/pdf/2411.00640.pdf | `22570aaf1313c7ab8861d2373f0e8e90c160f6c69c8960aecbb4733c48b22149` |
| `Dont Use CLT in LLM Evals.pdf` | https://arxiv.org/pdf/2503.01747.pdf | `b09606e94fd3574a05dfe362b63e0c3b418b4747df5fdd62969c92f0225fe682` |
| `Active Learning for NLP Survey.pdf` | https://aclanthology.org/2022.emnlp-main.414.pdf | `1c006b52b53041f05d21e0b302001eef5e6b7740da925359381dc1b2b4b6d207` |
| `LLMs in the Loop Active Learning Annotation.pdf` | https://arxiv.org/pdf/2404.02261.pdf | `115385e13b6ea481e6c82c122932f708126555e10aa84adeaa66830a1ccab59f` |
| `LLM Assisted Annotation Subjective Tasks.pdf` | https://arxiv.org/pdf/2507.15821.pdf | `9297ea0b0ee5abd2b38655be7943ed9c45302008348fa8c7b911a427cafbe4e8` |
| `ActiveAED Annotation Error Detection.pdf` | https://arxiv.org/pdf/2305.20045.pdf | `3aca34a056d77d22332f65fb9dea78d5093c9810de6032c5b99b8153208d73a9` |
| `Skill-KNN Few-Shot Selection.pdf` | https://aclanthology.org/2023.emnlp-main.831.pdf | `6c93970dc2925dc4d79998ed7efd4ce6cd6f6826e29afb010dc8ac2a888b102b` |

## PAPER_INDEX Updates

Added four new sections:

- `16. Prompt optimization frameworks (WS0.5 round-0)`
- `17. Adaptive analysis & multiple-comparison discipline (WS0.5 round-0)`
- `18. NLP statistical tests & evaluation discipline (WS0.5 round-0)`
- `19. Annotation methodology (WS0.5 round-0)`

Added one referenced-only documentation subsection with the nine industry/docs/blog URLs from the round-0 search.

## New Notes

- `related papers/notes/prompt_optimization.md` (23 lines)
- `related papers/notes/adaptive_analysis_reusable_holdout.md` (13 lines)

## Failed Fetches

None.

## Additional Notes

- No listed round-0 paper was already indexed in `PAPER_INDEX.md`, so no duplicate PDFs were skipped.
- Industry docs and blogs were not converted to PDFs; they are represented as `REFERENCED_ONLY` URLs in `PAPER_INDEX.md`.
