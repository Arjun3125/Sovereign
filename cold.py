#!/usr/bin/env python3
"""
Cold Strategist - Sovereign Counsel Engine

Entry point for normal and war mode analysis.

Usage:
    python cold.py normal --domain career --stakes high
    python cold.py war --domain negotiation --stakes medium --arena career
"""

from cold_strategist.cli.main import main

if __name__ == "__main__":
    main()
