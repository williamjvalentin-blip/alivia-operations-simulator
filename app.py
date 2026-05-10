
import pandas as pd
import plotly.express as px
import streamlit as st

from simulation import run_operations_simulation


st.set_page_config(
    page_title="Alivia-style Operations Simulator",
    layout="wide",
)

st.title("Alivia-style Specialty Pharmacy Operations Simulator")

st.write(
    "Synthetic simulation demo for specialty pharmacy / healthcare operations. "
    "This model estimates bottlenecks, staffing pressure, wait time, cycle time, "
    "SLA risk, staffing optimization, and improvement scenarios. It uses fake data only."
)

PROCESS_LABELS = {
    "intake": "Intake",
    "benefits": "Benefits Verification",
    "prior_auth": "Prior Authorization",
    "pharmacy_review": "Pharmacy Review",
    "fulfillment": "Medication Fulfillment",
    "delivery": "Delivery / Infusion Coordination",
}

PROCESS_KEYS = list(PROCESS_LABELS.keys())
LABEL_TO_KEY = {label: key for key, label in PROCESS_LABELS.items()}


def run_model(referrals, shift_hours, target_hours, prior_auth_rate, seed, staff, service_times):
    result = run_operations_simulation(
        referrals_per_day=referrals,
        shift_hours=shift_hours,
        target_hours=target_hours,
        prior_auth_rate=prior_auth_rate,
        seed=seed,
        staff=staff,
        service_times=service_times,
    )

    if len(result) == 4:
        case_df, step_df, step_summary, summary = result
    else:
        case_df, step_summary, summary = result
        step_df = pd.DataFrame()

    return case_df, step_df, step_summary, summary


