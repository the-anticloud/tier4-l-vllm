# Developer Cookbook — L_VLLM

> Anticloud sovereign integration guide. All commands run offline.
> Author: Lois-Kleinner Alpasan / Anticloud FZ LLE
> USPTO pending 2026.

---

## Prerequisites

```bash
# Python 3.11+
python --version

# AIOSS ledger CLI (build from source)
cd TIER_1_ANTICLOUD_CORE/AIOSS_FORMAT/src && cargo build --release
export PATH="$PATH:$(pwd)/target/release"
aioss --version

# Initialize your ledger
aioss init --ledger ./ledger/main.aioss
```

---

## Installation

```bash
pip install vllm aioss-python
```

Verify:
```bash
python -c "import importlib; m = importlib.import_module('lvllm'); print('OK:', m)"
```

---

## Quickstart

```bash
python -m vllm.entrypoints.openai.api_server --model Qwen/Qwen2.5-1.5B-Instruct --port 8000
```

---

## Configuration

```yaml
# vllm_config.yaml
model: Qwen/Qwen2.5-1.5B-Instruct
max_model_len: 4096
gpu_memory_utilization: 0.85
tensor_parallel_size: 1
enable_prefix_caching: true
disable_log_requests: false
```

---

## Anticloud Integration Pattern

```python
from aioss_integration import AIossVLLMWrapper
from vllm import LLM, SamplingParams

llm = LLM(model="Qwen/Qwen2.5-1.5B-Instruct")
wrapper = AIossVLLMWrapper(llm, ledger_path="./ledger/main.aioss")

outputs = wrapper.generate(
    prompts=["Explain PagedAttention in one sentence."],
    sampling_params=SamplingParams(temperature=0.7, max_tokens=200)
)
print(outputs[0])
print("Cost savings:", wrapper.cost_savings())
```

---

## AIOSS Ledger Integration

Every significant L_VLLM operation should emit a ledger entry:

```python
import subprocess, json, hashlib

def aioss_append(ledger_path: str, event: dict):
    content = json.dumps(event, sort_keys=True)
    r = subprocess.run(
        ["aioss", "append", "--ledger", ledger_path, content],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        print("[AIOSS] Warning:", r.stderr)
    return r.returncode == 0

# Usage
aioss_append("./ledger/main.aioss", {
    "project": "L_VLLM",
    "event": "run",
    "input_hash": hashlib.sha3_256(b"your_input").hexdigest(),
})
```

Verify the chain at any time:
```bash
aioss verify --ledger ./ledger/main.aioss
```

---

## Benchmarking

Run the Anticloud 3-seed benchmark:
```bash
python BENCHMARKS/ENVIRONMENT_LAB_RESULTS_TEMPLATE.py
# Results at: OFFICIAL_BENCHMARKS/Environment_Lab_Results/results.json
```

For GPU benchmarks (T4):
```
https://www.kaggle.com/code/loiskleinner/anticloud-real-benchmarks
```

---

## Docker

```bash
# Full stack
docker compose up anticloud-ledger anticloud-inference

# Benchmark runner
docker compose run anticloud-bench

# Check health
curl http://localhost:8080/health  # AIOSS ledger
curl http://localhost:8000/health  # vLLM inference
```

---

## Common Issues

**CUDA OOM:** Reduce `gpu_memory_utilization` to 0.7 or lower `max_model_len` to 2048
**aioss CLI not found:** Build from source: `cd AIOSS_FORMAT/src && cargo build --release`
**Slow first request:** Expected — KV cache pages are allocated on first inference. Subsequent requests are faster.

---

## Further Reading

- [RESEARCH_PAPERS/anticloud_l_vllm_paper.md](../RESEARCH_PAPERS/anticloud_l_vllm_paper.md) — technical paper with citations
- [OFFICIAL_BENCHMARKS/](../OFFICIAL_BENCHMARKS/) — benchmark results
- [ENTERPRISE_LICENSING/PRICING.md](../ENTERPRISE_LICENSING/PRICING.md) — commercial licensing
- [CONTRACTS/MSA/MASTER_SERVICE_AGREEMENT.md](../CONTRACTS/MSA/MASTER_SERVICE_AGREEMENT.md) — MSA template
