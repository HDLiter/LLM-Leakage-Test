# Calibration, Uncertainty & Robustness

## Anchor Regression Heterogeneous Causality
**Authors & Year:** Rothenhausler et al. (2021)

**Summary:** We consider the problem of predicting a response variable from a set of covariates on a data set that di ers in distribution from the training data. Causal parameters are optimal in terms of predictive accuracy if in the new distribution either many variables are a ected by interventions or only some variables are a ected, but the perturbations are strong. If the training and test distributions di er by a shift, causal parameters might be too conservative to perform well on the above task.

**Key methods/findings**
- Anchor regression is shown empirically to improve replicability and protect against distributional shifts.
- This motivates anchor regression, a method that makes use of exogeneous variables to solve a relaxation of the causal minimax problem by considering a modi cation of the least-squares loss.
- The procedure naturally provides an interpolation between the solutions of ordinary least squares and two-stage least squares.

**Insight for our project:** This paper suggests auxiliary signals beyond accuracy, especially confidence, entropy, and invariance across environments. Those ideas can complement CFLS by flagging cases where DeepSeek-chat sounds certain even when the evidence is weak or counterfactual variants should reverse the answer.

---

## BaseCal: Unsupervised Confidence Calibration via Base Model Signals
**Authors & Year:** Tan et al. (2026)

**Summary:** Reliable confidence is essential for trusting the outputs of LLMs, yet widely deployed posttrained LLMs (PoLLMs) typically compromise this trust with severe overconfidence. In contrast, we observe that their corresponding base LLMs often remain well-calibrated. This naturally motivates us to calibrate PoLLM confidence using the base LLM as a reference.

**Key methods/findings**
- Experiments across five datasets and three LLM families demonstrate the effectiveness of BaseCal, reducing Expected Calibration Error (ECE) by an average of 42.90% compared to the best unsupervised baselines.
- To address this, we proposeBaseCal-Proj, which trains a lightweight projection to map the finallayer hidden states of PoLLMs back to those of their base LLMs.
- This work proposes two ways to achieve this.

**Insight for our project:** This paper suggests auxiliary signals beyond accuracy, especially confidence, entropy, and invariance across environments. Those ideas can complement CFLS by flagging cases where DeepSeek-chat sounds certain even when the evidence is weak or counterfactual variants should reverse the answer. It is a good candidate for an auxiliary signal alongside CFLS.

---

## Interpretable Probability Estimation via Shapley Reconstruction
**Authors & Year:** Nan et al. (2026)

**Summary:** Large Language Models (LLMs) demonstrate potential to estimate the probability of uncertain events, by leveraging their extensive knowledge and reasoning capabilities. This ability can be applied to support intelligent decision-making across diverse fields, such as financial forecasting and preventive healthcare. However, directly prompting LLMs for probability estimation faces significant challenges: their outputs are often noisy, and the underlying predicting process is opaque.

**Key methods/findings**
- In this paper, we proposePRISM: Probability Reconstruction via Shapley Measures, a framework that brings transparency and precision to LLM-based probability estimation.
- In our experiments, we demonstrate PRISM improves predictive accuracy over direct prompting and other baselines, across multiple domains including finance, healthcare, and agriculture.
- Large Language Models (LLMs) demonstrate potential to estimate the probability of uncertain events, by leveraging their extensive knowledge and reasoning capabilities.

**Insight for our project:** This paper suggests auxiliary signals beyond accuracy, especially confidence, entropy, and invariance across environments. Those ideas can complement CFLS by flagging cases where DeepSeek-chat sounds certain even when the evidence is weak or counterfactual variants should reverse the answer.

---

## Invariant Risk Minimization
**Authors & Year:** Arjovsky et al. (2019)

**Summary:** Machine learning su ers from a fundamental problem. While machines are able to learn complex prediction rules by minimizing their training error, data are often marred by selection biases, confounding factors, and other peculiarities [ 49,48,23]. As such, machines justi ably inherit these data biases.

**Key methods/findings**
- After training a convolutional neural network on this dataset, we observe that the model fails to classify easy examples of images of cows when they are taken on sandy beaches.
- Machine learning su ers from a fundamental problem.
- As such, machines justi ably inherit these data biases.

