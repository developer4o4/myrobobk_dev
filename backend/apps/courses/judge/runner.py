import os
import subprocess
import uuid
from dataclasses import dataclass

DOCKER_HOST = os.getenv("DOCKER_HOST", "tcp://dind:2375").strip()
DOCKER_IMAGE = os.getenv("JUDGE_IMAGE", "judge-sandbox:latest").strip()

# container ichidagi path
RUNS_DIR = "/judge_runs"
# docker volume nomi (compose'dagi volumes: judge_runs:)
RUNS_VOLUME = os.getenv("JUDGE_RUNS_VOLUME", "judge_runs").strip()

TIMEOUT_SECONDS = int(os.getenv("JUDGE_TIMEOUT_SECONDS", "5"))


@dataclass
class RunResult:
    ok: bool
    stdout: str
    stderr: str
    timeout: bool


def _docker_cmd():
    return ["docker", "-H", DOCKER_HOST]


def run_in_sandbox(language: str, source_code: str, input_data: str) -> RunResult:
    run_id = str(uuid.uuid4())
    workdir = f"{RUNS_DIR}/{run_id}"

    # 1) Fayllarni yozish: buni web konteynerning /judge_runs ichiga yozamiz.
    os.makedirs(workdir, exist_ok=True)

    if language == "py":
        filename = "main.py"
    elif language == "c":
        filename = "main.c"
    elif language == "cpp":
        filename = "main.cpp"
    else:
        return RunResult(False, "", "Unsupported language", False)

    with open(f"{workdir}/{filename}", "w", encoding="utf-8") as f:
        f.write(source_code)

    with open(f"{workdir}/input.txt", "w", encoding="utf-8") as f:
        f.write(input_data or "")

    # 2) Container ichida run command
    if language == "py":
        run_cmd = f"python3 {filename} < input.txt"
    elif language == "c":
        run_cmd = f"gcc {filename} -O2 -pipe -static -s -o app && ./app < input.txt"
    else:  # cpp
        run_cmd = f"g++ {filename} -O2 -pipe -static -s -o app && ./app < input.txt"

    # 3) docker run: ABSOLUTE PATH emas, NAMED VOLUME bilan mount qilamiz
    cmd = _docker_cmd() + [
        "run",
        "--rm",
        "--network", "none",
        "-v", f"{RUNS_VOLUME}:{RUNS_DIR}",
        "-w", workdir,
        DOCKER_IMAGE,
        "sh", "-lc", run_cmd,
    ]

    try:
        p = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=TIMEOUT_SECONDS,
            text=True,
        )
        return RunResult(
            ok=(p.returncode == 0),
            stdout=p.stdout or "",
            stderr=p.stderr or "",
            timeout=False,
        )
    except subprocess.TimeoutExpired:
        return RunResult(False, "", "Time limit exceeded", True)
    finally:
        # cleanup: web konteynerning volume ichidan o'chiramiz
        subprocess.run(["sh", "-lc", f"rm -rf {workdir}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)