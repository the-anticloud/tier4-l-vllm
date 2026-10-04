"""
AIOSS Ledger Test Suite — L_VLLM
Author: Lois-Kleinner Alpasan / Anticloud FZ LLE / 0-1.gg
USPTO drafting/pending 2026.

Run: pytest tests/test_aioss_ledger.py -v
All tests run offline, no network required.
"""
import hashlib
import json
import sys
import types
from pathlib import Path

import pytest

# Make aioss_integration importable without vllm installed
_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "src"))

# Stub vllm so import doesn't fail in CI
if "vllm" not in sys.modules:
    vllm_stub = types.ModuleType("vllm")
    vllm_stub.SamplingParams = lambda **kw: kw
    sys.modules["vllm"] = vllm_stub

import aioss_integration as aioss


# ── helpers ───────────────────────────────────────────────────────────────────

def _sha3(data: str) -> str:
    return hashlib.sha3_256(data.encode()).hexdigest()


def _chain(prev: str, content: str) -> str:
    return _sha3(prev + content)


# ── tests ─────────────────────────────────────────────────────────────────────

class TestSHA3HashChain:
    """Verifies the AIOSS SHA3-256 chain algorithm independently."""

    def test_sha3_hash_chain(self):
        """3-entry chain: each hash = sha3_256(prev_hash || content)."""
        entries = [
            {"content": "inference: prompt_hash=abc123 output_hash=def456 tokens_in=12 tokens_out=50"},
            {"content": "inference: prompt_hash=bcd234 output_hash=efg567 tokens_in=8 tokens_out=32"},
            {"content": "inference: prompt_hash=cde345 output_hash=fgh678 tokens_in=20 tokens_out=80"},
        ]
        prev_hash = "0" * 64  # genesis
        for entry in entries:
            expected = _chain(prev_hash, entry["content"])
            assert len(expected) == 64, "SHA3-256 must produce 64-char hex"
            assert all(c in "0123456789abcdef" for c in expected), "Must be hex"
            # Verify determinism: same inputs → same output
            assert _chain(prev_hash, entry["content"]) == expected
            prev_hash = expected

    def test_chain_is_tamper_evident(self):
        """Modifying any entry breaks all subsequent hashes."""
        content_a = "entry A"
        content_b = "entry B"
        genesis = "0" * 64
        h1 = _chain(genesis, content_a)
        h2 = _chain(h1, content_b)

        # Tamper entry A
        h1_tampered = _chain(genesis, content_a + " TAMPERED")
        h2_from_tampered = _chain(h1_tampered, content_b)

        assert h1_tampered != h1, "Tampered entry must change hash"
        assert h2_from_tampered != h2, "Downstream hash must break"

    def test_genesis_hash_is_zeros(self):
        """Genesis block starts with 64 zero hex chars."""
        genesis = "0" * 64
        assert len(genesis) == 64
        assert genesis == "0000000000000000000000000000000000000000000000000000000000000000"


class TestInferenceMetricsHashes:
    """Verifies InferenceMetrics produces SHA3-256 hashes."""

    def test_prompt_hash_is_sha3_256(self):
        m = aioss.InferenceMetrics(
            model_name="test-model",
            prompt="What is the capital of France?",
            output="Paris.",
            tokens_in=7,
            tokens_out=2,
            wall_time_ms=45.2,
        )
        expected = hashlib.sha3_256("What is the capital of France?".encode()).hexdigest()
        assert m.prompt_hash == expected
        assert len(m.prompt_hash) == 64

    def test_output_hash_is_sha3_256(self):
        m = aioss.InferenceMetrics(
            model_name="test-model",
            prompt="Ping",
            output="Pong",
            tokens_in=1,
            tokens_out=1,
            wall_time_ms=12.0,
        )
        expected = hashlib.sha3_256("Pong".encode()).hexdigest()
        assert m.output_hash == expected

    def test_hashes_differ_for_different_content(self):
        m1 = aioss.InferenceMetrics("m", "prompt A", "output X", 1, 1, 10.0)
        m2 = aioss.InferenceMetrics("m", "prompt B", "output Y", 1, 1, 10.0)
        assert m1.prompt_hash != m2.prompt_hash
        assert m1.output_hash != m2.output_hash

    def test_empty_strings_hash_deterministically(self):
        m = aioss.InferenceMetrics("m", "", "", 0, 0, 0.0)
        assert m.prompt_hash == hashlib.sha3_256(b"").hexdigest()
        assert m.output_hash == hashlib.sha3_256(b"").hexdigest()


