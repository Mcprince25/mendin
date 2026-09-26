"""Tests for the EARLY_REBREAK_RESEARCH_v0.1 RESEARCH DATA MODEL.

Research-only. These are NOT Pine regression tests and contain no real market data:
all prices/timestamps below are synthetic fixtures.
"""

import dataclasses
import hashlib
from pathlib import Path

import pytest

import rebreak_model as rm
from rebreak_model import (
    Attribution, Branch, BranchResult, BtcState, CtReference, ControlBreak, EarlyRebreakCase,
    FirstTouch, FtaSelection, Geometry, LineageError, M2Validity, ParentEvent, PromotionError,
    Pullback, Rebreak, StageObservation, StructuralStop, compute_r_to_fta,
)
from research_model import CaseEra, IdentityError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SEQ = 7
FIXTURE = "synthetic unit-test fixture (not market data)"


def T(hhmm):
    return f"2026-01-01T{hhmm}:00+00:00"


def parent(**kw):
    base = dict(
        research_case_id="TEST-RB-001", symbol="BINANCE:TESTUSDT.P", case_era=CaseEra.PROSPECTIVE,
        data_provenance=FIXTURE, event_kind="REVERSAL", event_direction="SELL_SIDE",
        thesis_direction="LONG", btc_state="BTC_NEUTRAL", htf_alignment="COUNTER_HTF",
        m2_validity="VALID", m2_type="EXTERNAL_SWING_LOW", m2_timeframe="1H",
        external_or_internal="EXTERNAL", location_class="MAJOR_EXTERNAL_1H",
        location_classified_at=T("00:30"), tested_structural_level=100.0, sweep_extreme=98.0,
        event_timestamp=T("00:00"), live_event_seq=SEQ, initial_resolution_timestamp=T("00:30"),
        asset_4h_context="4H_DOWNTREND", asset_1h_context="1H_RANGE",
    )
    base.update(kw)
    return ParentEvent(**base)


THESIS_STOP = StructuralStop(97.5, "ORIGINAL_LIQUIDITY_EXCURSION")
FTA = FtaSelection(105.0, "FTA_1H", T("00:30"))


def branch(which, entry_ts, entry, stop=THESIS_STOP, **kw):
    base = dict(branch=which, direction="LONG", signal=True, trade_eligible=True,
                entry_timestamp=entry_ts, entry_price=entry, structural_stop=stop, fta=FTA)
    base.update(kw)
    return BranchResult(**base)


def full_case(**kw):
    base = dict(
        parent=parent(),
        ct_reference=CtReference(101.0, "HIGH", T("00:15"), T("00:30")),
        control_break=ControlBreak(SEQ, T("00:45"), 101.5, body_atr=0.8, range_atr=1.1, close_location=0.9),
        pullback=Pullback(SEQ, "3m", T("00:48"), T("00:57"), depth_pct=0.3),
        rebreak=Rebreak(SEQ, "3m", T("01:00"), 101.6),
        watch=StageObservation(SEQ, T("00:35")),
        fvg=StageObservation(SEQ, T("01:15")),
        a_plus_signal=StageObservation(SEQ, T("01:30"), 102.2),
        thesis_stop=THESIS_STOP,
        direct_branch=branch("DIRECT_CONTROL_BREAK", T("00:45"), 101.5),
        rebreak_branch=branch("PULLBACK_REBREAK", T("01:00"), 101.6),
        a_plus_branch=branch("FROZEN_A_PLUS", T("01:30"), 102.2,
                             stop=StructuralStop(97.5, "FROZEN_A_PLUS_RULE")),
    )
    base.update(kw)
    return EarlyRebreakCase(**base)


def test_full_valid_case_constructs():
    c = full_case()
    assert all(v is Attribution.SAME_EVENT for v in c.attributions.values())


# 1. Rebreak cannot exist without a valid parent event
@pytest.mark.parametrize("override, reason", [
    (dict(btc_state="BTC_HARD_VETO"), "BTC_HARD_VETO"),
    (dict(asset_1h_context=None), "ASSET_4H_1H_CONTEXT_NOT_CAPTURED"),
    (dict(m2_validity="INVALID"), "M2_LOCATION_NOT_VALID"),
    (dict(m2_validity="UNKNOWN"), "M2_LOCATION_NOT_VALID"),
    (dict(initial_resolution_timestamp=None), "ACCEPTANCE_REJECTION_NOT_CONFIRMED"),
])
def test_rebreak_requires_eligible_parent(override, reason):
    p = parent(**override)
    assert reason in p.eligibility_failures()
    with pytest.raises(LineageError):
        EarlyRebreakCase(parent=p, rebreak=Rebreak(SEQ, "3m", T("01:00"), 101.6))