**Insight for our project:** This paper suggests auxiliary signals beyond accuracy, especially confidence, entropy, and invariance across environments. Those ideas can complement CFLS by flagging cases where DeepSeek-chat sounds certain even when the evidence is weak or counterfactual variants should reverse the answer.

---

## Kernel Language Entropy
**Authors & Year:** Nikitin et al. (2024)

**Summary:** Uncertainty quantification in Large Language Models (LLMs) is crucial for applications where safety and reliability are important. In particular, uncertainty can be used to improve the trustworthiness of LLMs by detecting factually incorrect model responses, commonly called hallucinations. Critically, one should seek to capture the model’s semantic uncertainty , i.e., the uncertainty over the meanings of LLM outputs, rather than uncertainty over lexical or syntactic variations that do not affect answer correctness.

**Key methods/findings**
- To address this problem, we propose Kernel Language Entropy (KLE), a novel method for uncertainty estimation in white- and black-box LLMs.
- We theoretically prove that KLE generalizes the previous state-of-the-art method called semantic entropy and empirically demonstrate that it improves uncertainty quantification performance across multiple natural language generation datasets and LLM architectures.
- In particular, uncertainty can be used to improve the trustworthiness of LLMs by detecting factually incorrect model responses, commonly called hallucinations.

**Insight for our project:** This paper suggests auxiliary signals beyond accuracy, especially confidence, entropy, and invariance across environments. Those ideas can complement CFLS by flagging cases where DeepSeek-chat sounds certain even when the evidence is weak or counterfactual variants should reverse the answer. It also maps directly to evidence-intrusion scoring.

---

## Stable Prediction Across Unknown Environments
**Authors & Year:** Unknown (Unknown)

**Summary:** In many machine learning applications, the training distribution used to learn a probabilistic classi er di ers from the testing distribution on which the classi er will be used to make predictions. Traditional methods correct the distribution shift by reweighting the training data with the ratio of the density between test and training data. But in many applications training takes place without prior knowledge of the testing.

**Key methods/findings**
- In this paper, we propose a novel Deep Global Balancing Regression algorithm to jointly optimize a deep auto-encoder model and a global balancing model for stable prediction across unknown environments.
- The deep auto-encoder model is designed to reduce the dimensionality of the feature space, thus making global balancing easier.
- We show, both theoretically and with empirical experiments, that our algorithm can make stable predictions across unknown environments.

**Insight for our project:** This paper suggests auxiliary signals beyond accuracy, especially confidence, entropy, and invariance across environments. Those ideas can complement CFLS by flagging cases where DeepSeek-chat sounds certain even when the evidence is weak or counterfactual variants should reverse the answer.

---

## Towards Objective Fine-tuning: How LLMs’ Prior Knowledge Causes Potential Poor Calibration?
**Authors & Year:** Wang et al. (2025)

**Summary:** Fine-tuned Large Language Models (LLMs) often demonstrate poor calibration, with their confidence scores misaligned with actual performance. While calibration has been extensively studied in models trained from scratch, the impact of LLMs’ prior knowledge on calibration during fine-tuning remains understudied. Our research reveals that LLMs’ prior knowledge causes potential poor calibration due to the ubiquitous presence of known data in real-world fine-tuning, which appears harmful for calibration.

**Key methods/findings**
- To address this, we propose CogCalib, a cognition-aware framework that applies targeted learning strategies according to the model’s prior knowledge.
- Specifically, data aligned with LLMs’ prior knowledge would induce overconfidence, while new knowledge improves calibration.
- Fine-tuned Large Language Models (LLMs) often demonstrate poor calibration, with their confidence scores misaligned with actual performance.

**Insight for our project:** This paper suggests auxiliary signals beyond accuracy, especially confidence, entropy, and invariance across environments. Those ideas can complement CFLS by flagging cases where DeepSeek-chat sounds certain even when the evidence is weak or counterfactual variants should reverse the answer. It is a good candidate for an auxiliary signal alongside CFLS.
