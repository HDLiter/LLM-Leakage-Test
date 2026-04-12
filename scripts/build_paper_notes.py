from __future__ import annotations

import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RELATED_DIR = PROJECT_ROOT / "related papers"
NOTES_DIR = RELATED_DIR / "notes"
CATALOG_PATH = NOTES_DIR / "_paper_catalog.json"


CATEGORY_FILES: list[tuple[str, str]] = [
    ("Memorization & Training Data Extraction", "memorization_extraction.md"),
    ("Benchmark Contamination & Leakage Detection", "contamination_detection.md"),
    ("Temporal Knowledge & Look-Ahead Bias", "temporal_lookahead.md"),
    ("Knowledge Editing & Localization", "knowledge_editing.md"),
    ("Factual Grounding & Knowledge Conflicts", "grounding_conflicts.md"),
    ("Mechanistic Interpretability & Internal Representations", "mechanistic_interpretability.md"),
    ("Financial NLP & Sentiment Analysis", "financial_nlp.md"),
    ("Prompting & Reasoning Techniques", "prompting_reasoning.md"),
    ("Calibration, Uncertainty & Robustness", "calibration_robustness.md"),
    ("Memory Systems & Cognitive Framing", "memory_cognitive.md"),
]


CATEGORY_MAP: dict[str, str] = {
    "A Test of Lookahead Bias in LLM Forecasts.pdf": "Temporal Knowledge & Look-Ahead Bias",
    "All Leaks Count, Some Count More Interpretable Temporal.pdf": "Temporal Knowledge & Look-Ahead Bias",
    "Anchor Regression Heterogeneous Causality.pdf": "Calibration, Uncertainty & Robustness",
    "AntiLeakBench Preventing Contamination.pdf": "Benchmark Contamination & Leakage Detection",
    "Assessing Look-Ahead Bias GPT Sentiment.pdf": "Temporal Knowledge & Look-Ahead Bias",
    "BaseCal Unsupervised Confidence Calibration.pdf": "Calibration, Uncertainty & Robustness",
    "Causal View Entity Bias LLMs.pdf": "Mechanistic Interpretability & Internal Representations",
    "CFinBench Chinese Financial Benchmark.pdf": "Financial NLP & Sentiment Analysis",
    "Chain-of-Note Enhancing RAG Robustness.pdf": "Factual Grounding & Knowledge Conflicts",
    "Chain-of-Verification Reduces Hallucination.pdf": "Factual Grounding & Knowledge Conflicts",
    "CHiLL Zero-Shot Feature Extraction Clinical.pdf": "Prompting & Reasoning Techniques",
    "Chronologically Consistent Large Language Models.pdf": "Temporal Knowledge & Look-Ahead Bias",
    "Closer Look at Memorization in Deep Networks.pdf": "Memorization & Training Data Extraction",
    "Company-specific Biases Financial Sentiment LLMs.pdf": "Financial NLP & Sentiment Analysis",
    "Context-faithful Prompting for LLMs.pdf": "Factual Grounding & Knowledge Conflicts",
    "Context-Faithfulness Memory Strength Evidence.pdf": "Factual Grounding & Knowledge Conflicts",
    "Co-occurrence Not Factual Association.pdf": "Mechanistic Interpretability & Internal Representations",
    "Counterfactual Memorization in Neural Language Models.pdf": "Memorization & Training Data Extraction",
    "Cutting Off Head Knowledge Conflicts.pdf": "Factual Grounding & Knowledge Conflicts",
    "Dated Data Tracing Knowledge Cutoffs.pdf": "Temporal Knowledge & Look-Ahead Bias",
    "DatedGPT Preventing Lookahead Bias.pdf": "Temporal Knowledge & Look-Ahead Bias",
    "Detecting Pretraining Data from Large Language Models.pdf": "Memorization & Training Data Extraction",
    "Disentangling Memory and Reasoning in LLMs.pdf": "Prompting & Reasoning Techniques",
    "Dissecting Recall Factual Associations.pdf": "Mechanistic Interpretability & Internal Representations",
    "Do Membership Inference Attacks Work on Large Language Models.pdf": "Memorization & Training Data Extraction",
    "Does Localization Inform Editing.pdf": "Knowledge Editing & Localization",
    "ECC Analyzer Trading Signal Earnings Calls.pdf": "Financial NLP & Sentiment Analysis",
    "Entity Cells Language Models.pdf": "Mechanistic Interpretability & Internal Representations",
    "Entity Identification Language Models.pdf": "Mechanistic Interpretability & Internal Representations",
    "Entity Knowledge Conflicts QA.pdf": "Factual Grounding & Knowledge Conflicts",
    "Entity-level Memorization in LLMs.pdf": "Memorization & Training Data Extraction",
    "Episodic Memories Benchmark LLMs.pdf": "Memory Systems & Cognitive Framing",
    "Extracting Training Data from LLMs 2020.pdf": "Memorization & Training Data Extraction",
    "Fake Date Tests LLM Macro Forecasting.pdf": "Temporal Knowledge & Look-Ahead Bias",
    "FFN Key-Value Memories Transformers.pdf": "Mechanistic Interpretability & Internal Representations",
    "FinDPO Financial Sentiment Preference Optimization.pdf": "Financial NLP & Sentiment Analysis",
    "FinGPT Dissemination-Aware Context-Enriched LLMs.pdf": "Mechanistic Interpretability & Internal Representations",
    "Generalization or Memorization Data Contamination.pdf": "Benchmark Contamination & Leakage Detection",
    "How Much are LLMs Contaminated LLMSanitize.pdf": "Benchmark Contamination & Leakage Detection",
    "How Well Do LLMs Truly Ground.pdf": "Factual Grounding & Knowledge Conflicts",
    "Interpretable Probability Estimation Shapley.pdf": "Calibration, Uncertainty & Robustness",
    "Invariant Risk Minimization.pdf": "Calibration, Uncertainty & Robustness",
    "Investigating Data Contamination in Modern Benchmarks.pdf": "Benchmark Contamination & Leakage Detection",
    "Kernel Language Entropy Uncertainty Quantification.pdf": "Calibration, Uncertainty & Robustness",
    "Knowledge Neurons Pretrained Transformers.pdf": "Knowledge Editing & Localization",
    "Language Models Represent Space Time.pdf": "Temporal Knowledge & Look-Ahead Bias",
    "Leakage Reproducibility Crisis ML Science.pdf": "Benchmark Contamination & Leakage Detection",
    "Least-to-Most Prompting Complex Reasoning.pdf": "Prompting & Reasoning Techniques",
    "LiveBench A Challenging Contamination-Limited Benchmark.pdf": "Benchmark Contamination & Leakage Detection",
    "LLMFactor Extracting Profitable Factors.pdf": "Financial NLP & Sentiment Analysis",
    "Look-Ahead-Bench Standardized Benchmark.pdf": "Temporal Knowledge & Look-Ahead Bias",
    "Lopez-Lira ChatGPT Stock Returns.pdf": "Financial NLP & Sentiment Analysis",
    "Mechanistic Circuits Extractive QA.pdf": "Factual Grounding & Knowledge Conflicts",
    "MEMIT Mass-Editing Memory Transformer.pdf": "Knowledge Editing & Localization",
    "Memorization Problem LLMs Economic Forecasts.pdf": "Temporal Knowledge & Look-Ahead Bias",
    "Memory GAPS Tulving Test LLMs.pdf": "Memory Systems & Cognitive Framing",
    "Memory Traces Transformers Tulving.pdf": "Memory Systems & Cognitive Framing",
    "MiniCheck Efficient Fact-Checking Grounding.pdf": "Factual Grounding & Knowledge Conflicts",
    "MIRAGE Model Internals Answer Attribution.pdf": "Factual Grounding & Knowledge Conflicts",
    "MMLU-CF Contamination-free Benchmark.pdf": "Benchmark Contamination & Leakage Detection",
    "MQuAKE Knowledge Editing Multi-Hop.pdf": "Knowledge Editing & Localization",
    "Profit_Mirage_Revisiting_Information_Leakage_in_LL.pdf": "Financial NLP & Sentiment Analysis",
    "Propagation Pitfalls Knowledge Editing.pdf": "Knowledge Editing & Localization",
    "Proving Test Set Contamination Black Box.pdf": "Benchmark Contamination & Leakage Detection",
    "Quantifying Memorization Across Neural LMs.pdf": "Memorization & Training Data Extraction",
    "Rationalizing Neural Predictions.pdf": "Prompting & Reasoning Techniques",
    "Reasoning or Reciting Counterfactual Tasks.pdf": "Benchmark Contamination & Leakage Detection",
    "ReEval Hallucination Evaluation RAG.pdf": "Factual Grounding & Knowledge Conflicts",
    "RE-IMAGINE Symbolic Benchmark Synthesis.pdf": "Benchmark Contamination & Leakage Detection",
    "Rethinking Benchmark and Contamination with Rephrased Samples.pdf": "Benchmark Contamination & Leakage Detection",
    "ROME Locating Editing Factual Associations GPT.pdf": "Knowledge Editing & Localization",
    "Scalable Extraction of Training Data from Language Models.pdf": "Memorization & Training Data Extraction",
    "Secret Sharer Unintended Memorization.pdf": "Memorization & Training Data Extraction",
    "Set the Clock Temporal Alignment LMs.pdf": "Temporal Knowledge & Look-Ahead Bias",
    "Stable Prediction Unknown Environments.pdf": "Calibration, Uncertainty & Robustness",
    "Structured Event Representation Stock Return.pdf": "Financial NLP & Sentiment Analysis",
    "Taming Knowledge Conflicts LMs.pdf": "Factual Grounding & Knowledge Conflicts",
    "Task Contamination Not Few-Shot.pdf": "Benchmark Contamination & Leakage Detection",
    "Time Encoded in Weights Finetuned LMs.pdf": "Temporal Knowledge & Look-Ahead Bias",
    "Time Travel in LLMs Tracing Contamination.pdf": "Benchmark Contamination & Leakage Detection",
    "Towards Objective Fine-tuning Calibration.pdf": "Calibration, Uncertainty & Robustness",
    "TRAK Attributing Model Behavior at Scale.pdf": "Mechanistic Interpretability & Internal Representations",
    "Unfaithful Explanations in CoT.pdf": "Prompting & Reasoning Techniques",
    "What Neural Networks Memorize Long Tail.pdf": "Memorization & Training Data Extraction",
    "Whos Harry Potter Approximate Unlearning LLMs.pdf": "Knowledge Editing & Localization",
    "Your AI, Not Your View The Bias of LLMs in Investment Analysis.pdf": "Financial NLP & Sentiment Analysis",
}


