from src.resume_tailoring.page_fit import (
    PageFitResult,
    classify_page_fit,
)


def test_page_fit_result_stores_measurement():
    result = PageFitResult(
        page_count=1,
        content_height_points=680.0,
        usable_height_points=720.0,
    )

    assert result.page_count == 1
    assert result.content_height_points == 680.0
    assert result.usable_height_points == 720.0


def test_page_fit_result_is_immutable():
    result = PageFitResult(
        page_count=1,
        content_height_points=680.0,
        usable_height_points=720.0,
    )

    try:
        result.page_count = 2
    except AttributeError:
        pass
    else:
        raise AssertionError("PageFitResult must be immutable.")


def test_page_fit_result_calculates_fill_ratio():
    result = PageFitResult(
        page_count=1,
        content_height_points=684.0,
        usable_height_points=720.0,
    )

    assert result.fill_ratio == 0.95


def test_page_fit_result_reports_overflow_for_multiple_pages():
    result = PageFitResult(
        page_count=2,
        content_height_points=760.0,
        usable_height_points=720.0,
    )

    assert result.fits_one_page is False


def test_page_fit_result_reports_one_page_fit():
    result = PageFitResult(
        page_count=1,
        content_height_points=700.0,
        usable_height_points=720.0,
    )

    assert result.fits_one_page is True


def test_classify_page_fit_reports_overfull_for_multiple_pages():
    result = PageFitResult(
        page_count=2,
        content_height_points=760.0,
        usable_height_points=720.0,
    )

    assert classify_page_fit(result) == "overfull"


def test_classify_page_fit_reports_underfilled_when_too_much_space_remains():
    result = PageFitResult(
        page_count=1,
        content_height_points=600.0,
        usable_height_points=720.0,
    )

    assert classify_page_fit(result) == "underfilled"


def test_classify_page_fit_reports_target_when_page_is_well_filled():
    result = PageFitResult(
        page_count=1,
        content_height_points=684.0,
        usable_height_points=720.0,
    )

    assert classify_page_fit(result) == "target"


def test_classify_page_fit_treats_safe_near_full_page_as_target():
    result = PageFitResult(
        page_count=1,
        content_height_points=705.0,
        usable_height_points=720.0,
    )

    assert classify_page_fit(result) == "target"


def test_classify_page_fit_reports_overfull_when_measured_height_exceeds_page():
    result = PageFitResult(
        page_count=1,
        content_height_points=725.0,
        usable_height_points=720.0,
    )

    assert classify_page_fit(result) == "overfull"


def test_page_fit_rejects_zero_usable_height():
    try:
        PageFitResult(
            page_count=1,
            content_height_points=600.0,
            usable_height_points=0.0,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "PageFitResult must reject zero usable height."
        )


def test_page_fit_rejects_negative_measurements():
    try:
        PageFitResult(
            page_count=1,
            content_height_points=-1.0,
            usable_height_points=720.0,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "PageFitResult must reject negative measurements."
        )