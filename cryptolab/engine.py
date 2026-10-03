"""Evaluate bounded synthetic difficulty retargets using epoch duration, clamping and work estimates."""

from .common import (
    number,
    integer,
    identity,
    records,
    chronology,
    allocate,
    result,
    validate_document,
)
from decimal import Decimal


def _analyze(d):
    target_time = integer(d["target_seconds"], 1)
    blocks = integer(d["epoch_blocks"], 1)
    difficulty = number(d["initial_difficulty"], minimum="0.000000000000000001")
    clamp = number(d["clamp_factor"], minimum=1)
    target = target_time * blocks
    trace = []
    for epoch in records(d["epochs"], "id"):
        elapsed = integer(epoch["elapsed_seconds"], 1)
        ratio = number(target) / elapsed
        bounded = min(clamp, max(1 / clamp, ratio))
        old = difficulty
        difficulty *= bounded
        trace.append(
            {
                "id": epoch["id"],
                "observed_ratio": ratio,
                "applied_ratio": bounded,
                "old_difficulty": old,
                "new_difficulty": difficulty,
                "clamped": ratio != bounded,
            }
        )
    return result(
        {"final_difficulty": difficulty, "trace": trace, "target_epoch_seconds": target}
    )


def analyze(document):
    validate_document(document)
    try:
        return result(_analyze(document))
    except (KeyError, TypeError, ArithmeticError, RecursionError) as error:
        raise ValueError("invalid domain input: " + str(error)) from error
