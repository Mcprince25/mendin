"""EARLY_REBREAK_RESEARCH_v0.1 research data model.

RESEARCH ONLY. Not production, not Pine, not an alert specification.
Implements the record structure and invariants of EARLY_REBREAK_RESEARCH_v0.1.md:

- three execution branches (DIRECT_CONTROL_BREAK, PULLBACK_REBREAK,
  FROZEN_A_PLUS) measured against ONE parent event;
- event identity: downstream objects are SAME_EVENT only when their eventSeq
  equals the parent LIVE_EVENT_SEQ, otherwise AMBIGUOUS; a stage carrying a
  different eventSeq, or predating the parent event, is rejected;
- structural stop comes from thesis invalidation, never from desired R;
- FTA is frozen before entry, and R is computed only from (stop, frozen FTA).

No thresholds are defined here. Raw measurements only.
All objects are immutable and validated on construction.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Optional, Tuple

from research_model import CaseEra, EventDirection, IdentityError

PROTOCOL_VERSION = "EARLY_REBREAK_RESEARCH_v0.1"

STATUS = "EXPERIMENTAL"
PRODUCTION_AUTHORIZED = False
PINE_IMPLEMENTATION_AUTHORIZED = False
LIVE_ALERT_IMPLEMENTATION_AUTHORIZED = False
PROSPECTIVE_ENROLLMENT = "NOT_AUTHORIZED"

A_PLUS_STATUS = "FROZEN_CONTROL"
A_EARLY_STATUS = "EXPERIMENTAL"

PULLBACK_DEFINITION = "PENDING_RESEARCH"
CT_PIVOT_DEFINITION = "RC1_PENDING_IMPORT_FROM_FROZEN_RESEARCH"
EXTERNAL_WIN_RATE_CLAIMS = "UNVERIFIED_EXTERNAL_CLAIM"

RESEARCH_ONLY = "RESEARCH_ONLY"

PIVOT_FIDELITY_STATUS = "MATERIAL_RESEARCH_FIDELITY_DEFECT"


@dataclass(frozen=True)
class ProtocolDependencies:
    """Blocking dependencies for enrollment. Each flips to True only when the
    authoritative definition is imported / the policy is resolved and approved."""
    ct_reference_definition_imported: bool = False
    structural_stop_rules_imported: bool = False
    fta_rules_imported: bool = False
    pullback_definition_resolved: bool = False
    pivot_fidelity_status_resolved_for_experiment: bool = False
    outcome_horizon_resolved: bool = False
    same_bar_stop_fta_policy_resolved: bool = False

    def missing(self) -> Tuple[str, ...]:
        return tuple(name.upper() for name, value in vars(self).items() if value is not True)


def protocol_ready_for_enrollment(deps: "ProtocolDependencies") -> bool:
    """Readiness only. Enrollment additionally requires explicit GPT/user authorisation."""
    return isinstance(deps, ProtocolDependencies) and not deps.missing()


CURRENT_DEPENDENCIES = ProtocolDependencies()
MISSING_AUTHORITATIVE_DEFINITIONS = bool(CURRENT_DEPENDENCIES.missing())
PROTOCOL_COMPLETE = not MISSING_AUTHORITATIVE_DEFINITIONS
PROTOCOL_READY_FOR_ENROLLMENT = protocol_ready_for_enrollment(CURRENT_DEPENDENCIES)


class LineageError(ValueError):
    """A downstream object violates the required stage ordering or parent eligibility."""


class PromotionError(RuntimeError):
    """Research output cannot be promoted to production by code."""


def promote_to_production(*_args, **_kwargs):
    raise PromotionError(
        "Research signals cannot be promoted automatically. Any production change "
        "requires explicit GPT/user approval under CONTROL/CHANGE_CONTROL.md."
    )


# --------------------------------------------------------------------- enums

class ThesisDirection(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class EventKind(str, Enum):
    REVERSAL = "REVERSAL"
    CONTINUATION = "CONTINUATION"


class BtcState(str, Enum):
    BTC_TREND = "BTC_TREND"
    BTC_NEUTRAL = "BTC_NEUTRAL"
    BTC_STRESS = "BTC_STRESS"
    BTC_HARD_VETO = "BTC_HARD_VETO"


class HtfAlignment(str, Enum):
    WITH_HTF = "WITH_HTF"
    COUNTER_HTF = "COUNTER_HTF"
    RANGE = "RANGE"
    TRANSITION = "TRANSITION"


class M2Validity(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    UNKNOWN = "UNKNOWN"


class ExternalOrInternal(str, Enum):
    EXTERNAL = "EXTERNAL"
    INTERNAL = "INTERNAL"


class LocationClass(str, Enum):
    MAJOR_EXTERNAL_4H = "MAJOR_EXTERNAL_4H"
    MAJOR_EXTERNAL_1H = "MAJOR_EXTERNAL_1H"
    ACTIVE_RANGE_BOUNDARY = "ACTIVE_RANGE_BOUNDARY"
    BROKEN_HTF_LEVEL_FIRST_RETEST = "BROKEN_HTF_LEVEL_FIRST_RETEST"
    INTERNAL_1H = "INTERNAL_1H"
    INTERNAL_15M = "INTERNAL_15M"
    OTHER_VALID_M2 = "OTHER_VALID_M2"


class PaRegime(str, Enum):
    CLEAN_DIRECTIONAL = "CLEAN_DIRECTIONAL"
    WICKY_DIRECTIONAL = "WICKY_DIRECTIONAL"
    TWO_SIDED_VOLATILITY = "TWO_SIDED_VOLATILITY"
    CHOP = "CHOP"
    TRANSITION = "TRANSITION"
    UNKNOWN = "UNKNOWN"


class PivotType(str, Enum):
    HIGH = "HIGH"
    LOW = "LOW"


class Attribution(str, Enum):
    SAME_EVENT = "SAME_EVENT"
    AMBIGUOUS = "AMBIGUOUS"


class StopSource(str, Enum):
    ORIGINAL_LIQUIDITY_EXCURSION = "ORIGINAL_LIQUIDITY_EXCURSION"
    THESIS_INVALIDATING_EXTREME = "THESIS_INVALIDATING_EXTREME"
    ACCEPTED_STRUCTURAL_BOUNDARY = "ACCEPTED_STRUCTURAL_BOUNDARY"
    FROZEN_A_PLUS_RULE = "FROZEN_A_PLUS_RULE"


class FtaLevel(str, Enum):
    # Hierarchy order: 4H, then 1H, then external 15m.
    FTA_4H = "FTA_4H"
    FTA_1H = "FTA_1H"
    FTA_15M_EXTERNAL = "FTA_15M_EXTERNAL"


class Branch(str, Enum):
    DIRECT_CONTROL_BREAK = "DIRECT_CONTROL_BREAK"
    PULLBACK_REBREAK = "PULLBACK_REBREAK"
    FROZEN_A_PLUS = "FROZEN_A_PLUS"


class FirstTouch(str, Enum):
    FTA_FIRST = "FTA_FIRST"
    STOP_FIRST = "STOP_FIRST"
    NEITHER = "NEITHER"
    RIGHT_CENSORED = "RIGHT_CENSORED"


class Geometry(str, Enum):
    VALID = "VALID"
    INVALID_GEOMETRY = "INVALID_GEOMETRY"
    INCOMPLETE = "INCOMPLETE"


LTF_TIMEFRAMES = ("1m", "3m")
_R_DERIVED_STOP_SOURCES = {"DESIRED_R", "FIXED_R", "R_MULTIPLE", "TARGET_RR", "FIXED_1_5R"}


# ------------------------------------------------------------------- helpers

def _ts(value, name) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise ValueError(f"{name} must be a timezone-aware timestamp")
    return value


def _set(obj, name, value):
    object.__setattr__(obj, name, value)


def _favourable(direction: ThesisDirection, a: float, b: float) -> float:
    """Signed distance from a to b in the thesis direction."""
    return (b - a) if direction is ThesisDirection.LONG else (a - b)


# -------------------------------------------------------------- parent event

@dataclass(frozen=True)
class ParentEvent:
    research_case_id: str
    symbol: str
    case_era: CaseEra
    data_provenance: str
    event_kind: EventKind
    event_direction: EventDirection
    thesis_direction: ThesisDirection
    btc_state: BtcState
    htf_alignment: HtfAlignment
    m2_validity: M2Validity
    m2_type: str
    m2_timeframe: str
    external_or_internal: ExternalOrInternal
    location_class: LocationClass
    location_classified_at: datetime
    tested_structural_level: float
    sweep_extreme: float
    event_timestamp: datetime
    live_event_seq: Optional[int] = None
    initial_resolution_timestamp: Optional[datetime] = None
    asset_4h_context: Optional[str] = None
    asset_1h_context: Optional[str] = None
    first_retest: Optional[bool] = None
    prior_reaction_count: Optional[int] = None
    active_range_position: Optional[float] = None
    pa_regime: PaRegime = PaRegime.UNKNOWN
    protocol_version: str = PROTOCOL_VERSION

    def __post_init__(self):
        for name in ("research_case_id", "symbol", "data_provenance", "m2_type", "m2_timeframe"):
            if not getattr(self, name) or not str(getattr(self, name)).strip():
                raise ValueError(f"{name.upper()} is required")
        for name, cls in (
            ("case_era", CaseEra), ("event_kind", EventKind), ("event_direction", EventDirection),
            ("thesis_direction", ThesisDirection), ("btc_state", BtcState),
            ("htf_alignment", HtfAlignment), ("m2_validity", M2Validity),
            ("external_or_internal", ExternalOrInternal), ("location_class", LocationClass),
            ("pa_regime", PaRegime),
        ):
            _set(self, name, cls(getattr(self, name)))
        for name in ("location_classified_at", "event_timestamp", "initial_resolution_timestamp"):
            _set(self, name, _ts(getattr(self, name), name.upper()))

        if self.case_era is CaseEra.PRE_EVENTSEQ_LEGACY and self.live_event_seq is not None:
            raise IdentityError(f"{self.research_case_id}: PRE_EVENTSEQ_LEGACY case cannot carry LIVE_EVENT_SEQ")

        # TESTED_STRUCTURAL_LEVEL and SWEEP_EXTREME are independent observations.
        if self.tested_structural_level is None or self.sweep_extreme is None:
            raise ValueError("TESTED_STRUCTURAL_LEVEL and SWEEP_EXTREME are both required")
        if self.event_direction is EventDirection.SELL_SIDE and self.sweep_extreme > self.tested_structural_level:
            raise ValueError("SELL_SIDE sweep extreme must be at or below the tested level")
        if self.event_direction is EventDirection.BUY_SIDE and self.sweep_extreme < self.tested_structural_level:
            raise ValueError("BUY_SIDE sweep extreme must be at or above the tested level")

        if self.event_kind is EventKind.REVERSAL:
            expected = ThesisDirection.LONG if self.event_direction is EventDirection.SELL_SIDE else ThesisDirection.SHORT
            if self.thesis_direction is not expected:
                raise ValueError(f"REVERSAL of {self.event_direction.value} liquidity implies {expected.value} thesis")

        if self.initial_resolution_timestamp is not None and self.initial_resolution_timestamp < self.event_timestamp:
            raise ValueError("INITIAL_RESOLUTION cannot precede EVENT")

    def eligibility_failures(self) -> Tuple[str, ...]:
        failures = []
        if self.btc_state is BtcState.BTC_HARD_VETO:
            failures.append("BTC_HARD_VETO")
        if not self.asset_4h_context or not self.asset_1h_context:
            failures.append("ASSET_4H_1H_CONTEXT_NOT_CAPTURED")
        if self.m2_validity is not M2Validity.VALID:
            failures.append("M2_LOCATION_NOT_VALID")
        if self.initial_resolution_timestamp is None:
            failures.append("ACCEPTANCE_REJECTION_NOT_CONFIRMED")
        return tuple(failures)

    @property
    def is_eligible(self) -> bool:
        return not self.eligibility_failures()

    @property
    def stratum(self) -> Tuple[str, str, str, str]:
        """Stratification key. Results must not be pooled across strata blindly."""
        return (self.htf_alignment.value, self.btc_state.value,
                self.location_class.value, self.pa_regime.value)


# ------------------------------------------------------------ lineage stages

@dataclass(frozen=True)
class StageObservation:
    """Generic downstream stage: WATCH, FVG, A_PLUS_SIGNAL."""
    event_seq: Optional[int]
    timestamp: datetime
    price: Optional[float] = None

    def __post_init__(self):
        _set(self, "timestamp", _ts(self.timestamp, "timestamp"))


@dataclass(frozen=True)
class CtReference:
    """Most recently confirmed opposing 15m structural pivot within EVENT_START → INITIAL_RESOLUTION,
    frozen at INITIAL_RESOLUTION. Pivot definition: RC1 (pending import)."""
    price: float
    pivot_type: PivotType
    pivot_timestamp: datetime
    confirmation_timestamp: datetime
    pivot_definition: str = CT_PIVOT_DEFINITION
    timeframe: str = "15m"

    def __post_init__(self):
        _set(self, "pivot_type", PivotType(self.pivot_type))
        _set(self, "pivot_timestamp", _ts(self.pivot_timestamp, "CT_REFERENCE_TIMESTAMP"))
        _set(self, "confirmation_timestamp", _ts(self.confirmation_timestamp, "CT_CONFIRMATION_TIMESTAMP"))
        if self.timeframe != "15m":
            raise ValueError("CT_REFERENCE must be a 15m pivot")
        if self.confirmation_timestamp < self.pivot_timestamp:
            raise ValueError("CT pivot cannot be confirmed before it forms")


@dataclass(frozen=True)
class ControlBreak:
    """DIRECT_CONTROL_BREAK: first confirmed 15m close through CT_REFERENCE in thesis direction."""
    event_seq: Optional[int]
    close_timestamp: datetime
    close_price: float
    confirmed_by: str = "CLOSE_15M"
    body_atr: Optional[float] = None
    range_atr: Optional[float] = None
    close_location: Optional[float] = None
    timeframe: str = "15m"

    def __post_init__(self):
        _set(self, "close_timestamp", _ts(self.close_timestamp, "CT_BREAK_TIMESTAMP"))
        if self.confirmed_by != "CLOSE_15M":
            raise ValueError("Control break must be confirmed by a 15m close; intrabar wick alone is not confirmation")
        if self.timeframe != "15m":
            raise ValueError("Control break is measured on 15m only")

    @property
    def timestamp(self) -> datetime:
        return self.close_timestamp


@dataclass(frozen=True)
class Pullback:
    """Lower-timeframe pullback after the control break. Raw measurements only;
    PULLBACK_DEFINITION = PENDING_RESEARCH, so no pullback 'qualifies' yet."""
    event_seq: Optional[int]
    timeframe: str
    start_timestamp: datetime
    end_timestamp: Optional[datetime] = None
    depth_pct: Optional[float] = None
    depth_atr: Optional[float] = None
    bars: Optional[int] = None
    closed_back_through_ct: Optional[bool] = None
    adverse_excursion: Optional[float] = None
    wick_body_notes: Optional[str] = None
    vwap_relation: Optional[str] = None
    micro_swing: Optional[str] = None

    def __post_init__(self):
        if self.timeframe not in LTF_TIMEFRAMES:
            raise ValueError("Pullback is observed on 1m/3m only")
        _set(self, "start_timestamp", _ts(self.start_timestamp, "PULLBACK_START"))
        _set(self, "end_timestamp", _ts(self.end_timestamp, "PULLBACK_END"))
        if self.end_timestamp is not None and self.end_timestamp < self.start_timestamp:
            raise ValueError("Pullback cannot end before it starts")

    @property
    def timestamp(self) -> datetime:
        return self.start_timestamp

    @property
    def definition(self) -> str:
        return PULLBACK_DEFINITION


@dataclass(frozen=True)
class Rebreak:
    event_seq: Optional[int]
    timeframe: str
    timestamp: datetime
    price: float

    def __post_init__(self):
        if self.timeframe not in LTF_TIMEFRAMES:
            raise ValueError("Rebreak is observed on 1m/3m only")
        _set(self, "timestamp", _ts(self.timestamp, "REBREAK_TIMESTAMP"))


# ---------------------------------------------------------- stop, FTA, branch

@dataclass(frozen=True)
class StructuralStop:
    """Thesis invalidation → structural stop. Never desired R → stop."""
    price: float
    source: StopSource

    def __post_init__(self):
        if str(getattr(self.source, "value", self.source)).upper() in _R_DERIVED_STOP_SOURCES:
            raise ValueError("Structural stop cannot be derived from desired R")
        _set(self, "source", StopSource(self.source))


@dataclass(frozen=True)
class FtaSelection:
    """First trouble area, selected (and frozen) before entry / R calculation."""
    price: float
    level: FtaLevel
    selected_at: datetime

    def __post_init__(self):
        _set(self, "level", FtaLevel(self.level))
        _set(self, "selected_at", _ts(self.selected_at, "FTA_SELECTED_AT"))


def compute_r_to_fta(direction, entry: float, stop: StructuralStop, fta: FtaSelection) -> Optional[float]:
    """R is derived from (structural stop, frozen FTA). Returns None for invalid geometry."""
    if not isinstance(stop, StructuralStop) or not isinstance(fta, FtaSelection):
        raise TypeError("R requires a StructuralStop and a frozen FtaSelection")
    direction = ThesisDirection(direction)
    risk = _favourable(direction, stop.price, entry)
    reward = _favourable(direction, entry, fta.price)
    if risk <= 0 or reward <= 0:
        return None
    return reward / risk


@dataclass(frozen=True)
class BranchResult:
    branch: Branch
    direction: ThesisDirection
    signal: bool
    trade_eligible: bool = False
    entry_timestamp: Optional[datetime] = None
    entry_price: Optional[float] = None
    structural_stop: Optional[StructuralStop] = None
    fta: Optional[FtaSelection] = None
    atr_15m: Optional[float] = None
    first_touch: Optional[FirstTouch] = None
    mfe: Optional[float] = None
    mae: Optional[float] = None
    outcome_resolved_at: Optional[datetime] = None

    def __post_init__(self):
        _set(self, "branch", Branch(self.branch))
        _set(self, "direction", ThesisDirection(self.direction))
        _set(self, "entry_timestamp", _ts(self.entry_timestamp, "ENTRY_TIMESTAMP"))
        _set(self, "outcome_resolved_at", _ts(self.outcome_resolved_at, "OUTCOME_RESOLVED_AT"))
        if self.first_touch is not None:
            _set(self, "first_touch", FirstTouch(self.first_touch))

        if not self.signal:
            if self.trade_eligible or self.entry_price is not None or self.entry_timestamp is not None \
                    or self.first_touch is not None:
                raise ValueError(f"{self.branch.value}: no signal → no entry, eligibility or outcome")
            return
        if self.entry_price is None or self.entry_timestamp is None:
            raise ValueError(f"{self.branch.value}: signal requires ENTRY_PRICE and ENTRY_TIMESTAMP")
        if self.fta is not None and self.fta.selected_at > self.entry_timestamp:
            raise ValueError(f"{self.branch.value}: FTA must be selected before entry (FTA before R)")
        if self.trade_eligible and self.geometry is not Geometry.VALID:
            raise ValueError(f"{self.branch.value}: trade cannot be eligible with {self.geometry.value}")
        for name in ("mfe", "mae"):
            if getattr(self, name) is not None and getattr(self, name) < 0:
                raise ValueError(f"{name.upper()} is a non-negative excursion")
        if self.outcome_resolved_at is not None and self.outcome_resolved_at < self.entry_timestamp:
            raise ValueError("Outcome cannot resolve before entry")

    @property
    def geometry(self) -> Geometry:
        if self.entry_price is None or self.structural_stop is None or self.fta is None:
            return Geometry.INCOMPLETE
        if compute_r_to_fta(self.direction, self.entry_price, self.structural_stop, self.fta) is None:
            return Geometry.INVALID_GEOMETRY
        return Geometry.VALID

    @property
    def r_to_fta(self) -> Optional[float]:
        if self.geometry is not Geometry.VALID:
            return None
        return compute_r_to_fta(self.direction, self.entry_price, self.structural_stop, self.fta)

    @property
    def stop_distance(self) -> Optional[float]:
        if self.entry_price is None or self.structural_stop is None:
            return None
        return abs(self.entry_price - self.structural_stop.price)

    @property
    def stop_distance_atr(self) -> Optional[float]:
        if self.stop_distance is None or not self.atr_15m:
            return None
        return self.stop_distance / self.atr_15m

    def _in_r(self, value):
        if value is None or self.geometry is not Geometry.VALID:
            return None
        return value / self.stop_distance

    @property
    def mfe_r(self):
        return self._in_r(self.mfe)

    @property
    def mae_r(self):
        return self._in_r(self.mae)

    @property
    def realized_r(self) -> Optional[float]:
        """Gross, before fees/slippage. Defined only for a resolved first touch."""
        if self.geometry is not Geometry.VALID:
            return None
        if self.first_touch is FirstTouch.FTA_FIRST:
            return self.r_to_fta
        if self.first_touch is FirstTouch.STOP_FIRST:
            return -1.0
        return None


# ------------------------------------------------------------ case container

_STAGES = ("watch", "control_break", "pullback", "rebreak", "fvg", "a_plus_signal")


@dataclass(frozen=True)
class EarlyRebreakCase:
    """One parent event and the three branches measured against it."""
    parent: ParentEvent
    ct_reference: Optional[CtReference] = None
    control_break: Optional[ControlBreak] = None
    pullback: Optional[Pullback] = None
    rebreak: Optional[Rebreak] = None
    watch: Optional[StageObservation] = None
    fvg: Optional[StageObservation] = None
    a_plus_signal: Optional[StageObservation] = None
    thesis_stop: Optional[StructuralStop] = None
    direct_branch: Optional[BranchResult] = None
    rebreak_branch: Optional[BranchResult] = None
    a_plus_branch: Optional[BranchResult] = None

    promotion_status = RESEARCH_ONLY

    def __post_init__(self):
        p = self.parent
        downstream = [getattr(self, n) for n in _STAGES + ("ct_reference", "direct_branch", "rebreak_branch", "a_plus_branch")]
        if any(x is not None for x in downstream) and not p.is_eligible:
            raise LineageError(f"{p.research_case_id}: downstream objects require an eligible parent "
                               f"({', '.join(p.eligibility_failures())})")
        self._check_identity()
        self._check_ct()
        self._check_sequence()
        self._check_thesis_stop()
        self._check_branches()

    # --- identity
    def _check_identity(self):
        p = self.parent
        for name in _STAGES:
            stage = getattr(self, name)
            if stage is None:
                continue
            if stage.timestamp < p.event_timestamp:
                raise IdentityError(f"{p.research_case_id}: {name.upper()} predates the parent event")
            if stage.event_seq is not None and stage.event_seq != p.live_event_seq:
                raise IdentityError(
                    f"{p.research_case_id}: {name.upper()}_EVENT_SEQ={stage.event_seq} belongs to a different "
                    f"event than parent LIVE_EVENT_SEQ={p.live_event_seq}"
                )

    def attribution(self, stage_name: str) -> Optional[Attribution]:
        stage = getattr(self, stage_name)
        if stage is None:
            return None
        if self.parent.live_event_seq is not None and stage.event_seq == self.parent.live_event_seq:
            return Attribution.SAME_EVENT
        return Attribution.AMBIGUOUS

    @property
    def attributions(self) -> Dict[str, Optional[Attribution]]:
        return {name: self.attribution(name) for name in _STAGES}

    # --- CT reference and break
    def _check_ct(self):
        p, ct = self.parent, self.ct_reference
        if ct is None:
            return
        if not (p.event_timestamp <= ct.pivot_timestamp <= p.initial_resolution_timestamp):
            raise LineageError("CT_REFERENCE pivot must lie within EVENT_START → INITIAL_RESOLUTION")
        if ct.confirmation_timestamp > p.initial_resolution_timestamp:
            raise LineageError("CT_REFERENCE must be confirmed by INITIAL_RESOLUTION (frozen at resolution)")
        opposing = PivotType.HIGH if p.thesis_direction is ThesisDirection.LONG else PivotType.LOW
        if ct.pivot_type is not opposing:
            raise LineageError(f"{p.thesis_direction.value} thesis requires an opposing {opposing.value} pivot")

    def _check_sequence(self):
        p, cb, pb, rb = self.parent, self.control_break, self.pullback, self.rebreak
        if cb is not None:
            if self.ct_reference is None:
                raise LineageError("CONTROL_BREAK requires a frozen CT_REFERENCE")
            if cb.close_timestamp <= p.initial_resolution_timestamp:
                raise LineageError("CONTROL_BREAK must close after INITIAL_RESOLUTION")
            if _favourable(p.thesis_direction, self.ct_reference.price, cb.close_price) <= 0:
                raise LineageError("CONTROL_BREAK close must be through CT_REFERENCE in thesis direction")
        if pb is not None:
            if cb is None:
                raise LineageError("PULLBACK requires a prior CONTROL_BREAK")
            if pb.start_timestamp < cb.close_timestamp:
                raise LineageError("PULLBACK cannot start before CONTROL_BREAK")
        if rb is not None:
            if cb is None:
                raise LineageError("REBREAK requires a prior CONTROL_BREAK")
            if pb is None:
                raise LineageError("REBREAK requires a PULLBACK after the CONTROL_BREAK")
            if rb.timestamp <= cb.close_timestamp:
                raise LineageError("REBREAK cannot occur at or before CONTROL_BREAK")
            if rb.timestamp < (pb.end_timestamp or pb.start_timestamp):
                raise LineageError("REBREAK cannot occur before the PULLBACK")

    # --- stops
    def _check_thesis_stop(self):
        p, s = self.parent, self.thesis_stop
        if s is None:
            return
        allowed = {
            EventKind.REVERSAL: {StopSource.ORIGINAL_LIQUIDITY_EXCURSION, StopSource.THESIS_INVALIDATING_EXTREME},
            EventKind.CONTINUATION: {StopSource.ACCEPTED_STRUCTURAL_BOUNDARY, StopSource.THESIS_INVALIDATING_EXTREME},
        }[p.event_kind]
        if s.source not in allowed:
            raise ValueError(f"{p.event_kind.value} thesis stop source must be one of {sorted(a.value for a in allowed)}")
        if s.source is StopSource.ORIGINAL_LIQUIDITY_EXCURSION and _favourable(p.thesis_direction, s.price, p.sweep_extreme) < 0:
            raise ValueError("Reversal stop must sit at or beyond the original SWEEP_EXTREME")

    # --- branches
    def _check_branches(self):
        p = self.parent
        slots = (
            ("direct_branch", Branch.DIRECT_CONTROL_BREAK, self.control_break),
            ("rebreak_branch", Branch.PULLBACK_REBREAK, self.rebreak),
            ("a_plus_branch", Branch.FROZEN_A_PLUS, self.a_plus_signal),
        )
        for slot, expected, trigger in slots:
            b = getattr(self, slot)
            if b is None:
                continue
            if b.branch is not expected:
                raise ValueError(f"{slot} must hold {expected.value}")
            if b.direction is not p.thesis_direction:
                raise ValueError(f"{expected.value}: direction must match parent thesis")
            if b.signal:
                if trigger is None:
                    raise LineageError(f"{expected.value}: signal requires its trigger stage")
                if b.entry_timestamp < trigger.timestamp:
                    raise LineageError(f"{expected.value}: entry cannot precede its trigger")
                if b.entry_timestamp < p.location_classified_at:
                    raise LineageError("Location must be classified before any entry/outcome")
            if b.outcome_resolved_at is not None and b.outcome_resolved_at < p.location_classified_at:
                raise LineageError("Location must be classified before the outcome is known")
            if b.structural_stop is not None:
                if expected is Branch.FROZEN_A_PLUS:
                    continue  # A+ stop is recorded exactly as the frozen A+ rule produces it.
                if b.structural_stop.source is StopSource.FROZEN_A_PLUS_RULE:
                    raise ValueError(f"{expected.value}: FROZEN_A_PLUS_RULE stop is reserved for the A+ branch")
                if self.thesis_stop is None or b.structural_stop != self.thesis_stop:
                    raise ValueError(f"{expected.value}: stop must be the parent's thesis-derived structural stop "
                                     f"(an early entry does not justify a tighter stop)")

    # --- comparison metrics
    @staticmethod
    def _gap(a, b) -> Optional[timedelta]:
        if a is None or b is None:
            return None
        return b - a

    @property
    def latencies(self) -> Dict[str, Optional[timedelta]]:
        p = self.parent
        cb = self.control_break.close_timestamp if self.control_break else None
        rb = self.rebreak.timestamp if self.rebreak else None
        ap = self.a_plus_signal.timestamp if self.a_plus_signal else None
        return {
            "EVENT_TO_RESOLUTION": self._gap(p.event_timestamp, p.initial_resolution_timestamp),
            "RESOLUTION_TO_CT_BREAK": self._gap(p.initial_resolution_timestamp, cb),
            "CT_BREAK_TO_REBREAK": self._gap(cb, rb),
            "CT_BREAK_TO_A_PLUS": self._gap(cb, ap),
            "REBREAK_TO_A_PLUS": self._gap(rb, ap),
        }

    @property
    def prices(self) -> Dict[str, Optional[float]]:
        return {
            "PRICE_AT_CT_BREAK": self.control_break.close_price if self.control_break else None,
            "PRICE_AT_REBREAK": self.rebreak.price if self.rebreak else None,
            "PRICE_AT_A_PLUS": self.a_plus_signal.price if self.a_plus_signal else None,
        }

    def move_consumed(self, branch: BranchResult) -> Optional[float]:
        """Thesis-direction distance travelled from SWEEP_EXTREME to the branch entry."""
        if branch is None or branch.entry_price is None:
            return None
        return _favourable(self.parent.thesis_direction, self.parent.sweep_extreme, branch.entry_price)

    @property
    def move_consumed_before_entry(self) -> Dict[str, Optional[float]]:
        return {
            "MOVE_CONSUMED_BEFORE_DIRECT_ENTRY": self.move_consumed(self.direct_branch),
            "MOVE_CONSUMED_BEFORE_REBREAK": self.move_consumed(self.rebreak_branch),
            "MOVE_CONSUMED_BEFORE_A_PLUS": self.move_consumed(self.a_plus_branch),
        }
