import subprocess

import pytest

from src.resume_tailoring.pdf_measurement import (
    LatexCompilationError,
    compile_latex,
    extract_content_height,
    extract_page_count,
    extract_usable_height,
)


def test_extract_page_count_from_single_page_pdflatex_output():
    output = (
        "Output written on resume.pdf "
        "(1 page, 12345 bytes)."
    )

    assert extract_page_count(output) == 1


def test_extract_page_count_from_multiple_page_pdflatex_output():
    output = (
        "Output written on resume.pdf "
        "(2 pages, 23456 bytes)."
    )

    assert extract_page_count(output) == 2


def test_extract_page_count_uses_last_compilation_pass():
    output = (
        "Output written on resume.pdf "
        "(2 pages, 23456 bytes).\n"
        "Output written on resume.pdf "
        "(1 page, 12345 bytes).\n"
    )

    assert extract_page_count(output) == 1


def test_extract_page_count_rejects_missing_page_information():
    with pytest.raises(
        ValueError,
        match="Could not determine PDF page count",
    ):
        extract_page_count("Compilation completed.")


def test_extract_content_height_from_pdflatex_output():
    output = "RESUME_CONTENT_HEIGHT_POINTS=684.25"

    assert extract_content_height(output) == pytest.approx(
        684.25
    )


def test_extract_content_height_accepts_latex_whitespace():
    output = "RESUME_CONTENT_HEIGHT_POINTS= 684.25"

    assert extract_content_height(output) == pytest.approx(
        684.25
    )


def test_extract_content_height_uses_last_measurement():
    output = (
        "RESUME_CONTENT_HEIGHT_POINTS=640.0\n"
        "other output\n"
        "RESUME_CONTENT_HEIGHT_POINTS=682.5\n"
    )

    assert extract_content_height(output) == pytest.approx(
        682.5
    )


def test_extract_content_height_rejects_missing_measurement():
    with pytest.raises(
        ValueError,
        match="Could not determine resume content height",
    ):
        extract_content_height("Compilation completed.")


def test_extract_usable_height_from_pdflatex_output():
    output = "RESUME_USABLE_HEIGHT_POINTS=720.0"

    assert extract_usable_height(output) == pytest.approx(
        720.0
    )


def test_extract_usable_height_accepts_latex_whitespace():
    output = "RESUME_USABLE_HEIGHT_POINTS= 720.0"

    assert extract_usable_height(output) == pytest.approx(
        720.0
    )


def test_extract_usable_height_uses_last_measurement():
    output = (
        "RESUME_USABLE_HEIGHT_POINTS=700.0\n"
        "other output\n"
        "RESUME_USABLE_HEIGHT_POINTS=720.0\n"
    )

    assert extract_usable_height(output) == pytest.approx(
        720.0
    )


def test_extract_usable_height_rejects_missing_measurement():
    with pytest.raises(
        ValueError,
        match="Could not determine usable page height",
    ):
        extract_usable_height("Compilation completed.")


def test_compile_latex_runs_two_passes_and_returns_final_result(
    tmp_path,
    monkeypatch,
):
    calls = []

    def fake_run(
        command,
        *,
        cwd,
        capture_output,
        text,
        check,
    ):
        calls.append(command)

        assert command[0] == "pdflatex"
        assert "-interaction=nonstopmode" in command
        assert "-halt-on-error" in command
        assert cwd == tmp_path
        assert capture_output is True
        assert text is True
        assert check is False

        pdf_path = tmp_path / "resume.pdf"
        pdf_path.write_bytes(b"%PDF synthetic")

        pass_number = len(calls)

        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout=(
                f"PASS={pass_number}\n"
                "RESUME_CONTENT_HEIGHT_POINTS="
                f"{640.0 + pass_number}\n"
                "RESUME_USABLE_HEIGHT_POINTS=720.0\n"
                "Output written on resume.pdf "
                "(1 page, 12345 bytes)."
            ),
            stderr="",
        )

    monkeypatch.setattr(
        subprocess,
        "run",
        fake_run,
    )

    result = compile_latex(
        latex_source=(
            r"\documentclass{article}"
            r"\begin{document}Test\end{document}"
        ),
        work_directory=tmp_path,
    )

    assert len(calls) == 2
    assert result.page_count == 1
    assert result.pdf_path == tmp_path / "resume.pdf"
    assert result.pdf_path.exists()

    assert extract_content_height(
        result.compiler_output
    ) == pytest.approx(642.0)

    assert extract_usable_height(
        result.compiler_output
    ) == pytest.approx(720.0)

    assert "PASS=1" in result.compiler_output
    assert "PASS=2" in result.compiler_output


def test_compile_latex_raises_when_first_pass_fails(
    tmp_path,
    monkeypatch,
):
    calls = []

    def fake_run(
        command,
        *,
        cwd,
        capture_output,
        text,
        check,
    ):
        calls.append(command)

        return subprocess.CompletedProcess(
            args=command,
            returncode=1,
            stdout="! Undefined control sequence.",
            stderr="",
        )

    monkeypatch.setattr(
        subprocess,
        "run",
        fake_run,
    )

    with pytest.raises(
        LatexCompilationError,
        match="LaTeX compilation failed",
    ):
        compile_latex(
            latex_source="invalid latex",
            work_directory=tmp_path,
        )

    assert len(calls) == 1


def test_compile_latex_raises_when_second_pass_fails(
    tmp_path,
    monkeypatch,
):
    calls = []

    def fake_run(
        command,
        *,
        cwd,
        capture_output,
        text,
        check,
    ):
        calls.append(command)

        if len(calls) == 1:
            return subprocess.CompletedProcess(
                args=command,
                returncode=0,
                stdout=(
                    "Output written on resume.pdf "
                    "(1 page, 12345 bytes)."
                ),
                stderr="",
            )

        return subprocess.CompletedProcess(
            args=command,
            returncode=1,
            stdout="! Second pass failed.",
            stderr="",
        )

    monkeypatch.setattr(
        subprocess,
        "run",
        fake_run,
    )

    with pytest.raises(
        LatexCompilationError,
        match="LaTeX compilation failed",
    ):
        compile_latex(
            latex_source="invalid latex",
            work_directory=tmp_path,
        )

    assert len(calls) == 2


def test_compile_latex_raises_when_pdf_is_missing(
    tmp_path,
    monkeypatch,
):
    calls = []

    def fake_run(
        command,
        *,
        cwd,
        capture_output,
        text,
        check,
    ):
        calls.append(command)

        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout=(
                "RESUME_CONTENT_HEIGHT_POINTS=684.0\n"
                "RESUME_USABLE_HEIGHT_POINTS=720.0\n"
                "Output written on resume.pdf "
                "(1 page, 12345 bytes)."
            ),
            stderr="",
        )

    monkeypatch.setattr(
        subprocess,
        "run",
        fake_run,
    )

    with pytest.raises(
        LatexCompilationError,
        match="did not produce a PDF",
    ):
        compile_latex(
            latex_source=(
                r"\documentclass{article}"
                r"\begin{document}Test\end{document}"
            ),
            work_directory=tmp_path,
        )

    assert len(calls) == 2