"""Canonical knowledge package.

Exports schema, registry, validators and read-only adapters.
"""

from . import registry, validators, synthesis

# Try to expose schema if available in canonical location or fallback locations
try:
	from .schema import *  # type: ignore
except Exception:
	try:
		# fallback to doctrine/schema
		from cold_strategist.doctrine.schema import *  # type: ignore
	except Exception:
		# schema not available in canonical path; keep package importable
		pass

__all__ = ["registry", "validators", "synthesis"]
