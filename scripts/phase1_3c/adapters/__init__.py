"""
scripts/phase1_3c/adapters/__init__.py
Authoritative Upstream Production Adapters for Phase 1.3C.
"""

from .production_adapters import (
    JMdictAdapter,
    KANJIDIC2Adapter,
    JoyoOfficialAdapter,
    NGSLAdapter,
    NGSLSpokenAdapter,
    NAWLAdapter,
    BSLAdapter,
    TSLAdapter,
    VietnameseFrequencyAdapter,
    HanVietAdapter,
    JLPTConsensusAdapter
)

__all__ = [
    "JMdictAdapter",
    "KANJIDIC2Adapter",
    "JoyoOfficialAdapter",
    "NGSLAdapter",
    "NGSLSpokenAdapter",
    "NAWLAdapter",
    "BSLAdapter",
    "TSLAdapter",
    "VietnameseFrequencyAdapter",
    "HanVietAdapter",
    "JLPTConsensusAdapter"
]
