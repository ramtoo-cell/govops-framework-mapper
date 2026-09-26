# Cross-Framework Control Mapper

Maps controls between governance frameworks with coverage scoring, unmapped-control detection, and mapping matrices.

**Stack:** Python 3.12 · stdlib only · unittest

## Problem

Controls get written once per framework (NIST AI RMF, ISO/IEC 42001,
SOC 2) and then mapped by hand in spreadsheets. This module registers
frameworks with their controls, records many-to-many mappings between
them, and answers: what is our coverage of framework B from framework
A, which controls are unmapped, and what does the mapping matrix look
like for the auditors?

## Design decisions

- Mappings are directed pairs between (framework, control) tuples;
- Coverage is computed per ordered framework pair: mapping A->B does
- matrix() rows pair every source control with its target (or None),
- All lookups validate framework and control existence up front.

## Layout

- `README.md`
- `src/framework_mapper.py`
- `tests/test_framework_mapper.py`
- `LICENSE`
- `.gitignore`

## Setup

No third-party dependencies — Python 3.11+ standard library only.

```bash
cd govops-framework-mapper
python -m unittest discover -s tests -v
```

## Usage

```python
from src.framework_mapper import FrameworkMapper

m = FrameworkMapper()
m.add_framework("NIST-AI-RMF", {"GV-1": "Governance"})
m.add_framework("ISO-42001", {"6.1": "Risk assessment"})
m.add_mapping("NIST-AI-RMF", "GV-1", "ISO-42001", "6.1")
print(m.coverage("NIST-AI-RMF", "ISO-42001"))
```

## License

MIT — see [LICENSE](LICENSE).
