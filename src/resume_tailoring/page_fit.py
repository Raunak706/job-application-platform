from dataclasses import dataclass

from src.resume_tailoring.pdf_measurement import (
    LatexCompilationResult,
    extract_content_height,
    extract_usable_height,
)


TARGET_MIN_FILL_RATIO = 0.90


@dataclass(frozen=True, slots=True)
class PageFitResult:
    page_count: int
    content_height_points: float
    usable_height_points: float

    def __post_init__(self) -> None:
        if self.page_count < 1:
            raise ValueError(
                "Page count must be at least one."
            )

        if self.content_height_points < 0:
            raise ValueError(
                "Content height cannot be negative."
            )

        if self.usable_height_points <= 0:
            raise ValueError(
                "Usable page height must be positive."
            )

    @property
    def fill_ratio(self) -> float:
        return (
            self.content_height_points
            / self.usable_height_points
        )

    @property
    def fits_one_page(self) -> bool:
        return (
            self.page_count == 1
            and self.content_height_points
            <= self.usable_height_points
        )


def build_page_fit_result(
    *,
    page_count: int,
    content_height_points: float,
    usable_height_points: float,
    measurement_is_first_page_only: bool = False,
) -> PageFitResult:
    if (
        measurement_is_first_page_only
        and page_count > 1
        and content_height_points > usable_height_points
    ):
        raise ValueError(
            "Measured first-page content height cannot exceed "
            "the usable page height."
        )

    return PageFitResult(
        page_count=page_count,
        content_height_points=content_height_points,
        usable_height_points=usable_height_points,
    )


def build_page_fit_result_from_compilation(
    compilation: LatexCompilationResult,
) -> PageFitResult:
    content_height_points = extract_content_height(
        compilation.compiler_output
    )

    usable_height_points = extract_usable_height(
        compilation.compiler_output
    )

    return build_page_fit_result(
        page_count=compilation.page_count,
        content_height_points=content_height_points,
        usable_height_points=usable_height_points,
    )


def classify_page_fit(
    result: PageFitResult,
) -> str:
    if not result.fits_one_page:
        return "overfull"

    if result.fill_ratio < TARGET_MIN_FILL_RATIO:
        return "underfilled"

    return "target"