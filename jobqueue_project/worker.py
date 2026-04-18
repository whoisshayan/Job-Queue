import os
import sys
import time
import traceback
import uuid
from pathlib import Path

import django


BASE_DIR = Path(__file__).resolve().parent
WORKER_LOGS_DIR = BASE_DIR / "worker_logs"
POLL_INTERVAL_SECONDS = 3


def setup_django() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jobqueue_project.settings")
    django.setup()


setup_django()

from django.db import transaction
from django.utils import timezone

from jobqueue.jobs import get_job_callable
from jobqueue.models import JobExecution


def generate_worker_id() -> str:
    return f"worker_{uuid.uuid4().hex[:8]}"


def ensure_worker_logs_dir() -> Path:
    WORKER_LOGS_DIR.mkdir(parents=True, exist_ok=True)
    return WORKER_LOGS_DIR


def build_worker_log_path(worker_id: str) -> Path:
    ensure_worker_logs_dir()
    return WORKER_LOGS_DIR / f"{worker_id}.log"


def append_worker_log(
    log_path: Path,
    *,
    worker_id: str,
    execution_id: int,
    job_name: str,
    final_status: str,
    message: str,
) -> None:
    timestamp = timezone.now().isoformat()
    log_text = (
        f"[{timestamp}] "
        f"worker_id={worker_id} "
        f"job_execution_id={execution_id} "
        f"job_name={job_name} "
        f"status={final_status}\n"
        f"{message}\n"
        f"{'-' * 80}\n"
    )

    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(log_text)


def claim_next_execution(worker_id: str, log_path: Path):
    while True:
        with transaction.atomic():
            execution = (
                JobExecution.objects.select_related("job_definition")
                .filter(status=JobExecution.Status.PENDING)
                .order_by("created_at", "id")
                .first()
            )

            if execution is None:
                return None

            claim_time = timezone.now()
            updated_rows = JobExecution.objects.filter(
                pk=execution.pk,
                status=JobExecution.Status.PENDING,
            ).update(
                status=JobExecution.Status.RUNNING,
                start_time=claim_time,
                worker_id=worker_id,
                output_file_path=str(log_path),
                error="",
            )

            if updated_rows == 1:
                return JobExecution.objects.select_related("job_definition").get(pk=execution.pk)


def update_execution_after_run(
    execution: JobExecution,
    *,
    status: str,
    result: str,
    error: str,
) -> JobExecution:
    execution.end_time = timezone.now()

    if execution.start_time is not None:
        execution.duration = execution.end_time - execution.start_time

    execution.status = status
    execution.result = result
    execution.error = error
    execution.save(
        update_fields={
            "status",
            "result",
            "error",
            "end_time",
            "duration",
        }
    )
    return execution


def handle_unknown_job_type(execution: JobExecution, worker_id: str, log_path: Path) -> None:
    error_message = f"Unknown job type: {execution.job_definition.name}"
    append_worker_log(
        log_path,
        worker_id=worker_id,
        execution_id=execution.pk,
        job_name=execution.job_name_snapshot,
        final_status=JobExecution.Status.FAILED,
        message=error_message,
    )
    update_execution_after_run(
        execution,
        status=JobExecution.Status.FAILED,
        result="error",
        error=error_message,
    )


def run_execution(execution: JobExecution, worker_id: str, log_path: Path) -> None:
    job_name = execution.job_definition.name
    job_callable = get_job_callable(job_name)

    print(
        f"[{worker_id}] picked execution {execution.pk} "
        f"for job '{execution.job_name_snapshot}'"
    )

    if job_callable is None:
        handle_unknown_job_type(execution, worker_id, log_path)
        print(f"[{worker_id}] execution {execution.pk} failed: unknown job type")
        return

    try:
        output = job_callable(execution)
        output_text = "" if output is None else str(output)

        append_worker_log(
            log_path,
            worker_id=worker_id,
            execution_id=execution.pk,
            job_name=execution.job_name_snapshot,
            final_status=JobExecution.Status.COMPLETED,
            message=output_text or "Job completed without output.",
        )

        update_execution_after_run(
            execution,
            status=JobExecution.Status.COMPLETED,
            result="done",
            error="",
        )
        print(f"[{worker_id}] execution {execution.pk} completed")
    except Exception as exc:
        error_message = f"{type(exc).__name__}: {exc}"
        traceback_text = traceback.format_exc()

        append_worker_log(
            log_path,
            worker_id=worker_id,
            execution_id=execution.pk,
            job_name=execution.job_name_snapshot,
            final_status=JobExecution.Status.FAILED,
            message=f"{error_message}\n{traceback_text}",
        )

        update_execution_after_run(
            execution,
            status=JobExecution.Status.FAILED,
            result="error",
            error=error_message,
        )
        print(f"[{worker_id}] execution {execution.pk} failed: {error_message}")


def worker_loop() -> int:
    worker_id = generate_worker_id()
    log_path = build_worker_log_path(worker_id)

    print(f"Worker started: {worker_id}")
    print(f"Worker log file: {log_path}")

    while True:
        execution = claim_next_execution(worker_id, log_path)

        if execution is None:
            print(f"[{worker_id}] no pending jobs found, sleeping for {POLL_INTERVAL_SECONDS}s")
            time.sleep(POLL_INTERVAL_SECONDS)
            continue

        run_execution(execution, worker_id, log_path)


if __name__ == "__main__":
    try:
        worker_loop()
    except KeyboardInterrupt:
        print("\nWorker stopped by user.")
        sys.exit(0)
