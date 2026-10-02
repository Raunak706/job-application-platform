from pathlib import Path

import pytest

from src.resume_tailoring.page_fit import (
    PageFitResult,
    build_page_fit_result,
    build_page_fit_result_from_compilation,
    classify_page_fit,
)
from src.resume_tailoring.pdf_measurement import (
    LatexCompilationResult,
)


def test_build_page_fit_result_preserves_measurement():
    result = build_page_fit_result(
        page_count=1,
        content_height_points=684.0,
        usable_height_points=720.0,
    )

    assert result == PageFitResult(
        page_count=1,
        content_height_points=684.0,
        usable_height_points=720.0,
    )


def test_build_page_fit_result_preserves_page_count():
    result = build_page_fit_result(
        page_count=2,
        content_height_points=720.0,
        usable_height_points=720.0,
    )

    assert result.page_count == 2


def test_build_page_fit_result_preserves_exact_usable_height():
    result = build_page_fit_result(
        page_count=1,
        content_height_points=684.0,
        usable_height_points=719.5,
    )

    assert result.usable_height_points == pytest.approx(
        719.5
    )


def test_first_page_measurement_can_equal_usable_height():
    result = build_page_fit_result(
        page_count=2,
        content_height_points=720.0,
        usable_height_points=720.0,
        measurement_is_first_page_only=True,
    )

    assert result.content_height_points == pytest.approx(
        720.0
    )


def test_first_page_measurement_cannot_exceed_usable_height():
    with pytest.raises(
        ValueError,
        match="Measured first-page content height cannot exceed",
    ):
        build_page_fit_result(
            page_count=2,
            content_height_points=721.0,
            usable_height_points=720.0,
            measurement_is_first_page_only=True,
        )


def test_build_page_fit_result_rejects_negative_measurement():
    with pytest.raises(
        ValueError,
        match="Content height cannot be negative",
    ):
        build_page_fit_result(
            page_count=1,
            content_height_points=-1.0,
            usable_height_points=720.0,
        )


def test_realistic_underfilled_measurement_is_classified():
    result = build_page_fit_result(
        page_count=1,
        content_height_points=600.0,
        usable_height_points=720.0,
    )

    assert classify_page_fit(result) == "underfilled"


def test_realistic_target_measurement_is_classified():
    result = build_page_fit_result(
        page_count=1,
        content_height_points=705.0,
        usable_height_points=720.0,
    )

    assert classify_page_fit(result) == "target"


def test_multiple_pages_are_overfull_even_with_small_height():
    result = build_page_fit_result(
        page_count=2,
        content_height_points=100.0,
        usable_height_points=720.0,
    )

    assert classify_page_fit(result) == "overfull"


def test_build_page_fit_result_from_compilation():
    compilation = LatexCompilationResult(
        page_count=1,
        pdf_path=Path("/tmp/resume.pdf"),
        compiler_output=(
            "RESUME_CONTENT_HEIGHT_POINTS= 684.25\n"
            "RESUME_USABLE_HEIGHT_POINTS= 722.7\n"
            "Output written on resume.pdf "
            "(1 page, 12345 bytes)."
        ),
    )

    result = build_page_fit_result_from_compilation(
        compilation
    )

    assert result == PageFitResult(
        page_count=1,
        content_height_points=684.25,
        usable_height_points=722.7,
    )


def test_compilation_measurement_classifies_underfilled_resume():
    compilation = LatexCompilationResult(
        page_count=1,
        pdf_path=Path("/tmp/resume.pdf"),
        compiler_output=(
            "RESUME_CONTENT_HEIGHT_POINTS= 600.0\n"
            "RESUME_USABLE_HEIGHT_POINTS= 722.7\n"
        ),
    )

    result = build_page_fit_result_from_compilation(
        compilation
    )

    assert classify_page_fit(result) == "underfilled"


def test_compilation_measurement_classifies_target_resume():
    compilation = LatexCompilationResult(
        page_count=1,
        pdf_path=Path("/tmp/resume.pdf"),
        compiler_output=(
            "RESUME_CONTENT_HEIGHT_POINTS= 705.0\n"
            "RESUME_USABLE_HEIGHT_POINTS= 720.0\n"
        ),
    )

    result = build_page_fit_result_from_compilation(
        compilation
    )

    assert classify_page_fit(result) == "target"


def test_compilation_measurement_classifies_multiple_pages_overfull():
    compilation = LatexCompilationResult(
        page_count=2,
        pdf_path=Path("/tmp/resume.pdf"),
        compiler_output=(
            "RESUME_CONTENT_HEIGHT_POINTS= 500.0\n"
            "RESUME_USABLE_HEIGHT_POINTS= 722.7\n"
        ),
    )

    result = build_page_fit_result_from_compilation(
        compilation
    )

    assert result.page_count == 2
    assert classify_page_fit(result) == "overfull"