
"""Tests for the cross-framework control mapper."""
import unittest

from src.framework_mapper import FrameworkMapper


def _mapper():
    m = FrameworkMapper()
    m.add_framework("NIST-AI-RMF", {"GV-1": "Governance", "MS-1": "Measurement"})
    m.add_framework("ISO-42001", {"6.1": "Risk assessment", "9.1": "Monitoring"})
    m.add_mapping("NIST-AI-RMF", "GV-1", "ISO-42001", "6.1")
    return m


class TestFrameworkMapper(unittest.TestCase):
    def test_mapped_from_and_to(self):
        m = _mapper()
        self.assertEqual(m.mapped_from("NIST-AI-RMF", "GV-1"), [("ISO-42001", "6.1")])
        self.assertEqual(m.mapped_to("ISO-42001", "6.1"), [("NIST-AI-RMF", "GV-1")])
        self.assertEqual(m.mapped_from("NIST-AI-RMF", "MS-1"), [])

    def test_coverage(self):
        cov = _mapper().coverage("NIST-AI-RMF", "ISO-42001")
        self.assertEqual(cov["total"], 2)
        self.assertEqual(cov["mapped"], 1)
        self.assertEqual(cov["pct"], 0.5)

    def test_coverage_is_directional(self):
        cov = _mapper().coverage("ISO-42001", "NIST-AI-RMF")
        self.assertEqual(cov["mapped"], 0)

    def test_unmapped(self):
        self.assertEqual(_mapper().unmapped("NIST-AI-RMF", "ISO-42001"), ["MS-1"])

    def test_matrix(self):
        rows = _mapper().matrix("NIST-AI-RMF", "ISO-42001")
        self.assertEqual(rows[0], ("GV-1", "Governance", "6.1", "Risk assessment"))
        self.assertEqual(rows[1][2], None)
        self.assertEqual(rows[1][3], None)

    def test_unknown_control_raises(self):
        with self.assertRaises(KeyError):
            _mapper().add_mapping("NIST-AI-RMF", "ZZ", "ISO-42001", "6.1")

    def test_duplicate_mapping_raises(self):
        m = _mapper()
        with self.assertRaises(ValueError):
            m.add_mapping("NIST-AI-RMF", "GV-1", "ISO-42001", "6.1")

    def test_frameworks(self):
        self.assertEqual(_mapper().frameworks(), ["ISO-42001", "NIST-AI-RMF"])
        self.assertEqual(_mapper().mapping_count(), 1)

    def test_duplicate_framework_raises(self):
        m = FrameworkMapper()
        m.add_framework("F", {"a": "A"})
        with self.assertRaises(ValueError):
            m.add_framework("F", {"b": "B"})


if __name__ == "__main__":
    unittest.main()
