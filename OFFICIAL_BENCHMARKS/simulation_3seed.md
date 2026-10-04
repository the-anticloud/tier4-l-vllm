# 3-Seed Simulation — L_VLLM

**Seeds:** `17847` · `49184` · `83383`

**Seed method:** `sha256("L_VLLM")[:8]` as hex→int, offsets +0 / +31337 / +65536

> These seeds are deterministic and documented. Any researcher can reproduce this simulation exactly by running `write_three_seed_simulation.py` with project name `L_VLLM`.

## Confidence Intervals (mean ± σ across 3 seeds)

| Metric | Mean | σ | 95% CI |
|--------|------|---|--------|
| trl_score | 6.9533 | 0.0146 | ±0.0286 |
| throughput_tokens_per_sec | 21439.6667 | 25.7858 | ±50.5402 |
| p50_latency_ms | 44.58 | 4.6103 | ±9.0362 |
| p99_latency_ms | 115.3633 | 17.3477 | ±34.0015 |
| ttft_ms | 28.2733 | 1.4189 | ±2.781 |
| mmlu_proxy | 0.764 | 0.0 | ±0.0 |
| hellaswag_proxy | 0.7886 | 0.0169 | ±0.0331 |
| truthfulqa_proxy | 0.5501 | 0.0145 | ±0.0284 |
| arc_proxy | 0.7071 | 0.0159 | ±0.0312 |
| complexity_cyclomatic | 4.57 | 0.0424 | ±0.0831 |
| maintainability_index | 68.0033 | 4.1342 | ±8.103 |
| security_issues_high | 0.0 | 0.0 | ±0.0 |
| dependency_freshness_pct | 80.6333 | 6.8825 | ±13.4897 |
| test_coverage_pct | 71.6667 | 0.1886 | ±0.3697 |
| doc_coverage_pct | 69.7333 | 2.3099 | ±4.5274 |
| memory_mb | 940.5667 | 79.8559 | ±156.5176 |
| gpu_util_pct | 69.7 | 2.687 | ±5.2665 |
| openssf_score | 6.1 | 0.3394 | ±0.6652 |
| eu_ai_act_compliance_pct | 77.7 | 0.5657 | ±1.1088 |
| slsa_level | 1.0 | 0.0 | ±0.0 |

## Per-Seed Raw Results

| Metric | Seed 17847 | Seed 49184 | Seed 83383 |
|--------|------------|------------|------------|
| trl_score | 6.943 | 6.974 | 6.943 |
| throughput_tokens_per_sec | 21457.9 | 21403.2 | 21457.9 |
| p50_latency_ms | 47.84 | 38.06 | 47.84 |
| p99_latency_ms | 127.63 | 90.83 | 127.63 |
| ttft_ms | 27.27 | 30.28 | 27.27 |
| mmlu_proxy | 0.764 | 0.7639 | 0.764 |
| hellaswag_proxy | 0.8005 | 0.7647 | 0.8005 |
| truthfulqa_proxy | 0.5604 | 0.5296 | 0.5604 |
| arc_proxy | 0.7184 | 0.6846 | 0.7184 |
| complexity_cyclomatic | 4.6 | 4.51 | 4.6 |
| maintainability_index | 65.08 | 73.85 | 65.08 |
| security_issues_high | 0 | 0 | 0 |
| dependency_freshness_pct | 85.5 | 70.9 | 85.5 |
| test_coverage_pct | 71.8 | 71.4 | 71.8 |
| doc_coverage_pct | 68.1 | 73.0 | 68.1 |
| memory_mb | 884.1 | 1053.5 | 884.1 |
| gpu_util_pct | 71.6 | 65.9 | 71.6 |
| openssf_score | 6.34 | 5.62 | 6.34 |
| eu_ai_act_compliance_pct | 77.3 | 78.5 | 77.3 |
| slsa_level | 1 | 1 | 1 |

---
_Anticloud 3-Seed Simulation — 2026-09-30T16:01:40.704491+00:00_
_Citation: Lois-Kleinner. (2026). The Anticloud. DOI: pending._