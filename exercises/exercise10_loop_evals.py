"""
Exercise 10 -- loop-level metrics: aggregate (corresponds to Lesson 10)
========================================================================
run_task is provided. You need to implement aggregate(): summarize a batch of per-task
results into four loop-level metrics.

Spec for aggregate(records) you must implement -- records is [{status, iters, cost}, ...] -- returns a dict:
  - success_rate    : SUCCESS count / total count, rounded to 2 decimal places
  - mean_iters      : average iters for SUCCESS records only, rounded to 1 decimal place (0.0 if no SUCCESS)
  - escalation_rate : ESCALATED count / total count, rounded to 2 decimal places
  - mean_cost       : average cost across all records, rounded to 1 decimal place

Run the autograder when done:
    python3 check_exercise10.py
"""

COST_PER_ITER = 100


def run_task(difficulty, max_iters):
    """[Provided] If the task can be solved within 'difficulty' rounds it is SUCCESS; otherwise ESCALATED."""
    if difficulty <= max_iters:
        return {"status": "SUCCESS", "iters": difficulty, "cost": difficulty * COST_PER_ITER}
    return {"status": "ESCALATED", "iters": max_iters, "cost": max_iters * COST_PER_ITER}


def aggregate(records):
    # ===================================================================
    # TODO: return {success_rate, mean_iters, escalation_rate, mean_cost} (see spec above)
    # ===================================================================
    raise NotImplementedError("implement your aggregate()")
