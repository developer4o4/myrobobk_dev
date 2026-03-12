from apps.courses.judge.runner import run_in_sandbox


def normalize_output(text: str) -> str:
    return (text or "").strip().replace("\r\n", "\n").replace("\r", "\n")


def evaluate(problem, language: str, source_code: str) -> tuple[str, str | None]:
    tests = problem.tests.all().order_by("id")

    for index, t in enumerate(tests, start=1):
        result = run_in_sandbox(language, source_code, t.input_data)

        if result.timeout:
            return ("error", f"Test #{index}: Time limit exceeded")

        if not result.ok:
            return ("error", f"Test #{index}: {(result.stderr or 'Runtime/Compile error')[:2000]}")

        out = normalize_output(result.stdout)
        exp = normalize_output(t.output_data)

        if out != exp:
            return ("rejected", f"Test #{index}: Wrong answer. Expected={exp!r} Got={out!r}")

    return ("accepted", None)