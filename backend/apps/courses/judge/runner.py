import os
import subprocess
import tempfile
import uuid
from dataclasses import dataclass

DOCKER_HOST = os.getenv("DOCKER_HOST", "tcp://dind:2375").strip()
DOCKER_IMAGE = os.getenv("JUDGE_IMAGE", "judge-sandbox:latest")

# judge_runs volume siz compose'da bergan:
RUNS_DIR = "/judge_runs"


@dataclass
class RunResult:
    ok: bool
    stdout: str
    stderr: str
    timeout: bool


def _docker_cmd():
    """
    Always connect to dind daemon
    """
    return ["docker", "-H", DOCKER_HOST]


def run_in_sandbox(language: str, source_code: str, input_data: str) -> RunResult:

    run_id = str(uuid.uuid4())
    workdir = os.path.join(RUNS_DIR, run_id)

    os.makedirs(workdir, exist_ok=True)

    try:

        # =====================
        # 1. write source file
        # =====================

        if language == "py":
            filename = "main.py"

        elif language == "c":
            filename = "main.c"

        elif language == "cpp":
            filename = "main.cpp"

        else:
            return RunResult(False, "", "Unsupported language", False)

        source_path = os.path.join(workdir, filename)

        with open(source_path, "w") as f:
            f.write(source_code)

        input_path = os.path.join(workdir, "input.txt")

        with open(input_path, "w") as f:
            f.write(input_data)

        # =====================
        # 2. build command inside container
        # =====================

        if language == "py":

            run_cmd = f"python {filename} < input.txt"

        elif language == "c":

            run_cmd = f"gcc {filename} -o app && ./app < input.txt"

        elif language == "cpp":

            run_cmd = f"g++ {filename} -o app && ./app < input.txt"

        # =====================
        # 3. docker run command
        # =====================

        cmd = _docker_cmd() + [

            "run",

            "--rm",

            "--network", "none",

            "-v", f"{RUNS_DIR}:{RUNS_DIR}",

            "-w", workdir,

            DOCKER_IMAGE,

            "sh",

            "-c",

            run_cmd

        ]

        try:

            p = subprocess.run(

                cmd,

                stdout=subprocess.PIPE,

                stderr=subprocess.PIPE,

                timeout=5,

                text=True

            )

            return RunResult(

                ok=(p.returncode == 0),

                stdout=p.stdout,

                stderr=p.stderr,

                timeout=False

            )

        except subprocess.TimeoutExpired as e:

            return RunResult(

                ok=False,

                stdout="",

                stderr="Time limit exceeded",

                timeout=True

            )

    finally:

        # clean files
        try:
            subprocess.run(["rm", "-rf", workdir])
        except:
            pass