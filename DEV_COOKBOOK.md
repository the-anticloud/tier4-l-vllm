# Dev Cookbook — L_VLLM (Anticloud Integration)
**Component:** L_VLLM | **Tier:** T4 Inference Agents  
**Anticloud Layer:** AIOSS Ledger + vLLM + PagedAttention  
**Date:** 2026-09-30

---

## Prerequisites

```bash
# Python 3.10+, CUDA 12.1+, 16GB+ VRAM (T4 minimum, A100 recommended)
pip install vllm>=0.4.0 anticloud-aioss>=1.0.0
# Verify AIOSS binary
aioss --version  # should print: aioss 1.x.x (sha3-256)
```

---

## 1. Quickstart — Sovereign Inference in 5 Minutes

```python
from l_vllm_anticloud import AIossVLLMWrapper

# Initialize with AIOSS ledger
wrapper = AIossVLLMWrapper(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    ledger_path="./inference.aioss",
    device="cuda",
)

# Generate — every call is automatically logged to the ledger
result = wrapper.generate("Explain sovereign AI in one paragraph.")
print(result.text)
print(f"Chain hash: {result.chain_hash}")   # SHA3-256, tamper-evident
print(f"Tok/s: {result.tokens_per_second}")
```

After this, `inference.aioss` contains a cryptographic audit trail.

---

## 2. Verifying the Ledger

```bash
# CLI verification (auditors can run this independently)
aioss verify ./inference.aioss

# Expected output:
# ✓ Chain integrity verified: 1 entries
# ✓ Algorithm: sha3-256
# ✓ Final hash: a3f9...
# ✓ AUDIT CLEAN
```

```python
# Programmatic verification
is_valid = wrapper.verify()
assert is_valid, "Ledger tampered!"
```

---

## 3. High-Throughput Server (OpenAI-Compatible API)

```python
# server.py
from vllm import AsyncLLMEngine, AsyncEngineArgs
from vllm.entrypoints.openai import api_server
from aioss_integration import AIossVLLMWrapper

engine_args = AsyncEngineArgs(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    tensor_parallel_size=1,       # increase for multi-GPU
    gpu_memory_utilization=0.90,  # leave 10% for OS
    max_num_batched_tokens=8192,
    enable_prefix_caching=True,   # reduces KV cache recomputation
    kv_cache_dtype="auto",
)

# Wrap with AIOSS ledger before serving
wrapper = AIossVLLMWrapper.from_engine_args(
    engine_args, ledger_path="/data/production.aioss"
)
wrapper.serve(host="0.0.0.0", port=8000)
```

```bash
# Test with curl (OpenAI-compatible)
curl http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "mistral-7b", "prompt": "Hello, sovereign AI", "max_tokens": 50}'
```

---

## 4. Batch Inference with Cost Tracking

```python
prompts = [
    "Summarize GDPR Article 17 in one sentence.",
    "Explain PagedAttention in plain English.",
    "What is SHA3-256 used for in audit logs?",
]

results = wrapper.generate_batch(prompts, max_tokens=200)

# Cost savings vs. GPT-4 API (rough estimate)
savings = wrapper.cost_savings()
print(f"Equivalent cloud cost avoided: ${savings['usd_saved']:.2f}")
# e.g., "Equivalent cloud cost avoided: $12.40" for 50K tokens
```

---

## 5. KV Cache Tuning

PagedAttention manages KV cache like virtual memory. Key knobs:

```python
# Maximize throughput on T4 (16GB VRAM)
engine_args = AsyncEngineArgs(
    model="...",
    gpu_memory_utilization=0.92,   # safe max on T4
    max_num_seqs=64,               # concurrent requests
    max_model_len=4096,            # reduce if OOM
    block_size=16,                 # KV cache block size (tokens)
    swap_space=4,                  # GB CPU swap for overflow
)
```

Monitor KV cache:
```python
stats = wrapper.engine.get_cache_block_table_state()
print(f"Free blocks: {stats['num_free_gpu_blocks']}")
print(f"Cache hit rate: {stats['prefix_cache_hit_rate']:.1%}")
```

---

## 6. Multi-GPU Tensor Parallelism

```python
# 2× A100 80GB
engine_args = AsyncEngineArgs(
    model="meta-llama/Llama-3-70b-instruct",
    tensor_parallel_size=2,        # split model across 2 GPUs
    pipeline_parallel_size=1,
    gpu_memory_utilization=0.95,
)
```

Performance reference (from NAV2 2023 paper benchmarks):
- 7B on T4: ~47 tok/s
- 7B on A100: ~180 tok/s
- 70B on 4×A100: ~85 tok/s

---

## 7. AIOSS Ledger Export for Audit

```bash
# Export to human-readable JSON
aioss export ./production.aioss --format json --output audit_report.json

# Export to CSV for SIEM ingestion
aioss export ./production.aioss --format csv --output siem_feed.csv

# Verify specific entry by index
aioss verify ./production.aioss --entry 42
```

JSON export structure:
```json
{
  "entries": [
    {
      "index": 0,
      "timestamp": "2026-09-30T14:23:01Z",
      "prompt_hash": "sha3-256:a1b2...",
      "output_hash": "sha3-256:c3d4...",
      "model_fingerprint": "mistral-7b-instruct-v0.2",
      "latency_ms": 312,
      "tokens_generated": 47,
      "chain_hash": "sha3-256:e5f6..."
    }
  ],
  "final_chain_hash": "sha3-256:...",
  "algorithm": "sha3-256",
  "total_entries": 1000
}
```

---

## 8. Docker Deployment

```dockerfile
FROM nvcr.io/nvidia/pytorch:24.01-py3
RUN pip install vllm anticloud-aioss
COPY . /app
WORKDIR /app
ENTRYPOINT ["python", "-m", "l_vllm_anticloud.server"]
```

```bash
docker run --gpus all -p 8000:8000 \
  -v /data/ledger:/ledger \
  -e AIOSS_LEDGER_PATH=/ledger/prod.aioss \
  anticloud/l-vllm:latest
```

---

## 9. Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `CUDA out of memory` | KV cache too large | Lower `gpu_memory_utilization` to 0.85 |
| `aioss: command not found` | Binary not on PATH | `export PATH=$PATH:~/.local/bin/aioss` |
| `Chain hash mismatch` | Ledger corrupted | Restore from backup; `aioss repair` |
| `Throughput < 20 tok/s` | Wrong dtype | Add `--dtype float16` to engine args |
| `P99 latency > 2s` | Batch too large | Reduce `max_num_seqs` to 16 |

---

## 10. References

1. Kwon, W., et al. (2023). Efficient memory management for large language model serving with PagedAttention. *SOSP 2023.*
2. vLLM documentation. https://docs.vllm.ai/
3. AIOSS Ledger specification. `TIER_1_ANTICLOUD_CORE/AIOSS_FORMAT/`
4. Lois-Kleinner Alpasan. AIOSS Architecture. USPTO pending, 2026.
