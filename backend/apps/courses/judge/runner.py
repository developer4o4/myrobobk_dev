import os, subprocess, uuid, shutil
from pathlib import Path
import tempfile
from dataclasses import dataclass

@dataclass
class RunResult:
    ok: bool
    stdout: str
    stderr: str
    exit_code: int
    timeout: bool = False

def _docker_run(cmd: list[str], timeout_sec: int = 3) -> RunResult:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec)
        return RunResult(ok=(p.returncode == 0), stdout=p.stdout, stderr=p.stderr, exit_code=p.returncode)
    except subprocess.TimeoutExpired as e:
        return RunResult(ok=False, stdout=e.stdout or "", stderr=e.stderr or "timeout", exit_code=124, timeout=True)

def run_in_sandbox(language: str, source_code: str, input_data: str) -> RunResult:
    if not shutil.which("docker"):
        return RunResult(False, "", "Docker CLI topilmadi", 1)

    sandbox_image = "judge-sandbox:latest"
    job_id = str(uuid.uuid4())
    base_dir = Path("/judge_runs")
    base_dir.mkdir(parents=True, exist_ok=True)

    td = base_dir / job_id
    td.mkdir(parents=True, exist_ok=True)
    try:
        if language == "py":
            src_name = "main.py"
        elif language == "c":
            src_name = "main.c"
        elif language == "cpp":
            src_name = "main.cpp"
        else:
            return RunResult(False, "", "Unsupported language", 1)

        (td / src_name).write_text(source_code, encoding="utf-8")
        (td / "input.txt").write_text(input_data or "", encoding="utf-8")

        os.chmod(td, 0o777)
        os.chmod(td / src_name, 0o666)
        os.chmod(td / "input.txt", 0o666)
        base = [
            "docker", "run", "--rm",
            "--network", "none",
            "--memory", "256m",
            "--cpus", "0.5",
            "--pids-limit", "64",
            "--read-only",

            "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m",

            "-v", f"{td.as_posix()}:/work:rw",
            "-w", "/work",
            sandbox_image,
            "bash", "-lc",
        ]

        if language == "py":
            script = "python3 main.py < input.txt"
        elif language == "c":
            script = "gcc -O2 -std=c11 main.c -o app && ./app < input.txt"
        if language == "cpp":
            compile_cmd = "g++ -O2 -pipe -std=c++17 main.cpp -o app"
            r1 = _docker_run(base + [compile_cmd], timeout_sec=15)
            if not r1.ok:
                return r1
            run_cmd = "./app < input.txt"
            return _docker_run(base + [run_cmd], timeout_sec=3)

        return _docker_run(base + [script], timeout_sec=5)

    finally:
        # tozalash (xohlasangiz saqlab ham qo'yishingiz mumkin)
        try:
            for p in td.iterdir():
                p.unlink(missing_ok=True)
            td.rmdir()
        except Exception:
            pass