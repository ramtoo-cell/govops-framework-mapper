
"""Cross-framework control mapper.

Controls get written once per framework (NIST AI RMF, ISO/IEC 42001,
SOC 2) and then mapped by hand in spreadsheets. This module registers
frameworks with their controls, records many-to-many mappings between
them, and answers: what is our coverage of framework B from framework
A, which controls are unmapped, and what does the mapping matrix look
like for the auditors?

Design:
- Mappings are directed pairs between (framework, control) tuples;
  many-to-many is allowed because real mappings are messy.
- Coverage is computed per ordered framework pair: mapping A->B does
  not imply B->A.
- matrix() rows pair every source control with its target (or None),
  which is exactly the shape auditors paste into workpapers.
- All lookups validate framework and control existence up front.
"""
from __future__ import annotations


class FrameworkMapper:
    """Control mappings across governance frameworks."""

    def __init__(self):
        self._frameworks = {}
        self._mappings = set()

    def add_framework(self, name, controls):
        """Register a framework: controls maps control_id -> title."""
        if name in self._frameworks:
            raise ValueError("duplicate framework %r" % (name,))
        if not controls:
            raise ValueError("framework needs at least one control")
        self._frameworks[name] = dict(controls)
        return name

    def frameworks(self):
        return sorted(self._frameworks)

    def _require(self, framework, control_id):
        if framework not in self._frameworks:
            raise KeyError("unknown framework %r" % (framework,))
        if control_id not in self._frameworks[framework]:
            raise KeyError("unknown control %r in %r" % (control_id, framework))

    def add_mapping(self, from_fw, from_control, to_fw, to_control):
        """Map one control to another across frameworks."""
        self._require(from_fw, from_control)
        self._require(to_fw, to_control)
        key = (from_fw, from_control, to_fw, to_control)
        if key in self._mappings:
            raise ValueError("duplicate mapping")
        self._mappings.add(key)
        return key

    def mapped_from(self, framework, control_id):
        """[(framework, control_id)] this control maps to."""
        self._require(framework, control_id)
        return sorted((tfw, tcid) for fw, cid, tfw, tcid in self._mappings
                      if fw == framework and cid == control_id)

    def mapped_to(self, framework, control_id):
        """[(framework, control_id)] mapping into this control."""
        self._require(framework, control_id)
        return sorted((fw, cid) for fw, cid, tfw, tcid in self._mappings
                      if tfw == framework and tcid == control_id)

    def coverage(self, source_fw, target_fw):
        """Share of source_fw controls mapped to target_fw."""
        if source_fw not in self._frameworks:
            raise KeyError("unknown framework %r" % (source_fw,))
        if target_fw not in self._frameworks:
            raise KeyError("unknown framework %r" % (target_fw,))
        source = self._frameworks[source_fw]
        mapped = {cid for fw, cid, tfw, _ in self._mappings
                  if fw == source_fw and tfw == target_fw}
        total = len(source)
        return {"source": source_fw, "target": target_fw, "total": total,
                "mapped": len(mapped),
                "pct": round(len(mapped) / total, 3) if total else 1.0}

    def unmapped(self, framework, against):
        """Controls in framework with no mapping to `against`."""
        self._require(framework, next(iter(self._frameworks[framework])))
        mapped = {cid for fw, cid, tfw, _ in self._mappings
                  if fw == framework and tfw == against}
        return sorted(cid for cid in self._frameworks[framework]
                      if cid not in mapped)

    def matrix(self, from_fw, to_fw):
        """Rows of (from_id, from_title, to_id|None, to_title|None)."""
        if from_fw not in self._frameworks:
            raise KeyError("unknown framework %r" % (from_fw,))
        if to_fw not in self._frameworks:
            raise KeyError("unknown framework %r" % (to_fw,))
        targets = {}
        for fw, cid, tfw, tcid in self._mappings:
            if fw == from_fw and tfw == to_fw:
                targets.setdefault(cid, []).append(tcid)
        rows = []
        for cid in sorted(self._frameworks[from_fw]):
            tcid = targets[cid][0] if cid in targets else None
            rows.append((cid, self._frameworks[from_fw][cid], tcid,
                         self._frameworks[to_fw].get(tcid) if tcid else None))
        return rows

    def mapping_count(self):
        return len(self._mappings)
