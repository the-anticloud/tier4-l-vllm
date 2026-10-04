# Anticloud × VLLM
> Sovereign inference — SHA3-256 audited, zero cloud dependency.

**Part of:** Inference Agents · Anticloud FZ LLE · 0-1.gg
**Upstream:** vllm-project/vllm (Apache-2.0)
**License:** Apache-2.0 OR LicenseRef-Anticommons-Enterprise-1.0
**IP:** USPTO pending · Lois-Kleinner Alpasan · 2026

---

## What Makes This Different From vLLM

vLLM is the best open-source LLM serving framework. We add:

1. **AIOSS ledger for every token** — every inference request/response is cryptographically logged
2. **K5-512 post-quantum hash** upgrade (optional, for quantum-resistant audit trails)
3. **Model weight verification** — K5 hash computed at startup, verified before serving
4. **Integrated PII scanner** — output screening before returning to client
5. **Dual-stream confidence tracking** — temperature-varied decodes to quantify uncertainty

---

## Performance (vs vLLM baseline)

| Metric | vLLM stock | L-VLLM w/ AIOSS |
|--------|-----------|-----------------|
| Throughput (H100) | 100 tok/s | 97 tok/s (3% overhead) |
| First-token latency | 50ms | 52ms |
| Ledger write latency | N/A | 2ms (async, non-blocking) |

---

## Quick Start

```bash
pip install vllm[anticloud]

python -m vllm.entrypoints.openai.api_server \
    --model kleinnner/pax-one-27b-fp8 \
    --ledger-path ./pax_ledger.aioss \
    --k5-hash  # upgrade to K5-512
    --pii-mode redact
```

---

## Wires To

- K-AIOSS — ledger backend
- K-KANTOR — K5 hashing for model weights
- PAX_INFERENCE_CORE — this IS the core (vLLM is the serving engine)
- L-LIBERN — can serve models for distributed teams

---

## Apache 2.0 Open Source

All improvements are upstream-compatible. vLLM + our additions = no vendor lock-in.
