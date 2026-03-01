from apps.courses.judge.runner import run_in_sandbox

def evaluate(problem, language: str, source_code: str) -> tuple[str, str | None]:
    """
    returns: (status, error_message)
    """
    tests = problem.tests.all().order_by("id")
    for t in tests:
        r = run_in_sandbox(language, source_code, t.input_data)
        if r.timeout:
            return ("error", "Time limit exceeded")
        if not r.ok:
            return ("error", (r.stderr or "Runtime/Compile error")[:2000])

        out = (r.stdout or "").strip()
        exp = (t.output_data or "").strip()
        if out != exp:
            return ("rejected", f"Wrong answer. Expected={exp} Got={out}")

    return ("accepted", None)