def build_process_animation(step_df, max_cases=80):
    if step_df is None or step_df.empty:
        return None

    animation_df = step_df.copy()
    sample_cases = animation_df["case_id"].drop_duplicates().head(max_cases)
    animation_df = animation_df[animation_df["case_id"].isin(sample_cases)].copy()

    step_order = {
        "Intake": 1,
        "Benefits Verification": 2,
        "Prior Authorization": 3,
        "Pharmacy Review": 4,
        "Medication Fulfillment": 5,
        "Delivery / Infusion Coordination": 6,
    }

    animation_df["step_position"] = animation_df["step"].map(step_order)
    animation_df = animation_df.dropna(subset=["step_position"])
    animation_df["time_bucket"] = (animation_df["service_start_minute"] // 30 * 30).astype(int)
    animation_df["case_index"] = animation_df["case_id"].rank(method="dense").astype(int)
    animation_df["queue_wait_minutes"] = animation_df["queue_wait_minutes"].round(2)
    animation_df["service_minutes"] = animation_df["service_minutes"].round(2)
    animation_df["marker_size"] = animation_df["queue_wait_minutes"].clip(lower=3, upper=60)

    fig = px.scatter(
        animation_df,
        x="step_position",
        y="case_index",
        animation_frame="time_bucket",
        color="step",
        size="marker_size",
        size_max=35,
        hover_data={
            "case_id": True,
            "step": True,
            "queue_wait_minutes": True,
            "service_minutes": True,
            "step_position": False,
            "case_index": False,
            "marker_size": False,
        },
        title="Animated Case Flow Through the Process",
        range_x=[0.5, 6.5],
    )

    fig.update_layout(
        height=600,
        xaxis=dict(
            tickmode="array",
            tickvals=list(step_order.values()),
            ticktext=list(step_order.keys()),
            title="Process Step",
        ),
        yaxis_title="Sampled Case",
    )

    return fig


def scenario_row(scenario_name, referrals, scenario_staff, scenario_service_times,
                 shift_hours, target_hours, prior_auth_rate, seed):
    _, _, _, summary = run_model(
        referrals=referrals,
        shift_hours=shift_hours,
        target_hours=target_hours,
        prior_auth_rate=prior_auth_rate,
        seed=seed,
        staff=scenario_staff,
        service_times=scenario_service_times,
    )

    return {
        "Scenario": scenario_name,
        "Completed Cases": summary.get("completed_cases", 0),
        "Avg Cycle Time Hours": summary.get("avg_cycle_time_hours", 0),
        "Avg Total Wait Minutes": summary.get("avg_total_wait_minutes", 0),
        "SLA Compliance %": summary.get("sla_compliance_pct", 0),
        "Finished After Shift": summary.get("finished_after_shift_cases", 0),
        "Bottleneck": summary.get("bottleneck", "N/A"),
        "Max Utilization %": summary.get("max_utilization_pct", 0),
    }


def total_staff(staff_dict):
    return int(sum(int(value) for value in staff_dict.values()))


def step_utilization_by_key(step_summary):
    util_by_key = {}

    if step_summary is None or step_summary.empty:
        return util_by_key

    for _, row in step_summary.iterrows():
        label = row["step"]
        key = LABEL_TO_KEY.get(label)
        if key:
            util_by_key[key] = float(row["utilization_pct"])

    return util_by_key


def stations_above_target(step_summary, target_max_util, allowed_steps):
    util_by_key = step_utilization_by_key(step_summary)
    return [
        key for key in allowed_steps
        if util_by_key.get(key, 0) > target_max_util
    ]


def underutilization_penalty(step_summary, candidate_staff, base_staff, min_util_floor):
    """
    Penalizes adding staff to a station if the added staff pushes that station
    below the minimum utilization floor.

    This prevents unreasonable recommendations like reducing Intake utilization
    to 40% while other stations are still overloaded.
    """
    util_by_key = step_utilization_by_key(step_summary)
    penalty = 0.0

    for key in PROCESS_KEYS:
        staff_added = candidate_staff[key] > base_staff[key]
        util = util_by_key.get(key, 0)

        if staff_added and util < min_util_floor:
            penalty += (min_util_floor - util)

    return penalty


def objective_weights(objective, staff_cost_penalty):
    staff_penalty_map = {
        "Low": 5,
        "Medium": 15,
        "High": 30,
    }

    staff_weight = staff_penalty_map[staff_cost_penalty]

    if objective == "Meet SLA with minimum staff":
        return {
            "sla": 160,
            "util_above": 30,
            "underutil": 35,
            "after_shift": 4,
            "staff": staff_weight * 1.6,
            "wait": 0.02,
            "cycle": 0.05,
        }

    if objective == "Reduce cycle time":
        return {
            "sla": 80,
            "util_above": 25,
            "underutil": 55,
            "after_shift": 2,
            "staff": staff_weight * 1.4,
            "wait": 0.08,
            "cycle": 6.0,
        }

    # Balanced default.
    return {
        "sla": 120,
        "util_above": 35,
        "underutil": 45,
        "after_shift": 3,
        "staff": staff_weight,
        "wait": 0.05,
        "cycle": 1.0,
    }


def meets_targets(summary, objective, target_sla, target_max_util, max_after_shift, target_cycle_hours):
    base_targets = (
        summary["sla_compliance_pct"] >= target_sla
        and summary["max_utilization_pct"] <= target_max_util
        and summary["finished_after_shift_cases"] <= max_after_shift
    )

    if objective == "Reduce cycle time":
        return base_targets and summary["avg_cycle_time_hours"] <= target_cycle_hours

    return base_targets


def optimizer_score(
    summary,
    candidate_staff,
    base_staff,
    base_total_staff,
    target_sla,
    target_max_util,
    target_cycle_hours,
    objective,
    staff_cost_penalty,
    min_util_floor,
    candidate_step_summary,
):
    weights = objective_weights(objective, staff_cost_penalty)

    sla_gap = max(0, target_sla - summary["sla_compliance_pct"])
    util_gap = max(0, summary["max_utilization_pct"] - target_max_util)
    cycle_gap = max(0, summary["avg_cycle_time_hours"] - target_cycle_hours)
    after_shift = summary["finished_after_shift_cases"]
    extra_staff = total_staff(candidate_staff) - base_total_staff
    avg_wait = summary["avg_total_wait_minutes"]
    avg_cycle = summary["avg_cycle_time_hours"]
    underutil_gap = underutilization_penalty(
        candidate_step_summary,
        candidate_staff,
        base_staff,
        min_util_floor,
    )

    return round(
        sla_gap * weights["sla"]
        + util_gap * weights["util_above"]
        + cycle_gap * weights["cycle"]
        + after_shift * weights["after_shift"]
        + extra_staff * weights["staff"]
        + avg_wait * weights["wait"]
        + avg_cycle * 0.10
        + underutil_gap * weights["underutil"],
        2,
    )


def optimize_staffing(
    referrals,
    shift_hours,
    target_hours,
    prior_auth_rate,
    seed,
    base_staff,
    service_times,
    target_sla,
    target_max_util,
    min_util_floor,
    max_after_shift,
    max_extra_staff,
    allowed_steps,
    objective,
    target_cycle_hours,
    staff_cost_penalty,
):
    current_staff = base_staff.copy()
    base_total = total_staff(base_staff)
    rejected_actions = []

    _, _, current_step_summary, current_summary = run_model(
        referrals=referrals,
        shift_hours=shift_hours,
        target_hours=target_hours,
        prior_auth_rate=prior_auth_rate,
        seed=seed,
        staff=current_staff,
        service_times=service_times,
    )

    history = []

    def add_history(iteration, action, staff_snapshot, summary_snapshot, step_summary_snapshot):
        row = {
            "Iteration": iteration,
            "Action": action,
            "Total Staff": total_staff(staff_snapshot),
            "Extra Staff": total_staff(staff_snapshot) - base_total,
            "SLA Compliance %": summary_snapshot["sla_compliance_pct"],
            "Max Utilization %": summary_snapshot["max_utilization_pct"],
            "Finished After Shift": summary_snapshot["finished_after_shift_cases"],
            "Avg Wait Minutes": summary_snapshot["avg_total_wait_minutes"],
            "Avg Cycle Hours": summary_snapshot["avg_cycle_time_hours"],
            "Bottleneck": summary_snapshot["bottleneck"],
            "Score": optimizer_score(
                summary_snapshot,
                staff_snapshot,
                base_staff,
                base_total,
                target_sla,
                target_max_util,
                target_cycle_hours,
                objective,
                staff_cost_penalty,
                min_util_floor,
                step_summary_snapshot,
            ),
        }

        for key in PROCESS_KEYS:
            row[f"Staff - {PROCESS_LABELS[key]}"] = staff_snapshot[key]

        history.append(row)

    add_history(0, "Current staffing", current_staff.copy(), current_summary, current_step_summary)

    if meets_targets(current_summary, objective, target_sla, target_max_util, max_after_shift, target_cycle_hours):
        return (
            pd.DataFrame(history),
            current_staff,
            current_summary,
            current_step_summary,
            "Current staffing already meets the selected targets.",
            pd.DataFrame(rejected_actions),
        )

    for iteration in range(1, int(max_extra_staff) + 1):
        overloaded_steps = stations_above_target(
            current_step_summary,
            target_max_util,
            allowed_steps,
        )

        if overloaded_steps:
            candidate_steps = overloaded_steps
        else:
            candidate_steps = allowed_steps

        candidates = []

        for step in candidate_steps:
            candidate_staff = current_staff.copy()
            candidate_staff[step] += 1

            _, _, candidate_step_summary, candidate_summary = run_model(
                referrals=referrals,
                shift_hours=shift_hours,
                target_hours=target_hours,
                prior_auth_rate=prior_auth_rate,
                seed=seed,
                staff=candidate_staff,
                service_times=service_times,
            )

            util_by_key = step_utilization_by_key(candidate_step_summary)
            changed_step_util = util_by_key.get(step, 0)

            if changed_step_util < min_util_floor:
                rejected_actions.append(
                    {
                        "Iteration": iteration,
                        "Rejected Action": f"Add 1 staff to {PROCESS_LABELS[step]}",
                        "Reason": (
                            f"Projected utilization would drop to {round(changed_step_util, 2)}%, "
                            f"below the minimum floor of {min_util_floor}%."
                        ),
                    }
                )
                continue

            candidates.append(
                {
                    "step": step,
                    "staff": candidate_staff,
                    "summary": candidate_summary,
                    "step_summary": candidate_step_summary,
                    "score": optimizer_score(
                        candidate_summary,
                        candidate_staff,
                        base_staff,
                        base_total,
                        target_sla,
                        target_max_util,
                        target_cycle_hours,
                        objective,
                        staff_cost_penalty,
                        min_util_floor,
                        candidate_step_summary,
                    ),
                }
            )

        if not candidates:
            return (
                pd.DataFrame(history),
                current_staff,
                current_summary,
                current_step_summary,
                (
                    "Optimizer stopped because all available staffing additions would violate "
                    "the minimum utilization floor. Try lowering the minimum utilization floor, "
                    "allowing different stations, or using process-time improvements."
                ),
                pd.DataFrame(rejected_actions),
            )

        best = sorted(candidates, key=lambda item: item["score"])[0]
        current_staff = best["staff"]
        current_summary = best["summary"]
        current_step_summary = best["step_summary"]

        add_history(
            iteration,
            f"Add 1 staff to {PROCESS_LABELS[best['step']]}",
            current_staff.copy(),
            current_summary,
            current_step_summary,
        )

        if meets_targets(current_summary, objective, target_sla, target_max_util, max_after_shift, target_cycle_hours):
            return (
                pd.DataFrame(history),
                current_staff,
                current_summary,
                current_step_summary,
                f"Target reached after adding {iteration} staff member(s).",
                pd.DataFrame(rejected_actions),
            )

    return (
        pd.DataFrame(history),
        current_staff,
        current_summary,
        current_step_summary,
        f"Target not fully reached within max extra staff limit of {max_extra_staff}. Use the best iteration shown.",
        pd.DataFrame(rejected_actions),
    )


def staffing_result_table(current_staff, recommended_staff):
    return pd.DataFrame(
        [
            {
                "Station": PROCESS_LABELS[key],
                "Current Staff": current_staff[key],
                "Recommended Staff": recommended_staff[key],
                "Change": recommended_staff[key] - current_staff[key],
            }
            for key in PROCESS_KEYS
        ]
    )


def utilization_comparison_table(current_step_summary, recommended_step_summary):
    current_util = current_step_summary[["step", "utilization_pct"]].rename(
        columns={"utilization_pct": "Current Utilization %"}
    )

    recommended_util = recommended_step_summary[["step", "utilization_pct"]].rename(
        columns={"utilization_pct": "Recommended Utilization %"}
    )

    util_compare = current_util.merge(
        recommended_util,
        on="step",
        how="outer",
    ).fillna(0)

    util_compare = util_compare.rename(columns={"step": "Station"})

    return util_compare


if "simulation_ready" not in st.session_state:
    st.session_state["simulation_ready"] = False

st.sidebar.header("Simulation Inputs")

referrals_per_day = st.sidebar.slider("Referrals / prescriptions per day", 50, 1000, 400, 50)
shift_hours = st.sidebar.slider("Shift hours", 4, 24, 8, 1)
target_hours = st.sidebar.slider("Target completion time in hours", 4, 120, 48, 4)
prior_auth_rate = st.sidebar.slider("Percent requiring prior authorization", 0, 100, 60, 5)
seed = st.sidebar.number_input("Random seed", 1, 9999, 42)

st.sidebar.subheader("Staffing")

staff = {
    "intake": st.sidebar.number_input("Intake staff", 1, 50, 5),
    "benefits": st.sidebar.number_input("Benefits verification staff", 1, 50, 6),
    "prior_auth": st.sidebar.number_input("Prior authorization staff", 1, 50, 4),
    "pharmacy_review": st.sidebar.number_input("Pharmacy review staff", 1, 50, 3),
    "fulfillment": st.sidebar.number_input("Fulfillment staff", 1, 50, 8),
    "delivery": st.sidebar.number_input("Delivery coordination staff", 1, 50, 4),
}

st.sidebar.subheader("Average Service Time")

service_times = {
    "intake": st.sidebar.number_input("Intake minutes", 1, 120, 5),
    "benefits": st.sidebar.number_input("Benefits verification minutes", 1, 120, 12),
    "prior_auth": st.sidebar.number_input("Prior authorization minutes", 1, 240, 25),
    "pharmacy_review": st.sidebar.number_input("Pharmacy review minutes", 1, 120, 15),
    "fulfillment": st.sidebar.number_input("Fulfillment minutes", 1, 120, 18),
    "delivery": st.sidebar.number_input("Delivery coordination minutes", 1, 120, 10),
}

if st.button("Run Simulation"):
    st.session_state["simulation_ready"] = True

if st.session_state["simulation_ready"]:
    case_df, step_df, step_summary, summary = run_model(
        referrals=referrals_per_day,
        shift_hours=shift_hours,
        target_hours=target_hours,
        prior_auth_rate=prior_auth_rate,
        seed=seed,
        staff=staff,
        service_times=service_times,
    )

    if not summary:
        st.error("Simulation did not return results.")
        st.stop()

    st.subheader("Executive Summary")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Completed Cases", summary["completed_cases"])
    col2.metric("Avg Cycle Time", f"{summary['avg_cycle_time_hours']} hrs")
    col3.metric("SLA Compliance", f"{summary['sla_compliance_pct']}%")
    col4.metric("Bottleneck", summary["bottleneck"])

    col5, col6, col7 = st.columns(3)
    col5.metric("Avg Total Wait", f"{summary['avg_total_wait_minutes']} min")
    col6.metric("Max Utilization", f"{summary['max_utilization_pct']}%")
    col7.metric("Finished After Shift", summary["finished_after_shift_cases"])

    st.subheader("Operational Interpretation")

    if summary["max_utilization_pct"] >= 90:
        st.error(
            f"The operation is under heavy pressure. "
            f"The main bottleneck is {summary['bottleneck']} with "
            f"{summary['max_utilization_pct']}% utilization."
        )
    elif summary["max_utilization_pct"] >= 75:
        st.warning(f"The operation is moderately constrained. The main bottleneck is {summary['bottleneck']}.")
    else:
        st.success("The current staffing scenario appears stable under these assumptions.")

    if summary["sla_compliance_pct"] < 90:
        st.warning(
            "SLA compliance is below 90%. Test adding staff to the bottleneck "
            "or reducing service time in the bottleneck step."
        )

    tab_names = [
        "Bottleneck Analysis",
        "Cycle Time",
        "Scenario Comparison",
        "Optimization",
    ]

    if step_df is not None and not step_df.empty:
        tab_names.append("Live Process Flow")

    tab_names.append("Raw Data")

    tabs = st.tabs(tab_names)

    with tabs[0]:
        st.subheader("Step Summary")
        st.dataframe(step_summary, use_container_width=True)

        fig_util = px.bar(
            step_summary,
            x="step",
            y="utilization_pct",
            title="Utilization by Process Step",
            text="utilization_pct",
        )
        st.plotly_chart(fig_util, use_container_width=True)

        fig_wait = px.bar(
            step_summary,
            x="step",
            y="avg_queue_wait_minutes",
            title="Average Queue Wait by Step",
            text="avg_queue_wait_minutes",
        )
        st.plotly_chart(fig_wait, use_container_width=True)

    with tabs[1]:
        st.subheader("Cycle Time Distribution")

        fig_cycle = px.histogram(
            case_df,
            x="cycle_time_hours",
            nbins=40,
            title="Cycle Time Distribution in Hours",
        )
        st.plotly_chart(fig_cycle, use_container_width=True)

        fig_case = px.line(
            case_df.sort_values("case_id"),
            x="case_id",
            y="cycle_time_hours",
            title="Cycle Time by Case",
        )
        st.plotly_chart(fig_case, use_container_width=True)

    with tabs[2]:
        st.subheader("What-If Scenario Comparison")

        current_staff = staff.copy()
        current_times = service_times.copy()

        add_prior_auth_staff = staff.copy()
        add_prior_auth_staff["prior_auth"] += 1

        add_benefits_staff = staff.copy()
        add_benefits_staff["benefits"] += 1

        reduce_prior_auth_time = service_times.copy()
        reduce_prior_auth_time["prior_auth"] = max(1, service_times["prior_auth"] * 0.8)

        scenario_rows = [
            scenario_row("Current State", referrals_per_day, current_staff, current_times, shift_hours, target_hours, prior_auth_rate, seed),
            scenario_row("Add 1 Prior Auth Staff", referrals_per_day, add_prior_auth_staff, current_times, shift_hours, target_hours, prior_auth_rate, seed),
            scenario_row("Add 1 Benefits Staff", referrals_per_day, add_benefits_staff, current_times, shift_hours, target_hours, prior_auth_rate, seed),
            scenario_row("Reduce Prior Auth Time 20%", referrals_per_day, current_staff, reduce_prior_auth_time, shift_hours, target_hours, prior_auth_rate, seed),
            scenario_row("Demand +15%", int(referrals_per_day * 1.15), current_staff, current_times, shift_hours, target_hours, prior_auth_rate, seed),
        ]

        scenario_df = pd.DataFrame(scenario_rows)
        st.dataframe(scenario_df, use_container_width=True)

        fig_sla = px.bar(
            scenario_df,
            x="Scenario",
            y="SLA Compliance %",
            title="SLA Compliance by Scenario",
            text="SLA Compliance %",
        )
        st.plotly_chart(fig_sla, use_container_width=True)

        fig_wait = px.bar(
            scenario_df,
            x="Scenario",
            y="Avg Total Wait Minutes",
            title="Average Total Wait by Scenario",
            text="Avg Total Wait Minutes",
        )
        st.plotly_chart(fig_wait, use_container_width=True)

        best_scenario = scenario_df.sort_values(
            ["SLA Compliance %", "Avg Total Wait Minutes"],
            ascending=[False, True],
        ).iloc[0]

        st.success(f"Best scenario based on SLA and wait time: {best_scenario['Scenario']}.")

    with tabs[3]:
        st.subheader("Optimization")

        st.write(
            "Choose an objective, set guardrails, then run the optimizer. "
            "The optimizer avoids adding staff to stations that would fall below the minimum utilization floor."
        )

        objective = st.selectbox(
            "Optimization Objective",
            [
                "Balanced optimization",
                "Meet SLA with minimum staff",
                "Reduce cycle time",
            ],
            index=0,
        )

        opt_col1, opt_col2, opt_col3 = st.columns(3)

        with opt_col1:
            target_sla = st.number_input("Target SLA compliance %", 50.0, 100.0, 95.0, 1.0)

        with opt_col2:
            target_max_util = st.number_input(
                "Target max utilization %",
                50.0,
                150.0,
                92.0,
                1.0,
                help="Use 100% if stations can run up to full utilization. Use 85-92% for safer capacity.",
            )

        with opt_col3:
            min_util_floor = st.number_input(
                "Minimum recommended utilization %",
                0.0,
                100.0,
                70.0,
                1.0,
                help="Prevents overstaffing. The optimizer avoids adding staff if that station would fall below this utilization floor.",
            )

        opt_col4, opt_col5, opt_col6 = st.columns(3)

        with opt_col4:
            max_after_shift = st.number_input("Max cases finished after shift", 0, 1000, 0, 1)

        with opt_col5:
            max_extra_staff = st.number_input("Max extra staff allowed", 1, 35, 20, 1)

        with opt_col6:
            staff_cost_penalty = st.selectbox(
                "Staff cost penalty",
                ["Low", "Medium", "High"],
                index=1,
                help="Higher penalty makes the optimizer more conservative about adding staff.",
            )

        target_cycle_hours = st.number_input(
            "Target average cycle time hours",
            min_value=0.1,
            max_value=200.0,
            value=float(summary["avg_cycle_time_hours"]),
            step=0.5,
            help="Used mainly when the objective is Reduce cycle time.",
        )

        allowed_labels = st.multiselect(
            "Stations optimizer can adjust",
            options=list(PROCESS_LABELS.values()),
            default=list(PROCESS_LABELS.values()),
        )

        allowed_steps = [key for key, label in PROCESS_LABELS.items() if label in allowed_labels]

        st.info(
            "Guardrail logic: if any station is above the max-utilization target, the optimizer focuses on those overloaded stations first. "
            "It also rejects additions that would push a station below the minimum utilization floor."
        )

        if st.button("Run Optimizer"):
            if not allowed_steps:
                st.error("Select at least one station the optimizer can adjust.")
            else:
                (
                    optimizer_history,
                    final_staff,
                    final_summary,
                    final_step_summary,
                    optimizer_message,
                    rejected_actions,
                ) = optimize_staffing(
                    referrals=referrals_per_day,
                    shift_hours=shift_hours,
                    target_hours=target_hours,
                    prior_auth_rate=prior_auth_rate,
                    seed=seed,
                    base_staff=staff,
                    service_times=service_times,
                    target_sla=target_sla,
                    target_max_util=target_max_util,
                    min_util_floor=min_util_floor,
                    max_after_shift=max_after_shift,
                    max_extra_staff=max_extra_staff,
                    allowed_steps=allowed_steps,
                    objective=objective,
                    target_cycle_hours=target_cycle_hours,
                    staff_cost_penalty=staff_cost_penalty,
                )

                st.subheader("Optimizer Recommendation")
                st.success(optimizer_message)

                result_table = staffing_result_table(staff, final_staff)
                additions = result_table[result_table["Change"] > 0]

                if additions.empty:
                    st.write("Recommended staffing change: **No additional staff required.**")
                else:
                    change_text = ", ".join(f"{row['Station']} +{int(row['Change'])}" for _, row in additions.iterrows())
                    st.write(f"Recommended staffing change: **{change_text}**")

                m1, m2, m3, m4, m5 = st.columns(5)
                m1.metric("Projected SLA", f"{final_summary['sla_compliance_pct']}%")
                m2.metric("Max Utilization", f"{final_summary['max_utilization_pct']}%")
                m3.metric("After Shift Cases", final_summary["finished_after_shift_cases"])
                m4.metric("Avg Cycle Time", f"{final_summary['avg_cycle_time_hours']} hrs")
                m5.metric("Remaining Bottleneck", final_summary["bottleneck"])

                st.subheader("Current vs Recommended Staffing")
                st.dataframe(result_table, use_container_width=True)

                fig_staff = px.bar(
                    result_table,
                    x="Station",
                    y=["Current Staff", "Recommended Staff"],
                    barmode="group",
                    title="Current vs Recommended Staffing",
                )
                st.plotly_chart(fig_staff, use_container_width=True)

                st.subheader("Station Utilization: Current vs Recommended")

                utilization_compare = utilization_comparison_table(
                    current_step_summary=step_summary,
                    recommended_step_summary=final_step_summary,
                )

                st.dataframe(utilization_compare, use_container_width=True)

                util_long = utilization_compare.melt(
                    id_vars="Station",
                    value_vars=["Current Utilization %", "Recommended Utilization %"],
                    var_name="Scenario",
                    value_name="Utilization %",
                )

                fig_util_station = px.bar(
                    util_long,
                    x="Station",
                    y="Utilization %",
                    color="Scenario",
                    barmode="group",
                    title="Station Utilization: Current vs Recommended Staffing",
                    text="Utilization %",
                )

                fig_util_station.add_hline(
                    y=target_max_util,
                    line_dash="dash",
                    annotation_text=f"Target max utilization: {target_max_util}%",
                    annotation_position="top left",
                )

                fig_util_station.add_hline(
                    y=min_util_floor,
                    line_dash="dot",
                    annotation_text=f"Minimum utilization floor: {min_util_floor}%",
                    annotation_position="bottom left",
                )

                st.plotly_chart(fig_util_station, use_container_width=True)

                st.write(
                    "The dashed line is the max-utilization target. The dotted line is the minimum-utilization floor. "
                    "A recommended station below the floor is usually a sign of overstaffing."
                )

                if not rejected_actions.empty:
                    st.subheader("Rejected Staffing Actions")
                    st.write(
                        "These actions were rejected because they would create unreasonable underutilization."
                    )
                    st.dataframe(rejected_actions, use_container_width=True)

                st.subheader("Optimizer Search History")
                st.dataframe(optimizer_history, use_container_width=True)

                fig_targets = px.line(
                    optimizer_history,
                    x="Iteration",
                    y=["SLA Compliance %", "Max Utilization %", "Avg Cycle Hours"],
                    markers=True,
                    title="SLA, Max Utilization, and Cycle Time by Optimizer Iteration",
                )
                st.plotly_chart(fig_targets, use_container_width=True)

                fig_score = px.line(
                    optimizer_history,
                    x="Iteration",
                    y="Score",
                    markers=True,
                    title="Optimizer Score by Iteration - Lower is Better",
                )
                st.plotly_chart(fig_score, use_container_width=True)

                st.markdown("### What the Optimizer Score Means")
                st.write(
                    "The optimizer score is a penalty score. Lower is better. "
                    "It is not a dollar cost and it is not a probability. "
                    "It is a weighted score used to compare staffing options during the optimizer search."
                )

                st.markdown(
                    """
                    | Component | Why it increases the score |
                    |---|---|
                    | SLA below target | The plan misses the selected service-level goal |
                    | Utilization above target | One or more stations remain overloaded |
                    | Utilization below floor | The plan creates unreasonable overstaffing |
                    | Cases finished after shift | Work spills into overtime/backlog |
                    | Extra staff | The plan uses more labor |
                    | Average wait time | Cases still spend time waiting in queues |
                    | Average cycle time | End-to-end completion time remains high |
                    """
                )

                st.code(
                    """Optimizer Score =
SLA gap penalty
+ utilization-above-target penalty
+ utilization-below-floor penalty
+ after-shift penalty
+ extra-staff penalty
+ wait-time penalty
+ cycle-time penalty""",
                    language="text",
                )

                st.markdown(
                    """
                    **How to read the chart:**

                    - A falling score means each optimizer iteration is finding a better staffing pattern.
                    - A flat score means adding staff is not materially improving the selected targets.
                    - A rising score means the added staff is not worth the improvement under the current scoring weights.
                    - The best solution is usually the lowest score that also meets the selected targets without violating the utilization floor.
                    """
                )

    next_tab_index = 4

    if step_df is not None and not step_df.empty:
        with tabs[next_tab_index]:
            st.subheader("Live Process Flow Animation")

            st.write(
                "Each dot is a sampled synthetic case moving through the simulated process. "
                "The x-axis shows the process step. Larger dots indicate longer queue wait before service."
            )

            flow_fig = build_process_animation(step_df)

            if flow_fig is None:
                st.warning("No step-level data available for animation.")
            else:
                st.plotly_chart(flow_fig, use_container_width=True)

            st.subheader("Queue Wait by Step")

            fig_flow_wait = px.bar(
                step_summary,
                x="step",
                y="avg_queue_wait_minutes",
                title="Average Queue Wait by Process Step",
                text="avg_queue_wait_minutes",
            )

            st.plotly_chart(fig_flow_wait, use_container_width=True)

        next_tab_index += 1

    with tabs[next_tab_index]:
        st.subheader("Case-Level Simulation Data")
        st.dataframe(case_df, use_container_width=True)

        csv = case_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Case Data as CSV",
            data=csv,
            file_name="synthetic_simulation_cases.csv",
            mime="text/csv",
        )

else:
    st.info("Set the assumptions in the sidebar, then click Run Simulation.")
