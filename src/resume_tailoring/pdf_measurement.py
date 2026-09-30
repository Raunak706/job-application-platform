import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


_PAGE_COUNT_PATTERN = re.compile(
    r"\((\d+)\s+pages?,"
)

_CONTENT_HEIGHT_PATTERN = re.compile(
    r"RESUME_CONTENT_HEIGHT_POINTS=\s*"
    r"([0-9]+(?:\.[0-9]+)?)"
)

_USABLE_HEIGHT_PATTERN = re.compile(
    r"RESUME_USABLE_HEIGHT_POINTS=\s*"
    r"([0-9]+(?:\.[0-9]+)?)"
)


class LatexCompilationError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class LatexCompilationResult:
    page_count: int
    pdf_path: Path
    compiler_output: str


def extract_page_count(output: str) -> int:
    matches = _PAGE_COUNT_PATTERN.findall(output)

    if not matches:
        raise ValueError(
            "Could not determine PDF page count "
            "from pdflatex output."
        )

    return int(matches[-1])


def extract_content_height(output: str) -> float:
    matches = _CONTENT_HEIGHT_PATTERN.findall(output)

    if not matches:
        raise ValueError(
            "Could not determine resume content height "
            "from pdflatex output."
        )

    return float(matches[-1])


def extract_usable_height(output: str) -> float:
    matches = _USABLE_HEIGHT_PATTERN.findall(output)

    if not matches:
        raise ValueError(
            "Could not determine usable page height "
            "from pdflatex output."
        )

    return float(matches[-1])


def compile_latex(
    *,
    latex_source: str,
    work_directory: Path,
) -> LatexCompilationResult:
    work_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    tex_path = work_directory / "resume.tex"
    pdf_path = work_directory / "resume.pdf"

    tex_path.write_text(
        latex_source,
        encoding="utf-8",
    )

    command = [
        "pdflatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        tex_path.name,
    ]

    outputs = []

    for _ in range(2):
        completed = subprocess.run(
            command,
            cwd=work_directory,
            capture_output=True,
            text=True,
            check=False,
        )

        pass_output = (
            completed.stdout + completed.stderr
        )

        outputs.append(pass_output)

        if completed.returncode != 0:
            raise LatexCompilationError(
                "LaTeX compilation failed.\n"
                + pass_output
            )

    compiler_output = "\n".join(outputs)

    if not pdf_path.exists():
        raise LatexCompilationError(
            "LaTeX compilation did not produce a PDF."
        )

    page_count = extract_page_count(
        compiler_output
    )

    return LatexCompilationResult(
        page_count=page_count,
        pdf_path=pdf_path,
        compiler_output=compiler_output,
    )