def test_ineligible_parent_is_still_recordable_without_downstream():
    # Rejected events are kept (not discarded), just never given branches.
    c = EarlyRebreakCase(parent=parent(m2_validity="INVALID"))
    assert not c.parent.is_eligible


# 2. Rebreak cannot exist before CT break
def test_rebreak_requires_control_break():
    with pytest.raises(LineageError):
        full_case(control_break=None, pullback=None, direct_branch=None)


def test_rebreak_requires_pullback():
    with pytest.raises(LineageError):
        full_case(pullback=None)


def test_rebreak_cannot_precede_control_break():
    with pytest.raises(LineageError):
        full_case(rebreak=Rebreak(SEQ, "3m", T("00:40"), 101.6), rebreak_branch=None)


def test_rebreak_cannot_precede_pullback():
    with pytest.raises(LineageError):
        full_case(rebreak=Rebreak(SEQ, "3m", T("00:50"), 101.6),
                  rebreak_branch=branch("PULLBACK_REBREAK", T("00:50"), 101.6))


def test_control_break_requires_15m_close_not_wick():
    with pytest.raises(ValueError):
        ControlBreak(SEQ, T("00:45"), 101.5, confirmed_by="WICK")


def test_control_break_close_must_be_through_ct_reference():
    with pytest.raises(LineageError):
        full_case(control_break=ControlBreak(SEQ, T("00:45"), 100.9))


def test_ct_reference_must_be_frozen_at_resolution_and_opposing():
    with pytest.raises(LineageError):  # confirmed after resolution
        full_case(ct_reference=CtReference(101.0, "HIGH", T("00:15"), T("00:45")))
    with pytest.raises(LineageError):  # pivot before event start
        full_case(ct_reference=CtReference(101.0, "HIGH", "2025-12-31T23:45:00+00:00", T("00:30")))
    with pytest.raises(LineageError):  # LONG thesis needs opposing HIGH pivot
        full_case(ct_reference=CtReference(101.0, "LOW", T("00:15"), T("00:30")))


def test_lower_timeframes_only_for_pullback_and_rebreak():
    with pytest.raises(ValueError):
        Pullback(SEQ, "15m", T("00:48"))
    with pytest.raises(ValueError):
        Rebreak(SEQ, "5m", T("01:00"), 101.6)


def test_pullback_definition_is_pending():
    assert rm.PULLBACK_DEFINITION == "PENDING_RESEARCH"
    assert full_case().pullback.definition == "PENDING_RESEARCH"


# 3. Rebreak eventSeq must match parent LIVE_EVENT_SEQ for SAME_EVENT
def test_rebreak_same_event_requires_matching_seq():
    assert full_case().attribution("rebreak") is Attribution.SAME_EVENT
    c = full_case(rebreak=Rebreak(None, "3m", T("01:00"), 101.6))
    assert c.attribution("rebreak") is Attribution.AMBIGUOUS


def test_parent_without_seq_makes_everything_ambiguous():
    c = full_case(
        parent=parent(live_event_seq=None),
        control_break=ControlBreak(None, T("00:45"), 101.5),
        pullback=Pullback(None, "3m", T("00:48"), T("00:57")),
        rebreak=Rebreak(None, "3m", T("01:00"), 101.6),
        watch=StageObservation(None, T("00:35")), fvg=StageObservation(None, T("01:15")),
        a_plus_signal=StageObservation(None, T("01:30"), 102.2),
    )
    assert all(v is Attribution.AMBIGUOUS for v in c.attributions.values())


# 4. FVG eventSeq must match parent LIVE_EVENT_SEQ for SAME_EVENT
def test_fvg_same_event_requires_matching_seq():
    assert full_case().attribution("fvg") is Attribution.SAME_EVENT
    assert full_case(fvg=StageObservation(None, T("01:15"))).attribution("fvg") is Attribution.AMBIGUOUS


def test_temporal_proximity_alone_never_gives_same_event():
    # FVG one minute after the rebreak, but without eventSeq evidence → AMBIGUOUS.
    c = full_case(fvg=StageObservation(None, T("01:01")))
    assert c.attribution("fvg") is Attribution.AMBIGUOUS


# 5. A later event cannot inherit an older event's WATCH/CT/FVG/rebreak
OLD_SEQ = SEQ - 1


