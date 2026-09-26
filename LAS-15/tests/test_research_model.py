"""Tests for the RESEARCH DATA MODEL only. These are NOT Pine regression tests."""

import dataclasses
from pathlib import Path

import pytest

from research_model import (
    CaseEra,
    EventRecord,
    FvgAttribution,
    IdentityError,
    ProductionChangeJustified,
    ProspectiveEnrollment,
    ResearchGovernance,
    WatchAttribution,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def prospective(**kw):
    base = dict(
        symbol="BINANCE:BTCUSDT.P",
        research_case_id="TEST-PROSPECTIVE-001",
        case_era=CaseEra.PROSPECTIVE,
        data_provenance="unit test fixture (not real data)",
    )
    base.update(kw)
    return EventRecord(**base)


def legacy(**kw):
    base = dict(
        symbol="BINANCE:BTCUSDT.P",
        research_case_id="TEST-LEGACY-001",
        case_era=CaseEra.PRE_EVENTSEQ_LEGACY,
        data_provenance="unit test fixture (not real data)",
    )
    base.update(kw)
    return EventRecord(**base)


# 1. research records permit LIVE_EVENT_SEQ = null
def test_live_event_seq_null_is_permitted_and_default():
    assert prospective().live_event_seq is None
    assert prospective(live_event_seq=None).live_event_seq is None
    assert legacy().live_event_seq is None


# 2. legacy cases cannot silently receive fabricated eventSeq values
@pytest.mark.parametrize("field", ["live_event_seq", "watch_event_seq", "fvg_event_seq"])
def test_legacy_rejects_event_seq_at_construction(field):
    with pytest.raises(IdentityError):
        legacy(**{field: 42})


@pytest.mark.parametrize("field", ["live_event_seq", "watch_event_seq", "fvg_event_seq"])
def test_legacy_rejects_event_seq_via_replace(field):
    rec = legacy()
    with pytest.raises(IdentityError):
        dataclasses.replace(rec, **{field: 42})


def test_legacy_rejects_direct_mutation():
    rec = legacy()
    with pytest.raises(dataclasses.FrozenInstanceError):
        rec.live_event_seq = 42


# 3. WATCH cannot be EXACT without identity evidence
@pytest.mark.parametrize(
    "live, watch",
    [(None, None), (None, 7), (7, None), (7, 8)],
)
def test_watch_exact_requires_identity_evidence(live, watch):
    with pytest.raises(IdentityError):
        prospective(live_event_seq=live, watch_event_seq=watch,
                    watch_attribution=WatchAttribution.EXACT)


def test_watch_exact_accepted_with_matching_identity():
    rec = prospective(live_event_seq=7, watch_event_seq=7,
                      watch_attribution=WatchAttribution.EXACT)
    assert rec.watch_attribution is WatchAttribution.EXACT


def test_legacy_watch_cannot_be_exact():
    with pytest.raises(IdentityError):
        legacy(watch_attribution="EXACT")


def test_watch_attribution_defaults_to_unattributed():
    assert prospective().watch_attribution is WatchAttribution.UNATTRIBUTED


# 4. FVG cannot be SAME_EVENT without identity evidence
@pytest.mark.parametrize(
    "live, fvg",
    [(None, None), (None, 7), (7, None), (7, 8)],
)
def test_fvg_same_event_requires_identity_evidence(live, fvg):
    with pytest.raises(IdentityError):
        prospective(live_event_seq=live, fvg_event_seq=fvg,
                    fvg_attribution=FvgAttribution.SAME_EVENT)


def test_fvg_same_event_accepted_with_matching_identity():
    rec = prospective(live_event_seq=7, fvg_event_seq=7,
                      fvg_attribution=FvgAttribution.SAME_EVENT)
    assert rec.fvg_attribution is FvgAttribution.SAME_EVENT


def test_legacy_fvg_cannot_be_same_event():
    with pytest.raises(IdentityError):
        legacy(fvg_attribution="SAME_EVENT")


def test_fvg_attribution_defaults_to_unattributed():
    assert prospective().fvg_attribution is FvgAttribution.UNATTRIBUTED


# 5. production-change status defaults to NO
def test_production_change_defaults_to_no():
    assert ResearchGovernance().production_change_justified is ProductionChangeJustified.NO


def test_research_status_doc_records_production_change_no():
    text = (PROJECT_ROOT / "CONTROL" / "RESEARCH_STATUS.md").read_text()
    assert "| PRODUCTION_CHANGE_JUSTIFIED | NO |" in text


# 6. prospective-enrollment status defaults to NOT_AUTHORIZED
def test_prospective_enrollment_defaults_to_not_authorized():
    assert ResearchGovernance().prospective_enrollment is ProspectiveEnrollment.NOT_AUTHORIZED


# Supporting: provenance is mandatory (no unattributed / fabricated data)
@pytest.mark.parametrize("prov", ["", "   "])
def test_data_provenance_required(prov):
    with pytest.raises(ValueError):
        prospective(data_provenance=prov)


# Supporting: historical classifications are representable without eventSeq
@pytest.mark.parametrize(
    "case_id, watch",
    [
        ("P4", WatchAttribution.NO_WATCH_FOR_ORIGINAL_EVENT),
        ("P5", WatchAttribution.NO_WATCH_FOR_ORIGINAL_EVENT),
        ("P6", WatchAttribution.AMBIGUOUS_EVENT_IDENTITY),
    ],
)
def test_historical_watch_classifications_are_legacy_without_seq(case_id, watch):
    rec = legacy(research_case_id=case_id, watch_attribution=watch)
    assert rec.case_era is CaseEra.PRE_EVENTSEQ_LEGACY
    assert rec.live_event_seq is None