MANUAL_METADATA: dict[str, dict[str, str]] = {
    "A Test of Lookahead Bias in LLM Forecasts.pdf": {
        "title": "A Test of Lookahead Bias in LLM Forecasts",
        "authors": "Gao, Jiang & Yan",
        "year": "2026",
    },
    "All Leaks Count, Some Count More Interpretable Temporal.pdf": {
        "title": "All Leaks Count, Some Count More: Interpretable Temporal Contamination Detection in LLM Backtesting",
        "authors": "Zhang, Chen & Stadie",
        "year": "2026",
    },
    "AntiLeakBench Preventing Contamination.pdf": {
        "title": "AntiLeakBench: Preventing Data Contamination by Automatically Constructing Benchmarks with Updated Real-World Knowledge",
        "authors": "Wu et al.",
        "year": "2024",
    },
    "Assessing Look-Ahead Bias GPT Sentiment.pdf": {
        "title": "Assessing Look-Ahead Bias in Stock Return Predictions Generated by GPT Sentiment Analysis",
        "authors": "Glasserman & Lin",
        "year": "2024",
    },
    "BaseCal Unsupervised Confidence Calibration.pdf": {
        "title": "BaseCal: Unsupervised Confidence Calibration via Base Model Signals",
        "authors": "Tan et al.",
        "year": "2026",
    },
    "Causal View Entity Bias LLMs.pdf": {
        "title": "A Causal View of Entity Bias in (Large) Language Models",
        "authors": "Wang et al.",
        "year": "2023",
    },
    "CFinBench Chinese Financial Benchmark.pdf": {
        "title": "CFinBench: A Comprehensive Chinese Financial Benchmark for Large Language Models",
        "authors": "Nie et al.",
        "year": "2024",
    },
    "Chain-of-Note Enhancing RAG Robustness.pdf": {
        "title": "Chain-of-Note: Enhancing Robustness in Retrieval-Augmented Language Models",
        "authors": "Yu et al.",
        "year": "2024",
    },
    "Chain-of-Verification Reduces Hallucination.pdf": {
        "title": "Chain-of-Verification Reduces Hallucination in Large Language Models",
        "authors": "Dhuliawala et al.",
        "year": "2023",
    },
    "CHiLL Zero-Shot Feature Extraction Clinical.pdf": {
        "title": "CHiLL: Zero-Shot Feature Extraction with Large Language Models",
        "authors": "McInerney et al.",
        "year": "2022",
    },
    "Chronologically Consistent Large Language Models.pdf": {
        "title": "Chronologically Consistent Large Language Models",
        "authors": "He et al.",
        "year": "2025",
    },
    "Company-specific Biases Financial Sentiment LLMs.pdf": {
        "title": "Evaluating Company-Specific Biases in Financial Sentiment Analysis Using Large Language Models",
        "authors": "Nakagawa et al.",
        "year": "2024",
    },
    "Context-faithful Prompting for LLMs.pdf": {
        "title": "Context-Faithful Prompting for Large Language Models",
        "authors": "Zhou et al.",
        "year": "2023",
    },
    "Context-Faithfulness Memory Strength Evidence.pdf": {
        "title": "Investigating Context-Faithfulness in Large Language Models: The Roles of Memory Strength and Evidence Style",
        "authors": "Li et al.",
        "year": "2024",
    },
    "Counterfactual Memorization in Neural Language Models.pdf": {
        "title": "Counterfactual Memorization in Neural Language Models",
        "authors": "Zhang et al.",
        "year": "2021",
    },
    "Cutting Off Head Knowledge Conflicts.pdf": {
        "title": "Interpreting and Mitigating Knowledge Conflicts in Language Models",
        "authors": "Jin et al.",
        "year": "2024",
    },
    "Dated Data Tracing Knowledge Cutoffs.pdf": {
        "title": "Dated Data: Tracing Knowledge Cutoffs in Large Language Models",
        "authors": "Cheng et al.",
        "year": "2024",
    },
    "Dissecting Recall Factual Associations.pdf": {
        "title": "Dissecting Recall of Factual Associations in Auto-Regressive Language Models",
        "authors": "Geva et al.",
        "year": "2023",
    },
    "Does Localization Inform Editing.pdf": {
        "title": "Does Localization Inform Editing? Surprising Differences in Causality-Based Localization vs. Knowledge Editing in Language Models",
        "authors": "Hase et al.",
        "year": "2023",
    },
    "Entity Cells Language Models.pdf": {
        "title": "Entity Cells in Language Models",
        "authors": "Yona et al.",
        "year": "2026",
    },
    "Entity Identification Language Models.pdf": {
        "title": "Entity Identification in Language Models",
        "authors": "Sakata et al.",
        "year": "2025",
    },
    "Entity Knowledge Conflicts QA.pdf": {
        "title": "Entity-Based Knowledge Conflicts in Question Answering",
        "authors": "Longpre et al.",
        "year": "2021",
    },
    "Episodic Memories Benchmark LLMs.pdf": {
        "title": "Episodic Memories: Generation and Evaluation Benchmark for Large Language Models",
        "authors": "Huet et al.",
        "year": "2025",
    },
    "Extracting Training Data from LLMs 2020.pdf": {
        "title": "Extracting Training Data from Large Language Models",
        "authors": "Carlini et al.",
        "year": "2021",
    },
    "FFN Key-Value Memories Transformers.pdf": {
        "title": "Transformer Feed-Forward Layers Are Key-Value Memories",
        "authors": "Geva et al.",
        "year": "2021",
    },
    "FinGPT Dissemination-Aware Context-Enriched LLMs.pdf": {
        "title": "Explaining the Unexplained: Revealing Hidden Correlations for Better Interpretability",
        "authors": "Jiang et al.",
        "year": "Unknown",
    },
    "Knowledge Neurons Pretrained Transformers.pdf": {
        "title": "Knowledge Neurons in Pretrained Transformers",
        "authors": "Dai et al.",
        "year": "2022",
    },
    "Language Models Represent Space Time.pdf": {
        "title": "Language Models Represent Space and Time",
        "authors": "Gurnee & Tegmark",
        "year": "2024",
    },
    "Leakage Reproducibility Crisis ML Science.pdf": {
        "title": "Leakage and the Reproducibility Crisis in ML-Based Science",
        "authors": "Kapoor & Narayanan",
        "year": "2023",
    },
    "LLMFactor Extracting Profitable Factors.pdf": {
        "title": "LLMFactor: Extracting Profitable Factors through Prompts for Explainable Stock Movement Prediction",
        "authors": "Wang, Izumi & Sakaji",
        "year": "2024",
    },
    "Lopez-Lira ChatGPT Stock Returns.pdf": {
        "title": "Can ChatGPT Forecast Stock Price Movements? Return Predictability and Large Language Models",
        "authors": "Lopez-Lira & Tang",
        "year": "2024",
    },
    "Mechanistic Circuits Extractive QA.pdf": {
        "title": "Mechanistic Circuits for Extractive Question Answering",
        "authors": "Basu et al.",
        "year": "2025",
    },
    "MEMIT Mass-Editing Memory Transformer.pdf": {
        "title": "MEMIT: Mass-Editing Memory in a Transformer",
        "authors": "Meng et al.",
        "year": "2023",
    },
    "Memorization Problem LLMs Economic Forecasts.pdf": {
        "title": "The Memorization Problem in LLMs’ Economic Forecasts",
        "authors": "Lopez-Lira, Tang & Zhu",
        "year": "2025",
    },
    "Memory GAPS Tulving Test LLMs.pdf": {
        "title": "Memory GAPS: Would LLMs Pass the Tulving Test?",
        "authors": "Chauvet",
        "year": "2024",
    },
    "MiniCheck Efficient Fact-Checking Grounding.pdf": {
        "title": "MiniCheck: Efficient Fact-Checking of LLM Outputs on Grounding Documents",
        "authors": "Tang, Laban & Durrett",
        "year": "2024",
    },
    "MIRAGE Model Internals Answer Attribution.pdf": {
        "title": "MIRAGE: Model Internals for Answer Attribution",
        "authors": "Unknown",
        "year": "Unknown",
    },
    "MMLU-CF Contamination-free Benchmark.pdf": {
        "title": "MMLU-CF: A Contamination-Free Multi-Task Language Understanding Benchmark",
        "authors": "Fang et al.",
        "year": "2025",
    },
    "MQuAKE Knowledge Editing Multi-Hop.pdf": {
        "title": "MQuAKE: Assessing Knowledge Editing in Language Models via Multi-Hop Questions",
        "authors": "Zhong et al.",
        "year": "2023",
    },
    "Profit_Mirage_Revisiting_Information_Leakage_in_LL.pdf": {
        "title": "Profit Mirage: Revisiting Information Leakage in LLM-based Financial Agents",
        "authors": "Li et al.",
        "year": "2025",
    },
    "Proving Test Set Contamination Black Box.pdf": {
        "title": "Proving Test Set Contamination in Black-Box Language Models",
        "authors": "Oren et al.",
        "year": "2024",
    },
    "Quantifying Memorization Across Neural LMs.pdf": {
        "title": "Quantifying Memorization Across Neural Language Models",
        "authors": "Carlini et al.",
        "year": "2023",
    },
    "RE-IMAGINE Symbolic Benchmark Synthesis.pdf": {
        "title": "RE-IMAGINE: Symbolic Benchmark Synthesis for Reasoning",
        "authors": "Xu et al.",
        "year": "2025",
    },
    "Reasoning or Reciting Counterfactual Tasks.pdf": {
        "title": "Reasoning or Reciting? Exploring the Capabilities and Limitations of Language Models Through Counterfactual Tasks",
        "authors": "Wu et al.",
        "year": "2023",
    },
    "ReEval Hallucination Evaluation RAG.pdf": {
        "title": "ReEval: Hallucination Evaluation for Retrieval-Augmented Generation",
        "authors": "Yu et al.",
        "year": "2023",
    },
    "ROME Locating Editing Factual Associations GPT.pdf": {
        "title": "ROME: Locating and Editing Factual Associations in GPT",
        "authors": "Meng et al.",
        "year": "2022",
    },
    "Set the Clock Temporal Alignment LMs.pdf": {
        "title": "Set the Clock: Temporal Alignment of Pretrained Language Models",
        "authors": "Zhao et al.",
        "year": "2024",
    },
    "Stable Prediction Unknown Environments.pdf": {
        "title": "Stable Prediction Across Unknown Environments",
        "authors": "Unknown",
        "year": "Unknown",
    },
    "Task Contamination Not Few-Shot.pdf": {
        "title": "Task Contamination: Language Models May Not Be Few-Shot Anymore",
        "authors": "Li & Flanigan",
        "year": "2024",
    },
    "Taming Knowledge Conflicts LMs.pdf": {
        "title": "Taming Knowledge Conflicts in Language Models",
        "authors": "Li et al.",
        "year": "2025",
    },
    "Time Encoded in Weights Finetuned LMs.pdf": {
        "title": "Time Is Encoded in the Weights of Finetuned Language Models",
        "authors": "Nylund et al.",
        "year": "2024",
    },
    "Time Travel in LLMs Tracing Contamination.pdf": {
        "title": "Time Travel in LLMs: Tracing Contamination Through Language Reconstruction",
        "authors": "Golchin & Surdeanu",
        "year": "2024",
    },
    "Towards Objective Fine-tuning Calibration.pdf": {
        "title": "Towards Objective Fine-tuning: How LLMs’ Prior Knowledge Causes Potential Poor Calibration?",
        "authors": "Wang et al.",
        "year": "2025",
    },
    "TRAK Attributing Model Behavior at Scale.pdf": {
        "title": "TRAK: Attributing Model Behavior at Scale",
        "authors": "Park et al.",
        "year": "2023",
    },
    "Unfaithful Explanations in CoT.pdf": {
        "title": "Language Models Don’t Always Say What They Think: Unfaithful Explanations in Chain-of-Thought Prompting",
        "authors": "Turpin et al.",
        "year": "2023",
    },
    "What Neural Networks Memorize Long Tail.pdf": {
        "title": "What Neural Networks Memorize and Why: Discovering the Long Tail via Influence Estimation",
        "authors": "Feldman & Zhang",
        "year": "2020",
    },
    "Whos Harry Potter Approximate Unlearning LLMs.pdf": {
        "title": "Who’s Harry Potter? Approximate Unlearning in LLMs",
        "authors": "Eldan & Russinovich",
        "year": "2023",
    },
    "Your AI, Not Your View The Bias of LLMs in Investment Analysis.pdf": {
        "title": "Your AI, Not Your View: The Bias of LLMs in Investment Analysis",
        "authors": "Lee et al.",
        "year": "2025",
    },
}


