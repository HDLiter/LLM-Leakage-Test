"""R5A measurement stack.

This namespace contains the implementation of the frozen R5A measurement
framework defined in:

- refine-logs/reviews/R5A_STEP2/R5A_FROZEN_SHORTLIST.md  (scope freeze)
- refine-logs/reviews/R5A_STEP2/MEASUREMENT_FRAMEWORK.md (four-layer framework)
- config/prompts/R5A_OPERATOR_SCHEMA.md                  (operator contracts)
- plans/phase7-pilot-implementation.md                   (Phase 7 plan)

Everything under this package targets the Phase 7 pilot. Legacy single-model
code lives under archive/pre_r5a_src/ and must not be imported from here.
"""

__version__ = "0.1.0"