class TestMockGenerate:
    """Verifies AIossVLLMWrapper with MockLLM (no vLLM, no network)."""

    def _make_wrapper(self, tmp_path):
        class MockLLM:
            model_name = "mock-anticloud"
            def generate(self, prompts, sampling_params=None):
                return [f"Mock: {p}" for p in prompts]

        # Patch subprocess so aioss CLI calls don't fail in CI
        import unittest.mock as mock
        with mock.patch("subprocess.run") as mock_run:
            mock_run.return_value = mock.MagicMock(returncode=0, stdout="", stderr="")
            wrapper = aioss.AIossVLLMWrapper(
                MockLLM(),
                ledger_path=str(tmp_path / "test.aioss"),
                async_logging=False,
            )
        return wrapper

    def test_mock_generate_returns_list(self, tmp_path):
        import unittest.mock as mock
        with mock.patch("subprocess.run") as mock_run:
            mock_run.return_value = mock.MagicMock(returncode=0, stdout="", stderr="")
            wrapper = self._make_wrapper(tmp_path)
            outputs = wrapper.generate(["Hello world", "Test prompt"])
        assert isinstance(outputs, list)
        assert len(outputs) == 2

    def test_mock_generate_single_prompt(self, tmp_path):
        import unittest.mock as mock
        with mock.patch("subprocess.run") as mock_run:
            mock_run.return_value = mock.MagicMock(returncode=0, stdout="", stderr="")
            wrapper = self._make_wrapper(tmp_path)
            outputs = wrapper.generate(["Single prompt"])
        assert len(outputs) == 1

    def test_generate_calls_subprocess_for_logging(self, tmp_path):
        import unittest.mock as mock
        call_count = []
        def mock_run(*args, **kwargs):
            call_count.append(1)
            return mock.MagicMock(returncode=0, stdout="", stderr="")

        with mock.patch("subprocess.run", side_effect=mock_run):
            wrapper = self._make_wrapper(tmp_path)
            call_count.clear()  # reset after init
            wrapper.generate(["prompt 1", "prompt 2"])
        # Should have called subprocess at least twice (one per prompt for logging)
        assert len(call_count) >= 2, f"Expected ≥2 subprocess calls, got {len(call_count)}"


class TestCostSavingsStructure:
    """Verifies cost_savings() returns the expected schema."""

    REQUIRED_KEYS = {
        "entries", "total_tokens_in", "total_tokens_out",
        "local_cost_usd", "cloud_cost_equivalent_usd",
        "savings_usd", "savings_pct",
    }

    def test_cost_savings_keys_present(self, tmp_path):
        import unittest.mock as mock
        mock_export = json.dumps({
            "entries": [
                {"content": {"telemetry": {"tokens_in": 10, "tokens_out": 50}}},
                {"content": {"telemetry": {"tokens_in": 5, "tokens_out": 20}}},
            ]
        })

        class MockLLM:
            model_name = "mock"
            def generate(self, p, s=None): return p

        with mock.patch("subprocess.run") as mock_run:
            mock_run.return_value = mock.MagicMock(returncode=0, stdout=mock_export, stderr="")
            wrapper = aioss.AIossVLLMWrapper(MockLLM(), str(tmp_path / "t.aioss"))
            result = wrapper.cost_savings()

        assert isinstance(result, dict)
        missing = self.REQUIRED_KEYS - set(result.keys())
        assert not missing, f"Missing keys: {missing}"

    def test_local_cost_is_zero(self, tmp_path):
        import unittest.mock as mock
        mock_export = json.dumps({"entries": [{"content": {"telemetry": {"tokens_in": 100, "tokens_out": 200}}}]})

        class MockLLM:
            model_name = "mock"
            def generate(self, p, s=None): return p

        with mock.patch("subprocess.run") as mock_run:
            mock_run.return_value = mock.MagicMock(returncode=0, stdout=mock_export, stderr="")
            wrapper = aioss.AIossVLLMWrapper(MockLLM(), str(tmp_path / "t.aioss"))
            result = wrapper.cost_savings()

        assert result["local_cost_usd"] == 0.0, "Local inference must be $0"
        assert result["savings_pct"] == 100.0, "Savings must be 100% vs cloud"

    def test_cloud_cost_calculation(self, tmp_path):
        """$0.01/1K in + $0.03/1K out (GPT-4-Turbo rates)."""
        import unittest.mock as mock
        mock_export = json.dumps({"entries": [
            {"content": {"telemetry": {"tokens_in": 1000, "tokens_out": 1000}}}
        ]})

        class MockLLM:
            model_name = "mock"
            def generate(self, p, s=None): return p

        with mock.patch("subprocess.run") as mock_run:
            mock_run.return_value = mock.MagicMock(returncode=0, stdout=mock_export, stderr="")
            wrapper = aioss.AIossVLLMWrapper(MockLLM(), str(tmp_path / "t.aioss"))
            result = wrapper.cost_savings()

        # 1000 in @ $0.01/1K = $0.01, 1000 out @ $0.03/1K = $0.03 → $0.04
        assert abs(result["cloud_cost_equivalent_usd"] - 0.04) < 0.001