@pytest.mark.parametrize("field, stage", [
    ("watch", StageObservation(OLD_SEQ, T("00:35"))),
    ("control_break", ControlBreak(OLD_SEQ, T("00:45"), 101.5)),
    ("pullback", Pullback(OLD_SEQ, "3m", T("00:48"), T("00:57"))),
    ("rebreak", Rebreak(OLD_SEQ, "3m", T("01:00"), 101.6)),
    ("fvg", StageObservation(OLD_SEQ, T("01:15"))),
    ("a_plus_signal", StageObservation(OLD_SEQ, T("01:30"), 102.2)),
])
def test_stage_from_other_event_is_rejected(field, stage):
    with pytest.raises(IdentityError):
        full_case(**{field: stage})


@pytest.mark.parametrize("field, stage", [
    ("watch", StageObservation(None, "2025-12-31T23:50:00+00:00")),
    ("fvg", StageObservation(None, "2025-12-31T23:55:00+00:00")),
])
def test_stage_predating_parent_event_is_rejected(field, stage):
    with pytest.raises(IdentityError):
        full_case(**{field: stage})


def test_stage_seq_cannot_attach_to_parent_without_seq():
    with pytest.raises(IdentityError):
        EarlyRebreakCase(parent=parent(live_event_seq=None), watch=StageObservation(SEQ, T("00:35")))


# 6. TESTED_STRUCTURAL_LEVEL and SWEEP_EXTREME remain separate
def test_tested_level_and_sweep_extreme_are_separate():
    p = parent()
    assert p.tested_structural_level == 100.0 and p.sweep_extreme == 98.0
    q = dataclasses.replace(p, sweep_extreme=97.0)
    assert q.tested_structural_level == 100.0
    with pytest.raises(ValueError):
        parent(sweep_extreme=None)
    with pytest.raises(ValueError):
        parent(tested_structural_level=None)


def test_sweep_extreme_must_be_beyond_tested_level():
    with pytest.raises(ValueError):
        parent(sweep_extreme=100.5)  # SELL_SIDE sweep above the tested level


# 7. Structural stop cannot be derived from desired R
@pytest.mark.parametrize("source", ["DESIRED_R", "FIXED_R", "R_MULTIPLE", "TARGET_RR", "FIXED_1_5R"])
def test_stop_cannot_come_from_desired_r(source):
    with pytest.raises(ValueError):
        StructuralStop(99.0, source)


def test_early_branch_cannot_use_tighter_stop_than_thesis():
    tight = StructuralStop(100.8, "THESIS_INVALIDATING_EXTREME")
    with pytest.raises(ValueError):
        full_case(rebreak_branch=branch("PULLBACK_REBREAK", T("01:00"), 101.6, stop=tight))


def test_reversal_stop_must_sit_beyond_sweep_extreme():
    with pytest.raises(ValueError):
        full_case(thesis_stop=StructuralStop(98.5, "ORIGINAL_LIQUIDITY_EXCURSION"),
                  direct_branch=None, rebreak_branch=None)


def test_a_plus_rule_stop_reserved_for_a_plus_branch():
    with pytest.raises(ValueError):
        full_case(direct_branch=branch("DIRECT_CONTROL_BREAK", T("00:45"), 101.5,
                                       stop=StructuralStop(97.5, "FROZEN_A_PLUS_RULE")))


@pytest.mark.parametrize("stop", [102.0, 101.5])
def test_long_stop_not_below_entry_is_invalid_geometry(stop):
    b = branch("DIRECT_CONTROL_BREAK", T("00:45"), 101.5,
               stop=StructuralStop(stop, "THESIS_INVALIDATING_EXTREME"), trade_eligible=False)
    assert b.geometry is Geometry.INVALID_GEOMETRY
    assert b.r_to_fta is None
    with pytest.raises(ValueError):
        dataclasses.replace(b, trade_eligible=True)


def test_short_geometry():
    b = BranchResult("DIRECT_CONTROL_BREAK", "SHORT", True, True, T("00:45"), 100.0,
                     StructuralStop(102.0, "ORIGINAL_LIQUIDITY_EXCURSION"), FtaSelection(96.0, "FTA_4H", T("00:30")))
    assert b.geometry is Geometry.VALID and b.r_to_fta == pytest.approx(2.0)


# 8. FTA is frozen before R calculation
def test_fta_selected_after_entry_is_rejected():
    late = FtaSelection(105.0, "FTA_1H", T("00:50"))
    with pytest.raises(ValueError):
        branch("DIRECT_CONTROL_BREAK", T("00:45"), 101.5, fta=late)


def test_fta_is_immutable():
    with pytest.raises(dataclasses.FrozenInstanceError):
        FTA.price = 110.0


