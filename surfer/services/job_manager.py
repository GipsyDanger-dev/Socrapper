"""Job store for long-running surf jobs.

Jobs (progress events + final result) live in Django's cache framework. With
the default LocMemCache the store is per-process — fine for `runserver` and a
single gunicorn worker. If production ever runs multiple gunicorn workers,
point CACHES at a shared backend (e.g. Redis) and the store becomes shared
automatically.
"""

import json
import time
import uuid

from django.core.cache import cache

JOB_PREFIX = "surf_job:"
JOB_TTL = 600  # 10 minutes — surf requests can take minutes on free engines


def _key(job_id):
    return JOB_PREFIX + job_id


class JobManager:
    """Create, update and read surf jobs by id."""

    def create(self, job_type):
        job_id = uuid.uuid4().hex[:16]
        job = {
            "id": job_id,
            "type": job_type,
            "status": "running",  # running | done | error
            "events": [],
            "result": None,
            "error": None,
            "created_at": time.time(),
        }
        cache.set(_key(job_id), job, JOB_TTL)
        return job_id

    def emit(self, job_id, stage, message, data=None):
        # Single-writer assumption: only the job's own worker thread emits, so
        # the get→append→set sequence cannot lose events in practice. SSE
        # readers only call get(), which is safe.
        job = cache.get(_key(job_id))
        if job is None:
            return
        job["events"].append({"stage": stage, "message": message, "data": data})
        cache.set(_key(job_id), job, JOB_TTL)

    def finish(self, job_id, result):
        job = cache.get(_key(job_id))
        if job is None:
            return
        job["result"] = result
        job["status"] = "done"
        cache.set(_key(job_id), job, JOB_TTL)

    def fail(self, job_id, error):
        job = cache.get(_key(job_id))
        if job is None:
            return
        job["error"] = error
        job["status"] = "error"
        cache.set(_key(job_id), job, JOB_TTL)

    def get(self, job_id):
        job = cache.get(_key(job_id))
        if job is None:
            return None
        # Deep-copy so callers cannot mutate the stored job.
        return json.loads(json.dumps(job))


job_manager = JobManager()
