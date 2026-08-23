"""Pure semantic JSON comparison for corpus expectations."""

from __future__ import annotations

import math
from typing import Any

from qa_corpus.manifest import (
    ReferenceBackedExpectation,
    SemanticJsonComparison,
    ValueAssertion,
)


class PointerLookupError(ValueError):
    """A JSON Pointer cannot be resolved against a value."""


def _unescape_pointer_token(token: str) -> str:
    return token.replace("~1", "/").replace("~0", "~")


def resolve_json_pointer(value: Any, pointer: str) -> Any:
    """Resolve an RFC 6901 JSON Pointer or raise PointerLookupError."""
    current = value
    if pointer == "":
        return current

    for raw_token in pointer[1:].split("/"):
        token = _unescape_pointer_token(raw_token)
        match current:
            case dict():
                if token not in current:
                    raise PointerLookupError(f"object key {token!r} does not exist")
                current = current[token]
            case list():
                if not token.isdigit() or (len(token) > 1 and token.startswith("0")):
                    raise PointerLookupError(
                        f"{token!r} is not a canonical array index"
                    )
                index = int(token)
                if index >= len(current):
                    raise PointerLookupError(
                        f"array index {index} is outside length {len(current)}"
                    )
                current = current[index]
            case _:
                raise PointerLookupError(
                    f"cannot select {token!r} from {type(current).__name__}"
                )
    return current


def _pointer_child(pointer: str, token: str) -> str:
    escaped = token.replace("~", "~0").replace("/", "~1")
    return f"{pointer}/{escaped}"


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _issue(
    pointer: str,
    message: str,
    *,
    expected: Any = None,
    actual: Any = None,
    include_values: bool = False,
) -> dict[str, Any]:
    issue: dict[str, Any] = {"pointer": pointer, "message": message}
    if include_values:
        issue["expected"] = expected
        issue["actual"] = actual
    return issue


def _numbers_match(
    expected: float,
    actual: float,
    *,
    absolute: float,
    relative: float,
) -> bool:
    if absolute == 0.0 and relative == 0.0:
        return expected == actual
    return math.isclose(
        actual,
        expected,
        abs_tol=absolute,
        rel_tol=relative,
    )


def validate_comparison_profile(
    expected: Any,
    profile: SemanticJsonComparison,
) -> list[str]:
    """Validate that every tolerance selects a numeric expected value."""
    errors: list[str] = []
    for tolerance in profile.tolerances:
        try:
            selected = resolve_json_pointer(expected, tolerance.pointer)
        except PointerLookupError as error:
            errors.append(f"tolerance {tolerance.pointer!r}: {error}")
            continue
        if not _is_number(selected):
            errors.append(
                f"tolerance {tolerance.pointer!r}: expected value is not numeric"
            )
    return errors


def compare_semantic_json(
    expected: Any,
    actual: Any,
    profile: SemanticJsonComparison,
) -> list[dict[str, Any]]:
    """Compare JSON semantically, applying only explicitly declared tolerances."""
    tolerances = {item.pointer: item for item in profile.tolerances}
    issues: list[dict[str, Any]] = []

    def compare(expected_value: Any, actual_value: Any, pointer: str) -> None:
        tolerance = tolerances.get(pointer)
        if tolerance is not None:
            if not _is_number(expected_value) or not _is_number(actual_value):
                issues.append(
                    _issue(
                        pointer,
                        "numeric tolerance applied to a non-numeric value",
                        expected=expected_value,
                        actual=actual_value,
                        include_values=True,
                    )
                )
            elif not _numbers_match(
                expected_value,
                actual_value,
                absolute=tolerance.absolute,
                relative=tolerance.relative,
            ):
                issues.append(
                    _issue(
                        pointer,
                        "numeric values differ outside tolerance",
                        expected=expected_value,
                        actual=actual_value,
                        include_values=True,
                    )
                )
            return

        if isinstance(expected_value, dict) and isinstance(actual_value, dict):
            for key in sorted(expected_value.keys() - actual_value.keys()):
                issues.append(
                    _issue(
                        _pointer_child(pointer, key),
                        "value is missing from actual output",
                    )
                )
            for key in sorted(actual_value.keys() - expected_value.keys()):
                issues.append(
                    _issue(
                        _pointer_child(pointer, key),
                        "unexpected value in actual output",
                    )
                )
            for key in sorted(expected_value.keys() & actual_value.keys()):
                compare(
                    expected_value[key],
                    actual_value[key],
                    _pointer_child(pointer, key),
                )
            return

        if isinstance(expected_value, list) and isinstance(actual_value, list):
            if len(expected_value) != len(actual_value):
                issues.append(
                    _issue(
                        pointer,
                        "array lengths differ",
                        expected=len(expected_value),
                        actual=len(actual_value),
                        include_values=True,
                    )
                )
            for index, (expected_item, actual_item) in enumerate(
                zip(expected_value, actual_value, strict=False)
            ):
                compare(
                    expected_item,
                    actual_item,
                    _pointer_child(pointer, str(index)),
                )
            return

        if _is_number(expected_value) and _is_number(actual_value):
            matches = expected_value == actual_value
        else:
            matches = type(expected_value) is type(actual_value) and (
                expected_value == actual_value
            )
        if not matches:
            issues.append(
                _issue(
                    pointer,
                    "values differ",
                    expected=expected_value,
                    actual=actual_value,
                    include_values=True,
                )
            )

    compare(expected, actual, "")
    return issues


def _evaluate_assertion(
    actual: Any,
    assertion: ValueAssertion,
) -> dict[str, Any] | None:
    try:
        actual_value = resolve_json_pointer(actual, assertion.pointer)
    except PointerLookupError as error:
        return _issue(assertion.pointer, str(error))

    expected_value = assertion.expected
    if _is_number(expected_value) and _is_number(actual_value):
        matches = _numbers_match(
            expected_value,
            actual_value,
            absolute=assertion.absolute_tolerance,
            relative=assertion.relative_tolerance,
        )
    else:
        matches = type(expected_value) is type(actual_value) and (
            expected_value == actual_value
        )

    if matches:
        return None
    return _issue(
        assertion.pointer,
        "assertion failed",
        expected=expected_value,
        actual=actual_value,
        include_values=True,
    )


def evaluate_reference_assertions(
    actual: Any,
    expectation: ReferenceBackedExpectation,
) -> list[dict[str, Any]]:
    """Evaluate every reference-backed JSON Pointer assertion."""
    return [
        issue
        for assertion in expectation.assertions
        if (issue := _evaluate_assertion(actual, assertion)) is not None
    ]
