import random
from typing import Dict, Tuple

import pandas as pd
import simpy


def _service_time(mean_minutes: float) -> float:
    mean_minutes = max(float(mean_minutes), 0.1)
    return max(0.1, random.expovariate(1.0 / mean_minutes))


def run_operations_simulation(
    referrals_per_day: int = 400,
    shift_hours: float = 8,
    target_hours: float = 48,
    prior_auth_rate: float = 60,
    seed: int = 42,
    staff: Dict[str, int] | None = None,
    service_times: Dict[str, float] | None = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, dict]:

    random.seed(seed)

    staff = staff or {
        "intake": 5,
        "benefits": 6,
        "prior_auth": 4,
        "pharmacy_review": 3,
        "fulfillment": 8,
        "delivery": 4,
    }

    service_times = service_times or {
        "intake": 5,
        "benefits": 12,
        "prior_auth": 25,
        "pharmacy_review": 15,
        "fulfillment": 18,
        "delivery": 10,
    }

    env = simpy.Environment()
    resources = {
        step: simpy.Resource(env, capacity=max(1, int(capacity)))
        for step, capacity in staff.items()
    }

    step_records = []
    case_records = []
    busy_minutes = {step: 0.0 for step in staff.keys()}

    def case_flow(case_id: int):
        arrival_time = env.now

        steps = [
            ("intake", "Intake"),
            ("benefits", "Benefits Verification"),
            ("pharmacy_review", "Pharmacy Review"),
            ("fulfillment", "Medication Fulfillment"),
            ("delivery", "Delivery / Infusion Coordination"),
        ]

        if random.random() < prior_auth_rate / 100:
            steps.insert(2, ("prior_auth", "Prior Authorization"))

        for step_key, step_name in steps:
            queue_enter = env.now

            with resources[step_key].request() as request:
                yield request

                service_start = env.now
                queue_wait = service_start - queue_enter

                service_duration = _service_time(service_times[step_key])
                busy_minutes[step_key] += service_duration

                yield env.timeout(service_duration)

                service_end = env.now

                step_records.append({
                    "case_id": case_id,
                    "step_key": step_key,
                    "step": step_name,
                    "queue_enter_minute": queue_enter,
                    "service_start_minute": service_start,
                    "service_end_minute": service_end,
                    "queue_wait_minutes": queue_wait,
                    "service_minutes": service_duration,
                })

        completed_time = env.now
        cycle_time = completed_time - arrival_time

        case_records.append({
            "case_id": case_id,
            "arrival_minute": arrival_time,
            "completed_minute": completed_time,
            "cycle_time_minutes": cycle_time,
            "cycle_time_hours": cycle_time / 60,
            "completed_within_target": cycle_time <= target_hours * 60,
            "finished_after_shift": completed_time > shift_hours * 60,
        })

    def arrival_generator():
        if referrals_per_day <= 0:
            return

        arrival_window_minutes = shift_hours * 60
        avg_interarrival_minutes = arrival_window_minutes / referrals_per_day

        for case_id in range(1, referrals_per_day + 1):
            env.process(case_flow(case_id))

            if case_id < referrals_per_day:
                yield env.timeout(
                    random.expovariate(1.0 / avg_interarrival_minutes)
                )

    env.process(arrival_generator())
    env.run()

    case_df = pd.DataFrame(case_records)
    step_df = pd.DataFrame(step_records)

    if case_df.empty or step_df.empty:
        return case_df, pd.DataFrame(), {}

    step_summary = (
        step_df.groupby(["step_key", "step"])
        .agg(
            cases=("case_id", "count"),
            avg_queue_wait_minutes=("queue_wait_minutes", "mean"),
            avg_service_minutes=("service_minutes", "mean"),
            total_busy_minutes=("service_minutes", "sum"),
        )
        .reset_index()
    )

    step_summary["staff"] = step_summary["step_key"].map(staff)
    step_summary["utilization_pct"] = (
        step_summary["total_busy_minutes"]
        / (step_summary["staff"] * shift_hours * 60)
        * 100
    )

    for col in [
        "avg_queue_wait_minutes",
        "avg_service_minutes",
        "total_busy_minutes",
        "utilization_pct",
    ]:
        step_summary[col] = step_summary[col].round(2)

    total_wait_by_case = (
        step_df.groupby("case_id")["queue_wait_minutes"].sum().mean()
    )

    bottleneck_row = step_summary.sort_values(
        ["utilization_pct", "avg_queue_wait_minutes"],
        ascending=False
    ).iloc[0]

    summary = {
        "completed_cases": int(len(case_df)),
        "avg_cycle_time_hours": round(case_df["cycle_time_hours"].mean(), 2),
        "avg_total_wait_minutes": round(total_wait_by_case, 2),
        "sla_compliance_pct": round(case_df["completed_within_target"].mean() * 100, 2),
        "finished_after_shift_cases": int(case_df["finished_after_shift"].sum()),
        "bottleneck": bottleneck_row["step"],
        "max_utilization_pct": round(float(bottleneck_row["utilization_pct"]), 2),
    }

    return case_df, step_summary, summary