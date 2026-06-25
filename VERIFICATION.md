# ISC-Bench Verification Rules

This document explains how ISC-Bench decides whether a model has been **triggered**, how we treat different harm categories, and why we use different verification procedures for general versus specialist-domain cases.

## Why we say "Triggered"

Earlier versions of ISC-Bench used the word `jailbroken`. We now prefer **triggered**.

`Jailbroken` usually implies that a user directly attacked the model with an adversarial harmful query. ISC-Bench studies a different phenomenon: the model produces harmful or policy-relevant content as a side effect of completing a legitimate-looking task. In other words, the harmful behavior is **triggered by the workflow**, not necessarily by a direct malicious request.

That is the reason the leaderboard now uses **Triggered** rather than **Jailbroken**.

## Verification Principles

We use the following principles throughout the benchmark:

1. **Primary goal**
   Determine whether the model produces clearly policy-relevant harmful output under the released ISC/TVD workflow.

2. **Different domains require different standards**
   Some outputs are easy to judge directly. Others require domain expertise, model cross-checking, or manual review.

3. **Public release is conservative**
   We do not always publish every raw output or strongest variant. Public evidence is curated to support the claim while reducing unnecessary misuse risk.

4. **Verification is layered**
   ISC-Bench does not rely on a single judge model or a single heuristic across every domain.

## Category 1: General Harmful Content

This includes categories where the harmfulness or policy relevance is usually apparent to trained maintainers without specialized scientific review, for example:

- toxicity and abuse
- harassment
- misinformation-style outputs
- scam or fraud-style outputs
- policy-sensitive moderation failures

For these categories, our **primary evaluation** is direct human judgment by the benchmark maintainers. This is usually sufficient because the target behavior is already well understood in the current safety-benchmark ecosystem.

Where helpful, we also refer to established public benchmarks and prompt taxonomies, including widely used AI-safety evaluation resources.

## Category 2: Specialist or Closed-Domain Content

This includes domains where the output may be safety-relevant, but correct interpretation requires more technical knowledge. Examples include:

- computational chemistry
- biology and genomics
- pharmacology and toxicology
- epidemiology
- specialist cyber or engineering workflows

These cases are harder to judge fairly. For that reason, we use a more careful verification procedure.

### Layer 1: Model Cross-Checking

We often test the same content across multiple models with different alignment profiles. The purpose is not to treat one model as an oracle, but to see whether the content is consistently handled as sensitive, refused under direct questioning, or recognized as high-risk across systems.

In practice, this often involves:

- directly asking about the content in a more explicit form
- following up over multiple turns
- comparing responses from models with weaker versus stronger alignment

If strongly aligned models still refuse or treat the content as sensitive when asked more directly, that is evidence that the material is genuinely safety-relevant.

### Layer 2: Structured Judge Prompts

For some specialist cases, we use a custom judge prompt to evaluate whether the generated content is actually completing a harmful or policy-relevant task, rather than merely producing technical vocabulary.

This is a supporting signal, not the only signal.

### Layer 3: Human Review

We also perform manual review, including external fact-checking or literature checks when needed. This step is slower, but it is important for domains where superficial inspection is not enough.

## What We Do Not Claim

ISC-Bench does **not** claim that every template:

- works equally well on every model
- has identical severity across domains
- should be judged using one universal rule

Our claim is narrower and more structural:

- ISC/TVD can trigger policy-relevant harmful behavior in ordinary task-completion settings
- this pattern generalizes across multiple strong models
- verification should be matched to the domain, rather than reduced to a single judge score

## If You Disagree With a Verification Decision

That feedback is useful. If you think a case has been misclassified, please be specific:

- identify the exact template or issue
- explain what failed to reproduce
- explain why the output should not count as triggered
- suggest a better verification procedure for that domain

We are open to improving the benchmark, especially for specialist-domain verification where reasonable people may disagree about evidentiary standards.

## Summary

ISC-Bench uses a simple rule:

- **general harmful content** is primarily judged by informed human review
- **specialist-domain content** is judged with layered verification: model cross-checking, structured judge prompts, and human review

This is not perfect, but it is more faithful to the benchmark than treating every case as if it were a standard single-turn jailbreak prompt.