def normalize_whitespace(text: str) -> str:
    text = text.replace("\r", "\n").replace("\u00a0", " ").replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_text_block(text: str) -> str:
    text = normalize_whitespace(text)
    text = re.sub(r"\b\d+\s+INTRODUCTION\b.*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\bI\s+NTRODUCTION\b.*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\bKEYWORDS\b.*", "", text, flags=re.IGNORECASE)
    return text.strip()


def split_sentences(text: str) -> list[str]:
    text = clean_text_block(text)
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9“\"'(\[])", text)
    sentences = []
    for part in parts:
        sentence = normalize_whitespace(part)
        if any(sentence.startswith(prefix) for prefix in ("CCS Concepts", "JEL Classification", "Keywords", "Index Terms")):
            continue
        if len(sentence) >= 35:
            sentences.append(sentence)
    return sentences


def pretty_stem(filename: str) -> str:
    return Path(filename).stem.replace("_", " ").strip()


def clean_authors(authors: str) -> str:
    authors = normalize_whitespace(authors)
    if not authors or authors.lower() == "unknown":
        return "Unknown"
    if "et al." in authors:
        return authors
    if authors.count(",") <= 3 and len(authors) <= 50 and not re.search(r"\d", authors):
        return authors

    stripped = re.sub(r"[\d*†‡♠♣~]", " ", authors)
    stripped = re.sub(r"[^\w&,\-'. ]+", " ", stripped)
    stripped = normalize_whitespace(stripped)
    if not stripped:
        return "Unknown"
    words = stripped.split()
    if len(words) >= 2:
        return f"{words[0]} {words[1]} et al."
    return stripped


