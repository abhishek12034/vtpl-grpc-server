from enum import Enum


class StatusMessage(Enum):
    JOB_STARTED = "Job started"
    JOB_COMPLETED = "Job completed"
    JOB_CANCELLED = "Job cancelled"
    JOB_FAILED = "Job failed"
    JOB_NOT_FOUND = "Job Not Found"