def test_r_requires_frozen_fta_object_not_raw_number():
    with pytest.raises(TypeError):
        compute_r_to_fta("LONG", 101.5, THESIS_STOP, 105.0)


def test_r_to_fta_derived_from_stop_and_fta():
    b = full_case().direct_branch
    assert b.r_to_fta == pytest.approx((105.0 - 101.5) / (101.5 - 97.5))


# 9. Legacy PRE_EVENTSEQ cases cannot be assigned fabricated eventSeq
def test_legacy_parent_rejects_event_seq():
    with pytest.raises(IdentityError):
        parent(case_era="PRE_EVENTSEQ_LEGACY", live_event_seq=SEQ)
    legacy = parent(case_era="PRE_EVENTSEQ_LEGACY", live_event_seq=None)
    with pytest.raises(IdentityError):
        dataclasses.replace(legacy, live_event_seq=SEQ)
    with pytest.raises(IdentityError):  # stages cannot smuggle a seq in either
        EarlyRebreakCase(parent=legacy, fvg=StageObservation(SEQ, T("01:15")))


# 10. No research signal can be promoted to production automatically
def test_no_automatic_promotion():
    c = full_case()
    assert c.promotion_status == "RESEARCH_ONLY"
    with pytest.raises(PromotionError):
        rm.promote_to_production(c)
    assert rm.PRODUCTION_AUTHORIZED is False
    assert rm.PINE_IMPLEMENTATION_AUTHORIZED is False
    assert rm.LIVE_ALERT_IMPLEMENTATION_AUTHORIZED is False
    assert rm.PROSPECTIVE_ENROLLMENT == "NOT_AUTHORIZED"
    assert rm.STATUS == "EXPERIMENTAL"


# 11. A-Early remains experimental
def test_a_early_remains_experimental():
    assert rm.A_EARLY_STATUS == "EXPERIMENTAL"
    assert rm.A_PLUS_STATUS == "FROZEN_CONTROL"
    text = (PROJECT_ROOT / "CONTROL" / "CHANGE_CONTROL.md").read_text()
    assert "| A-Early | **EXPERIMENTAL** |" in text
    assert "| LAS-15 A+ | **FROZEN CONTROL** |" in text


# 12. Frozen A+ control files remain semantically unchanged
FROZEN_SHA256 = {
    "CONTROL/RESEARCH_STATUS.md": "df49a8bc4c73b711ffc9294c23bedf782bca45bcab162f96f339f859bbed7bce",
    "CONTROL/SOURCE_OF_TRUTH.md": "f0d090c408c6abb153a5ec591874b3af42512bc307e241d6ac95b9baca028f91",
    "production/README.md": "26b900890d6fa5ce3552ab2b070828bcecd1ab77b341230db34f573d1f2ea1a5",
    "research/event_identity/EVENT_IDENTITY_SPEC_v0.1.md": "23474b17cd66d3d1f7f8e1d2c7f2c750ae00afbc2f251d8467414caa26d70a54",
    "research/event_identity/PROSPECTIVE_EVENT_SCHEMA_v0.1.md": "b8b0f5d7e1c8f4f943e138a19f7ac57b87858d1da3b1af5583b5221d109eb0f3",
    "research/event_identity/research_model.py": "ff9b2679317c3c6be482a8d1a6521bff61502a75e7e783f2a292b78aa67dc42e",
    "research/pullback_hypothesis/PROTOCOL_DRAFT_v0.1.md": "5d047ef345503c77727110f910b5bf5508b19b88034ca2cea90eb358b17e441a",
}
# CHANGE_CONTROL.md: everything above the append-only change log is frozen.
CHANGE_CONTROL_FROZEN_SECTION_SHA256 = "7e14a3fd21917a2af6527d0aa01e997cdcda91c40dd8031c494c6b325f19d602"


@pytest.mark.parametrize("rel, digest", sorted(FROZEN_SHA256.items()))
def test_frozen_files_unchanged(rel, digest):
    assert hashlib.sha256((PROJECT_ROOT / rel).read_bytes()).hexdigest() == digest


def test_change_control_frozen_section_unchanged():
    text = (PROJECT_ROOT / "CONTROL" / "CHANGE_CONTROL.md").read_text()
    frozen = text.split("## Change log")[0]
    assert hashlib.sha256(frozen.encode()).hexdigest() == CHANGE_CONTROL_FROZEN_SECTION_SHA256


def test_no_production_pine_present():
    assert sorted(p.name for p in (PROJECT_ROOT / "production").iterdir()) == ["README.md"]
    assert not list(PROJECT_ROOT.rglob("*.pine"))


