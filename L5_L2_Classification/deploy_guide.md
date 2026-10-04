# Deploy Guide — L_VLLM
**Tier:** TIER_4_INFERENCE_AGENTS | **Stack:** Python 3.11, vllm 0.4+, PyTorch 2.10+, CUDA 12.x, PAX 27B, AIOSS_FORMAT
**Air-gap capable after initial setup.**

## Prerequisites
Python 3.11+, vllm 0.4+, PyTorch 2.10+, CUDA 12.x, T4 (15.6GB) or A100 (40/80GB).

## Environment
T4 minimum (15.6GB VRAM for PAX 27B Q4). A100 for full FP16. CUDA 12.x. 32GB system RAM.

## AIOSS Integration
```bash
aioss init --module L_VLLM --output ./l_vllm.aioss
aioss append --chain ./l_vllm.aioss --payload ./output.bin --module L_VLLM
aioss verify --chain ./l_vllm.aioss
```

## Air-Gap Setup
```bash
pip download -r requirements.txt -d ./wheels/
pip install --no-index --find-links ./wheels/ -r requirements.txt
```

## PAX 27B Harness Wiring
```python
from anticloud_pax import PAXHarness
harness = PAXHarness(
    model_path="./pax-27b-q4.gguf",
    module="L_VLLM",
    aioss_chain="./L_VLLM.aioss",
    classification="L5_NARROW_L2_GENERAL"
)
result = harness.process(input_data)
```

## Verification
```bash
aioss verify --chain ./L_VLLM.aioss --verbose
python -m L_VLLM.tests.smoke
```
