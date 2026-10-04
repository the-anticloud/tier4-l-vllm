# Radon_Complexity_Lab_Results
**Project:** `L_VLLM` | **Status:** `PASS` | **Run:** `2026-09-30T17:14:20.030944+00:00`

**Framework:** [Radon — Cyclomatic Complexity & Maintainability Index](https://radon.readthedocs.io/)

## Key Metrics

- **files_analyzed:** `10`
- **average_complexity:** `{'grade': 'B', 'score': 5.223404255319149}`
- **complexity_grade:** `B`
- **complexity_score:** `5.223404255319149`
- **mi_output:** `E:\fenta\Downloads\The Anticloud\TIER_4_INFERENCE_AGENTS\L_VLLM\UPSTREAM\setup.py - C (0.00)
E:\fenta\Downloads\The Anti`

## Raw Output (first 50 lines)
```
E:\fenta\Downloads\The Anticloud\TIER_4_INFERENCE_AGENTS\L_VLLM\UPSTREAM\setup.py
    M 987:4 precompiled_wheel_utils.extract_precompiled_and_patch_package - C (20)
    F 1258:0 get_vllm_version - C (19)
    F 1312:0 get_requirements - C (15)
    M 255:4 cmake_build_ext.configure - C (14)
    M 828:4 precompiled_wheel_utils.determine_wheel_url_rocm - C (12)
    M 898:4 precompiled_wheel_utils.determine_wheel_url - C (12)
    C 206:0 cmake_build_ext - C (11)
    M 399:4 cmake_build_ext.run - B (9)
    M 686:4 precompiled_wheel_utils.resolve_rocm_wheel_variant - B (9)
    F 150:0 find_tcmalloc - B (8)
    M 213:4 cmake_build_ext.compute_num_jobs - B (8)
    M 340:4 cmake_build_ext.build_extensions - B (8)
    C 517:0 precompiled_wheel_utils - B (8)
    M 521:4 precompiled_wheel_utils.fetch_metadata_for_variant - B (8)
    M 603:4 precompiled_wheel_utils.detect_system_cuda_variant - B (7)
    C 487:0 precompiled_build_rust - B (6)
    M 1114:4 precompiled_wheel_utils.get_base_commit_in_main_branch - B (6)
    F 1209:0 get_rocm_version - A (5)
    M 490:4 precompiled_build_rust.run - A (5)
    M 587:4 precompiled_wheel_utils.is_rocm_system - A (5)
    M 735:4 precompiled_wheel_utils.warn_if_rocm_torch_version_mismatch - A (5)
    F 78:0 get_missing_precompiled_rust_extension_modules - A (4)
    M 650:4 precompiled_wheel_utils.detect_system_rocm_variant - A (4)
    M 791:4 precompiled_wheel_utils.fetch_wheel_from_pypi_index - A (4)
    F 140:0 should_bundle_tcmalloc - A (3)
    F 
```

---
_Anticloud Independent Benchmark — 2026-09-30T17:14:20.030944+00:00_