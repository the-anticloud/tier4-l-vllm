# HF_Leaderboard_Lab_Results

**Project:** `L_VLLM`  
**Tier:** `TIER_4_INFERENCE_AGENTS`  
**Slug:** `vllm-project/vllm`  
**Commit:** `1117140edbaf`  
**Run:** `2026-09-30T15:07:07.146295+00:00`  

## Isolation Environment

| Field | Value |
| ----- | ----- |
| Platform | `win32` |
| Python | `3.12.10` |
| HF model | `distilbert-base-uncased` |
| HF load time | `4.42s` |
| Inference device | `cpu` |

## Results

**Framework:** [HuggingFace Open LLM Leaderboard (proxy via distilbert-base-uncased)](https://huggingface.co/docs/leaderboards/en/open_llm_leaderboard/archive)

**Model used:** `distilbert-base-uncased`

### Inference Latency (Classification)

| Metric | Value |
| ------ | ----- |
| Avg latency | **56.84 ms** |
| Min latency | 48.53 ms |
| Max latency | 67.51 ms |
| Samples | 5 |

### Real Tokenization Results

| Field | Value |
| ----- | ----- |
| Token count | **43** |
| Tokenization latency | 2.92 ms |
| Classification label | `LABEL_0` |
| Classification score | 0.591 |
| Classification latency | 174.88 ms |
| Status | **PASS** |

**Input text tokenized:**
```
L_VLLM (vllm-project/vllm) — 7477 files, 1322747 source lines, licence Apache-2.0, primary language ['Python']
```

**First 20 tokens:**
```
['[CLS]', 'l', '_', 'v', '##ll', '##m', '(', 'v', '##ll', '##m', '-', 'project', '/', 'v', '##ll', '##m', ')', '—', '747', '##7']
```

> Full MMLU/HellaSwag/TruthfulQA/ARC/Winogrande/GSM8K require dedicated GPU.
> These results are CPU inference proxy metrics using distilbert-base-uncased.

---
_Anticloud Benchmark Suite — isolation log — 2026-09-30T15:07:07.146295+00:00_