# Supporting: comparison metrics and outcomes
def test_latency_and_move_consumed_metrics():
    c = full_case()
    lat = {k: v.total_seconds() / 60 for k, v in c.latencies.items()}
    assert lat == {"EVENT_TO_RESOLUTION": 30, "RESOLUTION_TO_CT_BREAK": 15, "CT_BREAK_TO_REBREAK": 15,
                   "CT_BREAK_TO_A_PLUS": 45, "REBREAK_TO_A_PLUS": 30}
    assert c.prices == {"PRICE_AT_CT_BREAK": 101.5, "PRICE_AT_REBREAK": 101.6, "PRICE_AT_A_PLUS": 102.2}
    mc = c.move_consumed_before_entry
    assert mc["MOVE_CONSUMED_BEFORE_DIRECT_ENTRY"] == pytest.approx(3.5)
    assert mc["MOVE_CONSUMED_BEFORE_REBREAK"] == pytest.approx(3.6)
    assert mc["MOVE_CONSUMED_BEFORE_A_PLUS"] == pytest.approx(4.2)


def test_outcome_r_measures():
    b = branch("DIRECT_CONTROL_BREAK", T("00:45"), 101.5, first_touch="STOP_FIRST",
               mfe=2.0, mae=4.0, outcome_resolved_at=T("02:00"))
    assert (b.mfe_r, b.mae_r, b.realized_r) == (pytest.approx(0.5), pytest.approx(1.0), -1.0)
    assert dataclasses.replace(b, first_touch="RIGHT_CENSORED").realized_r is None
    assert dataclasses.replace(b, first_touch="FTA_FIRST").realized_r == pytest.approx(b.r_to_fta)


def test_no_signal_means_no_entry_or_outcome():
    with pytest.raises(ValueError):
        BranchResult("PULLBACK_REBREAK", "LONG", signal=False, first_touch="NEITHER")
    assert BranchResult("PULLBACK_REBREAK", "LONG", signal=False).r_to_fta is None


def test_branch_signal_requires_its_trigger_and_cannot_precede_it():
    with pytest.raises(LineageError):
        full_case(a_plus_signal=None)
    with pytest.raises(LineageError):
        full_case(direct_branch=branch("DIRECT_CONTROL_BREAK", T("00:40"), 101.5))


def test_location_cannot_be_classified_after_outcome():
    with pytest.raises(LineageError):
        full_case(parent=parent(location_classified_at=T("01:10")))


def test_stratum_keeps_htf_btc_location_regime_separate():
    assert parent().stratum == ("COUNTER_HTF", "BTC_NEUTRAL", "MAJOR_EXTERNAL_1H", "UNKNOWN")


# Readiness gate: incomplete protocol can never be declared ready for enrollment
DEPENDENCY_FIELDS = [f.name for f in dataclasses.fields(rm.ProtocolDependencies)]


def test_current_protocol_not_ready_and_incomplete():
    assert rm.PROTOCOL_READY_FOR_ENROLLMENT is False
    assert rm.PROTOCOL_COMPLETE is False
    assert rm.MISSING_AUTHORITATIVE_DEFINITIONS is True
    assert len(rm.CURRENT_DEPENDENCIES.missing()) == 7
    assert rm.PIVOT_FIDELITY_STATUS == "MATERIAL_RESEARCH_FIDELITY_DEFECT"


@pytest.mark.parametrize("missing", DEPENDENCY_FIELDS)
def test_any_single_missing_dependency_blocks_readiness(missing):
    deps = rm.ProtocolDependencies(**{f: f != missing for f in DEPENDENCY_FIELDS})
    assert deps.missing() == (missing.upper(),)
    assert rm.protocol_ready_for_enrollment(deps) is False


def test_readiness_requires_real_dependency_object_and_is_not_authorization():
    assert rm.protocol_ready_for_enrollment({f: True for f in DEPENDENCY_FIELDS}) is False
    assert rm.protocol_ready_for_enrollment(rm.ProtocolDependencies(**{f: "YES" for f in DEPENDENCY_FIELDS})) is False
    all_met = rm.ProtocolDependencies(**{f: True for f in DEPENDENCY_FIELDS})
    assert rm.protocol_ready_for_enrollment(all_met) is True  # hypothetical future state only
    assert rm.PROSPECTIVE_ENROLLMENT == "NOT_AUTHORIZED"   # readiness never authorizes enrollment
    with pytest.raises(dataclasses.FrozenInstanceError):
        rm.CURRENT_DEPENDENCIES.fta_rules_imported = True
