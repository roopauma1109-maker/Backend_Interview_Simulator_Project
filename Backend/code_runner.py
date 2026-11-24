
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from database import SessionLocal
from models import User, CodeSubmission


router = APIRouter()

MAX_CODE_LENGTH = 10000
MAX_INPUT_LENGTH = 5000
MAX_OUTPUT_LENGTH = 10000
EXECUTION_TIMEOUT = 8
MAX_TEST_CASES = 10

LANGUAGES = {
    "python": {
        "image": "python:3.12-slim",
        "filename": "main.py",
        "command": ["python", "-I", "/workspace/main.py"],
    },
    "java": {
        "image": "eclipse-temurin:21-jdk",
        "filename": "Main.java",
        "command": [
            "sh", "-c",
            "javac -d /tmp /workspace/Main.java 2>&1; "
            "compile_status=$?; "
            "if [ $compile_status -ne 0 ]; then exit 100; fi; "
            "java -cp /tmp Main"
        ],
    },
    "cpp": {
        "image": "gcc:14",
        "filename": "main.cpp",
        "command": [
            "sh", "-c",
            "g++ -std=c++17 -O0 /workspace/main.cpp -o /tmp/main 2>&1; "
            "compile_status=$?; "
            "if [ $compile_status -ne 0 ]; then exit 100; fi; "
            "/tmp/main"
        ],
    },
}


class TestCase(BaseModel):
    input: str = Field(default="", max_length=MAX_INPUT_LENGTH)
    expected_output: str = Field(max_length=MAX_OUTPUT_LENGTH)


class CodeRequest(BaseModel):
    user_id: Optional[int] = None

    language: str
    code: str = Field(min_length=1, max_length=MAX_CODE_LENGTH)
    input: str = Field(default="", max_length=MAX_INPUT_LENGTH)

    expected_output: Optional[str] = Field(
        default=None,
        max_length=MAX_OUTPUT_LENGTH
    )

    test_cases: list[TestCase] = Field(
        default_factory=list,
        max_length=MAX_TEST_CASES
    )


def normalize_output(value: str) -> str:
    return value.strip()


def execute_code(language, code, test_input):
    config = LANGUAGES[language]
    container_name = f"interview-runner-{uuid.uuid4().hex[:12]}"

    with tempfile.TemporaryDirectory(prefix="interview_code_") as temp:
        workdir = Path(temp)
        source_file = workdir / config["filename"]
        source_file.write_text(code, encoding="utf-8")

        command = [
            "docker", "run",
            "-i",
            "--name", container_name,
            "--network", "none",
            "--memory", "256m",
            "--cpus", "1",
            "--pids-limit", "64",
            "--read-only",
            "--tmpfs", "/tmp:rw,nosuid,nodev,size=64m",
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges",
            "--mount",
            f"type=bind,source={workdir.resolve()},target=/workspace,readonly",
            config["image"],
            *config["command"],
        ]

        try:
            result = subprocess.run(
                command,
                input=test_input,
                capture_output=True,
                text=True,
                timeout=EXECUTION_TIMEOUT,
                encoding="utf-8",
                errors="replace",
            )

            output = result.stdout[-MAX_OUTPUT_LENGTH:]
            error = result.stderr[-MAX_OUTPUT_LENGTH:]

            if language == "python" and "SyntaxError" in error:
                verdict = "Compilation Error"

            elif result.returncode == 100:
                verdict = "Compilation Error"
                error = error or output or "Compilation failed."

            elif result.returncode != 0:
                verdict = "Runtime Error"

            else:
                verdict = "Executed"

            return {
                "verdict": verdict,
                "output": output,
                "error": error,
            }

        except subprocess.TimeoutExpired:
            return {
                "verdict": "Time Limit Exceeded",
                "output": "",
                "error": "Execution timed out (8 seconds).",
            }

        finally:
            subprocess.run(
                ["docker", "rm", "-f", container_name],
                capture_output=True,
                timeout=5,
            )


def save_submission(
    user_id,
    language,
    code,
    verdict,
    total_count,
    passed_count,
    failed_count,
):
    db = SessionLocal()

    try:
        if user_id is not None:
            user = db.query(User).filter(
                User.id == user_id
            ).first()

            if not user:
                raise HTTPException(
                    status_code=404,
                    detail="User not found."
                )

        submission = CodeSubmission(
            user_id=user_id,
            language=language,
            code=code,
            verdict=verdict,
            total_test_cases=total_count,
            passed_test_cases=passed_count,
            failed_test_cases=failed_count,
        )

        db.add(submission)
        db.commit()
        db.refresh(submission)

        return submission.id

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


@router.post("/coding/run")
def run_code(request: CodeRequest):
    language = request.language.lower()

    if language not in LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported language. Use python, java, or cpp."
        )

    # Validate user before executing code
    if request.user_id is not None:
        db = SessionLocal()

        try:
            user = db.query(User).filter(
                User.id == request.user_id
            ).first()

            if not user:
                raise HTTPException(
                    status_code=404,
                    detail="User not found."
                )
        finally:
            db.close()

    if request.test_cases:
        cases = request.test_cases
    else:
        cases = [{
            "input": request.input,
            "expected_output": request.expected_output,
        }]

    results = []
    passed_count = 0
    failed_count = 0

    try:
        for index, case in enumerate(cases, start=1):

            if isinstance(case, TestCase):
                test_input = case.input
                expected = case.expected_output
            else:
                test_input = case["input"]
                expected = case["expected_output"]

            result = execute_code(
                language,
                request.code,
                test_input
            )

            verdict = result["verdict"]

            if verdict == "Executed":
                if expected is None:
                    verdict = "Executed"

                elif (
                    normalize_output(result["output"])
                    == normalize_output(expected)
                ):
                    verdict = "Accepted"

                else:
                    verdict = "Wrong Answer"

            if verdict == "Accepted":
                passed_count += 1
            else:
                failed_count += 1

            results.append({
                "test_case": index,
                "verdict": verdict,
                "input": test_input,
                "expected_output": expected,
                "output": result["output"],
                "error": result["error"],
            })

            if verdict in [
                "Compilation Error",
                "Runtime Error",
                "Time Limit Exceeded",
            ]:
                break

        if len(results) == 1 and results[0]["verdict"] == "Executed":
            overall_verdict = "Executed"

        elif failed_count == 0 and len(results) == len(cases):
            overall_verdict = "Accepted"

        else:
            overall_verdict = next(
                (
                    item["verdict"]
                    for item in results
                    if item["verdict"] != "Accepted"
                ),
                "Wrong Answer",
            )

        # Save submission in database
        submission_id = save_submission(
            user_id=request.user_id,
            language=language,
            code=request.code,
            verdict=overall_verdict,
            total_count=len(cases),
            passed_count=passed_count,
            failed_count=failed_count,
        )

        return {
            "status": "success",
            "submission_id": submission_id,
            "verdict": overall_verdict,
            "passed_count": passed_count,
            "failed_count": failed_count,
            "total_test_cases": len(cases),
            "output": results[0]["output"] if results else "",
            "error": results[0]["error"] if results else "",
            "test_results": results,
        }

    except HTTPException:
        raise

    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="Docker CLI was not found."
        )

    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=500,
            detail="Docker cleanup timed out."
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Code execution failed: {str(error)}"
        )