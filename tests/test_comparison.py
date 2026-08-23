from qa_corpus.comparison import (
    compare_semantic_json,
    evaluate_reference_assertions,
)
from qa_corpus.manifest import (
    NumericTolerance,
    ReferenceBackedExpectation,
    SemanticJsonComparison,
    ValueAssertion,
)


def test_semantic_comparison_ignores_object_order_but_not_array_order() -> None:
    profile = SemanticJsonComparison(mode="semantic-json")

    assert (
        compare_semantic_json(
            {"values": [1, 2], "name": "budget"},
            {"name": "budget", "values": [1, 2]},
            profile,
        )
        == []
    )

    issues = compare_semantic_json(
        {"values": [1, 2]},
        {"values": [2, 1]},
        profile,
    )

    assert [issue["pointer"] for issue in issues] == ["/values/0", "/values/1"]


def test_semantic_comparison_applies_pointer_specific_tolerance() -> None:
    profile = SemanticJsonComparison(
        mode="semantic-json",
        tolerances=[NumericTolerance(pointer="/value", absolute=0.01)],
    )

    assert compare_semantic_json({"value": 10.0}, {"value": 10.005}, profile) == []
    assert compare_semantic_json({"other": 10.0}, {"other": 10.005}, profile)


def test_reference_assertions_report_only_failed_pointers() -> None:
    expectation = ReferenceBackedExpectation(
        kind="reference-backed",
        evidence="reference/calculation.md",
        assertions=[
            ValueAssertion(
                pointer="/node/value/si_value",
                expected=10.0,
                absolute_tolerance=0.01,
            ),
            ValueAssertion(pointer="/node/value/unit", expected="kg"),
        ],
    )

    issues = evaluate_reference_assertions(
        {"node": {"value": {"si_value": 10.005, "unit": "m"}}},
        expectation,
    )

    assert issues == [
        {
            "pointer": "/node/value/unit",
            "message": "assertion failed",
            "expected": "kg",
            "actual": "m",
        }
    ]
