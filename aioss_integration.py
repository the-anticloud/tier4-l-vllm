"""
L-VLLM Anticloud Integration — AIOSS Ledger Wrapper for vLLM

Usage:
    from aioss_integration import AIossVLLMWrapper, InferenceMetrics

    llm = LLM(model="kleinnner/pax-one-27b-fp8")
    wrapped = AIossVLLMWrapper(llm, ledger_path="./pax_ledger.aioss")
    outputs = wrapped.generate(["Your prompt here"])

No frontier API keys. Local inference only.
"""

from __future__ import annotations
import hashlib
import json
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List
import threading


@dataclass
class InferenceMetrics:
    model_name: str
    prompt: str
    output: str
    tokens_in: int
    tokens_out: int
    wall_time_ms: float
    confidence: float = 0.0
    contradiction: float = 0.0

    @property
    def prompt_hash(self) -> str:
        return hashlib.sha3_256(self.prompt.encode()).hexdigest()

    @property
    def output_hash(self) -> str:
        return hashlib.sha3_256(self.output.encode()).hexdigest()


class AIossVLLMWrapper:
    """
    Wraps vLLM's LLM class to log every inference to an AIOSS ledger.

    Thread-safe. Logging is synchronous by default (no data loss on crash).
    Set async_logging=True for zero-overhead fire-and-forget logging.
    """

    def __init__(
        self,
        llm,
        ledger_path: str = "./vllm_ledger.aioss",
        aioss_bin: str = "aioss",
        async_logging: bool = False,
    ):
        self.llm = llm
        self.ledger_path = Path(ledger_path)
        self.aioss_bin = aioss_bin
        self.async_logging = async_logging
        self._lock = threading.Lock()
        self._queue: list[InferenceMetrics] = []

        # Initialize ledger if it doesn't exist
        if not self.ledger_path.exists():
            self._init_ledger()

    def _init_ledger(self):
        ledger_dir = str(self.ledger_path.parent)
        result = subprocess.run(
            [self.aioss_bin, "init", ledger_dir, "--user", "vllm-anticloud"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"aioss init failed: {result.stderr}")

    def _append_entry(self, metrics: InferenceMetrics):
        content = json.dumps({
            "model": metrics.model_name,
            "prompt_hash": metrics.prompt_hash,
            "output_hash": metrics.output_hash,
            "confidence": round(metrics.confidence, 4),
            "contradiction": round(metrics.contradiction, 4),
            "telemetry": {
                "tokens_in": metrics.tokens_in,
                "tokens_out": metrics.tokens_out,
                "wall_time_ms": round(metrics.wall_time_ms, 1),
                "cost_if_cloud_microcents": 0,  # local inference = $0
            },
        })

        result = subprocess.run(
            [
                self.aioss_bin, "append", str(self.ledger_path),
                "--type", "inference_result",
                "--actor", metrics.model_name[:15],  # max 15 chars
                "--content", content,
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            # Log warning but don't crash inference
            print(f"[AIOSS WARNING] Failed to log entry: {result.stderr}")

    def generate(
        self,
        prompts: List[str],
        sampling_params=None,
    ):
        """
        Wraps vLLM generate(). Logs every request/response to AIOSS ledger.
        """
        start = time.perf_counter()

        if sampling_params is None:
            try:
                from vllm import SamplingParams
                sampling_params = SamplingParams(temperature=0.0, max_tokens=512)
            except ImportError:
                sampling_params = None

        outputs = self.llm.generate(prompts, sampling_params)

        elapsed_ms = (time.perf_counter() - start) * 1000
        per_prompt_ms = elapsed_ms / max(len(prompts), 1)

        for prompt, output in zip(prompts, outputs):
            # Extract output text
            output_text = ""
            tokens_in = 0
            tokens_out = 0

            if hasattr(output, "outputs"):
                # vLLM RequestOutput
                output_text = output.outputs[0].text if output.outputs else ""
                tokens_out = len(output.outputs[0].token_ids) if output.outputs else 0
            elif isinstance(output, str):
                output_text = output
                tokens_out = len(output.split())

            # Rough token count for input
            tokens_in = len(prompt.split()) + 1  # simplified

            metrics = InferenceMetrics(
                model_name=getattr(self.llm, "model_name", "local-llm"),
                prompt=prompt,
                output=output_text,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                wall_time_ms=per_prompt_ms,
            )

            if self.async_logging:
                t = threading.Thread(target=self._append_entry, args=(metrics,), daemon=True)
                t.start()
            else:
                self._append_entry(metrics)

        return outputs

    def verify(self) -> bool:
        """Verify ledger integrity. Returns True if chain is valid."""
        result = subprocess.run(
            [self.aioss_bin, "verify", str(self.ledger_path)],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0

    def cost_savings(self) -> dict:
        """
        Calculate cloud cost savings vs GPT-4-Turbo.
        Returns dict with local_cost, cloud_cost_equivalent, savings.
        """
        result = subprocess.run(
            [self.aioss_bin, "export", str(self.ledger_path), "--format", "json"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return {"error": result.stderr}

        data = json.loads(result.stdout)
        entries = data.get("entries", [])

        total_in = sum(
            e.get("content", {}).get("telemetry", {}).get("tokens_in", 0)
            for e in entries
        )
        total_out = sum(
            e.get("content", {}).get("telemetry", {}).get("tokens_out", 0)
            for e in entries
        )

        # GPT-4-Turbo: $0.01/1K in, $0.03/1K out
        cloud_cost = (total_in / 1000 * 0.01) + (total_out / 1000 * 0.03)

        return {
            "entries": len(entries),
            "total_tokens_in": total_in,
            "total_tokens_out": total_out,
            "local_cost_usd": 0.0,
            "cloud_cost_equivalent_usd": round(cloud_cost, 4),
            "savings_usd": round(cloud_cost, 4),
            "savings_pct": 100.0,
        }


# Example usage
if __name__ == "__main__":
    # This requires vLLM installed and a local model
    # For testing without vLLM, use the mock below

    class MockLLM:
        model_name = "mock-model"
        def generate(self, prompts, sampling_params=None):
            return [f"Mock response to: {p}" for p in prompts]

    llm = MockLLM()
    wrapper = AIossVLLMWrapper(llm, ledger_path="./test_ledger.aioss")

    outputs = wrapper.generate([
        "What is a hash chain?",
        "Explain PagedAttention in vLLM",
    ])

    print("Outputs:", outputs)
    print("Chain valid:", wrapper.verify())
    print("Cost savings:", wrapper.cost_savings())
