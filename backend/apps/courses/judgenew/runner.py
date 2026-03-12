import os
import shutil
import subprocess
import uuid
from pathlib import Path
from dataclasses import dataclass


@dataclass
class RunResult:
    ok: bool
    stdout: str
    stderr: str
    exit_code: int
    timeout: bool = False


BASE_DIR = Path("/judge_runs")
SANDBOX_IMAGE = "judge-sandbox:latest"
SECCOMP_PROFILE = Path("/opt/judge/seccomp.json")


def _truncate(text: str, limit: int = 10000) -> str:
    if not text:
        return ""
    return text[:limit]


def _docker_run(cmd: list[str], timeout_sec: int) -> RunResult:
    try:
        p = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
        return RunResult(
            ok=(p.returncode == 0),
            stdout=_truncate(p.stdout),
            stderr=_truncate(p.stderr),
            exit_code=p.returncode,
        )
    except subprocess.TimeoutExpired as e:
        return RunResult(
            ok=False,
            stdout=_truncate(e.stdout or ""),
            stderr=_truncate(e.stderr or "Time limit exceeded"),
            exit_code=124,
            timeout=True,
        )


def _safe_write(path: Path, content: str) -> None:
    path.write_text(content or "", encoding="utf-8")
    os.chmod(path, 0o600)


def _prepare_job_dir(job_id: str) -> Path:
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    td = BASE_DIR / job_id
    td.mkdir(mode=0o700, parents=True, exist_ok=False)
    return td


def _safe_cleanup(td: Path) -> None:
    if not td.exists():
        return

    try:
        real_base = BASE_DIR.resolve(strict=True)
        real_td = td.resolve(strict=True)
    except Exception:
        return

    if real_base not in real_td.parents:
        return

    shutil.rmtree(real_td, ignore_errors=True)


def run_in_sandbox(language: str, source_code: str, input_data: str) -> RunResult:
    if not shutil.which("docker"):
        return RunResult(False, "", "Docker CLI topilmadi", 1)

    if language not in {"py", "c", "cpp"}:
        return RunResult(False, "", "Unsupported language", 1)

    job_id = str(uuid.uuid4())
    td = _prepare_job_dir(job_id)

    try:
        if language == "py":
            src_name = "main.py"
        elif language == "c":
            src_name = "main.c"
        else:
            src_name = "main.cpp"

        src_path = td / src_name
        input_path = td / "input.txt"

        _safe_write(src_path, source_code)
        _safe_write(input_path, input_data)

        base = [
            "docker", "run", "--rm",
            "--network", "none",
            "--memory", "256m",
            "--memory-swap", "256m",
            "--cpus", "0.5",
            "--pids-limit", "64",
            "--read-only",
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges:true",
            "--security-opt", f"seccomp={SECCOMP_PROFILE}",
            "--user", "1000:1000",
            "--tmpfs", "/tmp:rw,nosuid,nodev,noexec,size=64m",
            "--tmpfs", "/run:rw,nosuid,nodev,noexec,size=16m",
            "-v", f"{td.as_posix()}:/work:rw",
            "-w", "/work",
            SANDBOX_IMAGE,
            "sh", "-c",
        ]

        if language == "py":
            cmd = "timeout 3s python3 main.py < input.txt"
            return _docker_run(base + [cmd], timeout_sec=5)

        if language == "c":
            compile_cmd = "timeout 10s gcc -O2 -std=c11 main.c -o app"
            r1 = _docker_run(base + [compile_cmd], timeout_sec=12)
            if not r1.ok:
                return r1

            run_cmd = "timeout 3s ./app < input.txt"
            return _docker_run(base + [run_cmd], timeout_sec=5)

        compile_cmd = "timeout 10s g++ -O2 -pipe -std=c++17 main.cpp -o app"
        r1 = _docker_run(base + [compile_cmd], timeout_sec=12)
        if not r1.ok:
            return r1

        run_cmd = "timeout 3s ./app < input.txt"
        return _docker_run(base + [run_cmd], timeout_sec=5)

    finally:
        _safe_cleanup(td)