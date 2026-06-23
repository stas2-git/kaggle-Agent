"""Actuarial portfolio monitoring agent package.

The package intentionally avoids importing ADK application objects at import
time while the project is being upgraded phase-by-phase. This keeps existing
deterministic tools and tests usable before ``root_agent``/``app`` are added in
the ADK implementation phase.
"""

__all__: list[str] = []