def clean_title(filename: str, raw_title: str) -> str:
    override = MANUAL_METADATA.get(filename, {})
    if override.get("title"):
        return override["title"]

    title = normalize_whitespace(raw_title)
    if not title:
        return pretty_stem(filename)

    title = re.sub(r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b.*", "", title)
    if len(title) > 160:
        return pretty_stem(filename)
    return title or pretty_stem(filename)


def clean_year(filename: str, raw_year: str) -> str:
    override = MANUAL_METADATA.get(filename, {})
    if override.get("year"):
        return override["year"]
    raw_year = normalize_whitespace(raw_year)
    return raw_year if re.fullmatch(r"\d{4}", raw_year) else "Unknown"


def short_title(title: str) -> str:
    if ":" in title:
        return title.split(":", 1)[0].strip()
    if "?" in title and len(title) > 75:
        return title.split("?", 1)[0].strip() + "?"
    words = title.split()
    if len(words) > 10:
        return " ".join(words[:10]).strip()
    return title


def build_summary(abstract: str, intro: str) -> str:
    sentences = split_sentences(abstract)
    if len(sentences) < 2:
        sentences.extend(split_sentences(intro))

    deduped: list[str] = []
    for sentence in sentences:
        if sentence not in deduped:
            deduped.append(sentence)
    chosen = deduped[:3]
    if not chosen:
        fallback = clean_text_block(abstract or intro)
        return fallback[:500].strip()
    return " ".join(chosen)


def build_key_points(abstract: str, intro: str) -> list[str]:
    sentences = split_sentences(abstract)
    if len(sentences) < 3:
        sentences.extend(split_sentences(intro))

    scored: list[tuple[int, str]] = []
    for sentence in sentences:
        lower = sentence.lower()
        if any(token in lower for token in ("ccs concepts", "jel classification", "keywords", "index terms")):
            continue
        score = 0
        if any(token in lower for token in ("we propose", "we introduce", "we develop", "we present", "we study", "we formulate")):
            score += 3
        if any(token in lower for token in ("benchmark", "dataset", "metric", "framework", "method", "attack", "editing", "prompting", "calibration")):
            score += 2
        if any(token in lower for token in ("show", "find", "demonstrate", "reveal", "improve", "reduce", "outperform", "supports")):
            score += 2
        scored.append((score, sentence))

    scored.sort(key=lambda item: (-item[0], len(item[1])))
    bullets: list[str] = []
    for _, sentence in scored:
        if sentence not in bullets:
            bullets.append(sentence)
        if len(bullets) == 3:
            break

    if not bullets:
        bullets = split_sentences(abstract or intro)[:2]
    return bullets[:3]


def build_project_insight(category: str, title: str, abstract: str) -> str:
    text = f"{title} {abstract}".lower()
    base = {
        "Memorization & Training Data Extraction": "This paper motivates CFLS as a leakage-sensitive score because memorized traces can surface even without explicit retrieval. It supports counterfactual testing that perturbs dates, entities, and narrative details to check whether DeepSeek-chat is reciting stored Chinese financial news patterns rather than reasoning from evidence.",
        "Benchmark Contamination & Leakage Detection": "This paper informs our contamination protocol and benchmark design. Its methods translate into CFLS-adjacent checks using temporally fresh Chinese news, counterfactual variants, and evidence-intrusion probes that separate leakage from genuine inference.",
        "Temporal Knowledge & Look-Ahead Bias": "This paper is directly aligned with our setting because Chinese financial news is time sensitive. It supports CFLS scoring against publication dates, fake-date counterfactuals, and tests for evidence intrusion where DeepSeek-chat answers with post-cutoff knowledge not licensed by the supplied article.",
        "Knowledge Editing & Localization": "Although this paper studies editing rather than detection, it identifies where factual associations reside and how they propagate. That is useful for interpreting entity-cue dependence and for designing counterfactual edits or ablations that test whether DeepSeek-chat relies on stored entity priors instead of article evidence.",
        "Factual Grounding & Knowledge Conflicts": "This paper is important for our evidence-intrusion analysis because it operationalizes whether answers stay within the supplied evidence. It can inform CFLS components that penalize unsupported post-article facts and compare original versus counterfactual context windows.",
        "Mechanistic Interpretability & Internal Representations": "This paper helps us reason about the internal route from entity cue to answer token. It is useful for framing entity-cue dependence, for interpreting counterfactual sensitivity, and for connecting CFLS failures to specific retrieval-like or association-like mechanisms.",
        "Financial NLP & Sentiment Analysis": "This paper anchors our domain setup in finance and shows how market-facing prompts can be sensitive to latent priors, entity cues, or temporal leakage. It helps calibrate CFLS on Chinese financial news and motivates counterfactual article rewrites that separate evidence from memorized market outcomes.",
        "Prompting & Reasoning Techniques": "This paper helps us separate reasoning behavior from recitation behavior at the prompt level. That is useful when building CFLS evaluation prompts, counterfactual testing scripts, and evidence-intrusion probes that minimize leakage introduced by the prompting format itself.",
        "Calibration, Uncertainty & Robustness": "This paper suggests auxiliary signals beyond accuracy, especially confidence, entropy, and invariance across environments. Those ideas can complement CFLS by flagging cases where DeepSeek-chat sounds certain even when the evidence is weak or counterfactual variants should reverse the answer.",
        "Memory Systems & Cognitive Framing": "This paper provides a conceptual vocabulary for distinguishing episodic-like recall, semantic priors, and confabulation. That framing is useful when interpreting CFLS errors, evidence intrusion, and entity-cue dependence in DeepSeek-chat on Chinese financial news.",
    }[category]

    addendum = ""
    if "entity" in text or "company" in text:
        addendum = " It is especially useful for entity-swap tests that measure entity-cue dependence."
    elif "counterfactual" in text or "fake-date" in text or "lookahead" in text or "look-ahead" in text:
        addendum = " It especially supports our counterfactual testing design."
    elif any(token in text for token in ("ground", "faithful", "hallucination", "context", "retrieval")):
        addendum = " It also maps directly to evidence-intrusion scoring."
    elif any(token in text for token in ("calibration", "confidence", "entropy", "uncertainty")):
        addendum = " It is a good candidate for an auxiliary signal alongside CFLS."
    return base + addendum


def load_catalog() -> list[dict[str, str]]:
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    return data["papers"]


def ensure_complete_mapping(records: list[dict[str, str]]) -> None:
    filenames = {record["filename"] for record in records}
    mapped = set(CATEGORY_MAP)
    missing = sorted(filenames - mapped)
    extra = sorted(mapped - filenames)
    if missing or extra:
        message = []
        if missing:
            message.append(f"Missing category mapping for: {missing}")
        if extra:
            message.append(f"Category mapping contains non-existent files: {extra}")
        raise ValueError(" | ".join(message))


def enrich_record(record: dict[str, str]) -> dict[str, str]:
    filename = record["filename"]
    override = MANUAL_METADATA.get(filename, {})
    title = clean_title(filename, record.get("title_guess", ""))
    authors = clean_authors(override.get("authors") or record.get("authors_guess", "Unknown"))
    year = clean_year(filename, override.get("year") or record.get("year_guess", "Unknown"))
    abstract = record.get("abstract", "")
    intro = record.get("introduction_excerpt", "")
    summary = build_summary(abstract, intro)
    key_points = build_key_points(abstract, intro)
    category = CATEGORY_MAP[filename]
    insight = build_project_insight(category, title, abstract or intro)

    return {
        "filename": filename,
        "title": title,
        "short_title": short_title(title),
        "authors": authors,
        "year": year,
        "summary": summary,
        "key_points": key_points,
        "insight": insight,
        "category": category,
    }


def render_index(records: list[dict[str, str]]) -> str:
    lines = ["# Paper Index", ""]
    for category, note_filename in CATEGORY_FILES:
        lines.append(f"## {category}")
        lines.append("")
        category_records = [record for record in records if record["category"] == category]
        category_records.sort(key=lambda item: item["title"].lower())
        for record in category_records:
            lines.append(f"- [{record['short_title']}]({record['filename']})")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_category_doc(category: str, records: list[dict[str, str]]) -> str:
    lines = [f"# {category}", ""]
    category_records = [record for record in records if record["category"] == category]
    category_records.sort(key=lambda item: item["title"].lower())
    for index, record in enumerate(category_records):
        if index:
            lines.append("---")
            lines.append("")
        lines.append(f"## {record['title']}")
        lines.append(f"**Authors & Year:** {record['authors']} ({record['year']})")
        lines.append("")
        lines.append(f"**Summary:** {record['summary']}")
        lines.append("")
        lines.append("**Key methods/findings**")
        for bullet in record["key_points"]:
            lines.append(f"- {bullet}")
        lines.append("")
        lines.append(f"**Insight for our project:** {record['insight']}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def main() -> None:
    NOTES_DIR.mkdir(exist_ok=True)
    raw_records = load_catalog()
    ensure_complete_mapping(raw_records)
    records = [enrich_record(record) for record in raw_records]

    index_text = render_index(records)
    (RELATED_DIR / "INDEX.md").write_text(index_text, encoding="utf-8")

    for category, filename in CATEGORY_FILES:
        doc_text = render_category_doc(category, records)
        (NOTES_DIR / filename).write_text(doc_text, encoding="utf-8")

    print(f"Wrote {RELATED_DIR / 'INDEX.md'}")
    for _, filename in CATEGORY_FILES:
        print(f"Wrote {NOTES_DIR / filename}")


if __name__ == "__main__":
    main()
