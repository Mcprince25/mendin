"""LAS-15 research data model (research only — not production, not Pine).

Implements PROSPECTIVE_EVENT_SCHEMA_v0.1 and the attribution rules of
EVENT_IDENTITY_SPEC_v0.1. Records are immutable; every construction (including
dataclasses.replace) is validated, so identity claims cannot be added silently.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class IdentityError(ValueError):
    """A record claims event identity it has no evidence for."""


class CaseEra(str, Enum):
    PRE_EVENTSEQ_LEGACY = "PRE_EVENTSEQ_LEGACY"
    PROSPECTIVE = "PROSPECTIVE"


class EventDirection(str, Enum):
    BUY_SIDE = "BUY_SIDE"
    SELL_SIDE = "SELL_SIDE"


class WatchAttribution(str, Enum):
    EXACT = "EXACT"
    NO_WATCH_FOR_ORIGINAL_EVENT = "NO_WATCH_FOR_ORIGINAL_EVENT"
    AMBIGUOUS_EVENT_IDENTITY = "AMBIGUOUS_EVENT_IDENTITY"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    UNATTRIBUTED = "UNATTRIBUTED"


class FvgAttribution(str, Enum):
    SAME_EVENT = "SAME_EVENT"
    AMBIGUOUS_EVENT_IDENTITY = "AMBIGUOUS_EVENT_IDENTITY"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    UNATTRIBUTED = "UNATTRIBUTED"


class ProductionChangeJustified(str, Enum):
    NO = "NO"
    YES = "YES"


class ProspectiveEnrollment(str, Enum):
    NOT_AUTHORIZED = "NOT_AUTHORIZED"
    AUTHORIZED = "AUTHORIZED"


@dataclass(frozen=True)
class ResearchGovernance:
    production_change_justified: ProductionChangeJustified = ProductionChangeJustified.NO
    prospective_enrollment: ProspectiveEnrollment = ProspectiveEnrollment.NOT_AUTHORIZED


@dataclass(frozen=True)
class EventRecord:
    symbol: str
    research_case_id: str
    case_era: CaseEra
    data_provenance: str
    live_event_seq: Optional[int] = None
    event_direction: Optional[EventDirection] = None
    tested_level: Optional[float] = None
    sweep_extreme: Optional[float] = None
    event_timestamp: Optional[str] = None
    resolution_timestamp: Optional[str] = None
    thesis_close_timestamp: Optional[str] = None
    thesis_close_reason: Optional[str] = None
    watch_timestamp: Optional[str] = None
    ct_timestamp: Optional[str] = None
    fvg_timestamp: Optional[str] = None
    pullback_timestamp: Optional[str] = None
    entry_timestamp: Optional[str] = None
    btc_context: Optional[str] = None
    asset_4h_context: Optional[str] = None
    asset_1h_context: Optional[str] = None
    m2_class: Optional[str] = None
    event_family: Optional[str] = None
    fta: Optional[float] = None
    structural_stop: Optional[float] = None
    r_to_fta: Optional[float] = None
    # Identity evidence (supporting fields)
    watch_event_seq: Optional[int] = None
    fvg_event_seq: Optional[int] = None
    watch_attribution: WatchAttribution = WatchAttribution.UNATTRIBUTED
    fvg_attribution: FvgAttribution = FvgAttribution.UNATTRIBUTED

    def __post_init__(self):
        if not self.symbol:
            raise ValueError("SYMBOL is required")
        if not self.research_case_id:
            raise ValueError("RESEARCH_CASE_ID is required")
        if not self.data_provenance or not self.data_provenance.strip():
            raise ValueError("DATA_PROVENANCE is required")
        # Normalise string inputs to enums (raises on unknown values).
        object.__setattr__(self, "case_era", CaseEra(self.case_era))
        object.__setattr__(self, "watch_attribution", WatchAttribution(self.watch_attribution))
        object.__setattr__(self, "fvg_attribution", FvgAttribution(self.fvg_attribution))
        if self.event_direction is not None:
            object.__setattr__(self, "event_direction", EventDirection(self.event_direction))

        if self.case_era is CaseEra.PRE_EVENTSEQ_LEGACY:
            for name in ("live_event_seq", "watch_event_seq", "fvg_event_seq"):
                if getattr(self, name) is not None:
                    raise IdentityError(
                        f"{self.research_case_id}: PRE_EVENTSEQ_LEGACY case cannot carry {name.upper()}"
                    )

        if self.watch_attribution is WatchAttribution.EXACT and not self._matches(self.watch_event_seq):
            raise IdentityError(
                f"{self.research_case_id}: WATCH=EXACT requires LIVE_EVENT_SEQ and matching WATCH_EVENT_SEQ"
            )
        if self.fvg_attribution is FvgAttribution.SAME_EVENT and not self._matches(self.fvg_event_seq):
            raise IdentityError(
                f"{self.research_case_id}: FVG=SAME_EVENT requires LIVE_EVENT_SEQ and matching FVG_EVENT_SEQ"
            )

    def _matches(self, stage_seq: Optional[int]) -> bool:
        return self.live_event_seq is not None and stage_seq == self.live_event_seq
