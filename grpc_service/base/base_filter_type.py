from enum import Enum


class StatusMessage(Enum):
    JOB_STARTED = "Job started"
    JOB_COMPLETED = "Job completed"
    JOB_CANCELLED = "Job cancelled"
    JOB_FAILED = "Job failed"
    JOB_NOT_FOUND = "Job Not Found"


class JobStatusCode(Enum):
    PENDING = 202
    IN_PROGRESS = 102
    COMPLETED = 200
    FAILED = 500
    CANCELLED = 410
    PAUSED = 425
    NOT_FOUND = 404

    def __str__(self):
        return self.name
