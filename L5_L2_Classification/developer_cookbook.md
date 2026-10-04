# Developer Cookbook — L_VLLM
**Stack:** Python 3.11, vllm 0.4+, PyTorch 2.10+, CUDA 12.x, PAX 27B, AIOSS_FORMAT
**Domain:** vLLM: production inference server with PagedAttention for PAX 27B high-throughput deployment

## Start vLLM server with PAX 27B
```bash
python -m vllm.entrypoints.openai.api_server \
  --model ./pax-27b-q4.gguf \
  --port 8000 \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.90
```

## Python client
```python
from l_vllm import VLLMAnticloudClient

client = VLLMAnticloudClient(
    base_url="http://localhost:8000",
    aioss_chain="./vllm.aioss"
)

result = client.generate(
    prompt="Analyze this biosignal data for the TIER_7 pipeline:",
    max_tokens=256, temperature=0.1
)
print(result.text, f"({result.tokens_per_sec:.1f} tok/s)")
print(f"Chain: {result.chain_hash}")
```

## Batch inference
```python
requests = [
    {"prompt": f"Analyze EEG sample {i}", "max_tokens": 128}
    for i in range(100)
]
results = client.batch_generate(requests)
print(f"Total throughput: {sum(r.tokens for r in results) / sum(r.latency for r in results):.1f} tok/s")
```

## OpenAI-compatible streaming
```python
import openai
openai_client = openai.OpenAI(base_url="http://localhost:8000/v1", api_key="none")
for chunk in openai_client.completions.create(model="pax-27b", prompt="Hello", stream=True):
    print(chunk.choices[0].text, end="", flush=True)
```

## AIOSS Chain Append
```python
import hashlib, time

def aioss_append(chain_path, payload: bytes, module_id: str):
    entry_hash = hashlib.sha3_256(payload).digest()
    ts = int(time.time_ns()).to_bytes(8, 'big')
    with open(chain_path, 'rb') as f:
        f.seek(-32, 2); prev_hash = f.read(32)
    new_hash = hashlib.sha3_256(prev_hash + entry_hash + ts).digest()
    with open(chain_path, 'ab') as f:
        f.write(ts + entry_hash + new_hash)
    return new_hash.hex()
```
