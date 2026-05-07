import streamlit as st
import plotly.express as px
import pandas as pd

from simulation import run_operations_simulation


def build_process_animation(step_df, max_cases=80):
    if step_df.empty:
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

    animation_df["time_bucket"] = (
        animation_df["service_start_minute"] // 30 * 30
    ).astype(int)

    animation_df["case_index"] = animation_df["case_id"].rank(
        method="dense"
    ).astype(int)

    animation_df["queue_wait_minutes"] = animation_df["queue_wait_minutes"].round(2)
    animation_df["service_minutes"] = animation_df["service_minutes"].round(2)

    animation_df["marker_size"] = animation_df["queue_wait_minutes"].clip(
        lower=3,
        upper=60,
    )

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



st.set_page_config(
    page_title="Alivia-style Operations Simulator",
    layout="wide"
)

st.title("Alivia-style Specialty Pharmacy Operations Simulator")

st.write(
    "Synthetic simulation demo for specialty pharmacy / healthcare operations. "
    "This model estimates bottlenecks, staffing pressure, wait time, cycle time, "
    "SLA risk, and improvement scenarios. It uses fake data only."
)

st.sidebar.header("Simulation Inputs")

referrals_per_day = st.sidebar.slider(
    "Referrals / prescriptions per day",
    min_value=50,
    max_value=1000,
    value=400,
    step=50
)

shift_hours = st.sidebar.slider(
    "Shift hours",
    min_value=4,
    max_value=24,
    value=8,
    step=1
)

target_hours = st.sidebar.slider(
    "Target completion time in hours",
    min_value=4,
    max_value=120,
    value=48,
    step=4
)

prior_auth_rate = st.sidebar.slider(
    "Percent requiring prior authorization",
    min_value=0,
    max_value=100,
    value=60,
    step=5
)

seed = st.sidebar.number_input(
    "Random seed",
    min_value=1,
    max_value=9999,
    value=42
)

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

run_button = st.button("Run Simulation")


def run_named_scenario(
    scenario_name,
    referrals,
    scenario_staff,
    scenario_service_times,
):
    case_df, step_df, step_summary, summary = run_operations_simulation(
        referrals_per_day=referrals,
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


if run_button:
    case_df, step_df, step_summary, summary = run_operations_simulation(
        referrals_per_day=referrals_per_day,
        shift_hours=shift_hours,
        target_hours=target_hours,
        prior_auth_rate=prior_auth_rate,
        seed=seed,
        staff=staff,
        service_times=service_times,
    )

    if not summary:
        st.error("Simulation did not return results.")
    else:
        st.subheader("Executive Summary")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Completed Cases", summary["completed_cases"])
        col2.metric("Avg Cycle Time", f'{summary["avg_cycle_time_hours"]} hrs')
        col3.metric("SLA Compliance", f'{summary["sla_compliance_pct"]}%')
        col4.metric("Bottleneck", summary["bottleneck"])

        col5, col6, col7 = st.columns(3)

        col5.metric("Avg Total Wait", f'{summary["avg_total_wait_minutes"]} min')
        col6.metric("Max Utilization", f'{summary["max_utilization_pct"]}%')
        col7.metric("Finished After Shift", summary["finished_after_shift_cases"])

        st.subheader("Operational Interpretation")

        if summary["max_utilization_pct"] >= 90:
            st.error(
                f"The operation is under heavy pressure. "
                f"The main bottleneck is {summary['bottleneck']} with "
                f"{summary['max_utilization_pct']}% utilization."
            )
        elif summary["max_utilization_pct"] >= 75:
            st.warning(
                f"The operation is moderately constrained. "
                f"The main bottleneck is {summary['bottleneck']}."
            )
        else:
            st.success(
                "The current staffing scenario appears stable under these assumptions."
            )

        if summary["sla_compliance_pct"] < 90:
            st.warning(
                "SLA compliance is below 90%. Test adding staff to the bottleneck "
                "or reducing service time in the bottleneck step."
            )

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Bottleneck Analysis",
            "Cycle Time",
            "Scenario Comparison",
            "Live Process Flow",
            "Raw Data"
        ])

        with tab1:
            st.subheader("Step Summary")
            st.dataframe(step_summary, use_container_width=True)

            fig_util = px.bar(
                step_summary,
                x="step",
                y="utilization_pct",
                title="Utilization by Process Step",
                text="utilization_pct"
            )
            st.plotly_chart(fig_util, use_container_width=True)

            fig_wait = px.bar(
                step_summary,
                x="step",
                y="avg_queue_wait_minutes",
                title="Average Queue Wait by Step",
                text="avg_queue_wait_minutes"
            )
            st.plotly_chart(fig_wait, use_container_width=True)

        with tab2:
            st.subheader("Cycle Time Distribution")

            fig_cycle = px.histogram(
                case_df,
                x="cycle_time_hours",
                nbins=40,
                title="Cycle Time Distribution in Hours"
            )
            st.plotly_chart(fig_cycle, use_container_width=True)

            fig_case = px.line(
                case_df.sort_values("case_id"),
                x="case_id",
                y="cycle_time_hours",
                title="Cycle Time by Case"
            )
            st.plotly_chart(fig_case, use_container_width=True)

        with tab3:
            st.subheader("What-If Scenario Comparison")

            current_staff = staff.copy()
            current_times = service_times.copy()

            add_prior_auth_staff = staff.copy()
            add_prior_auth_staff["prior_auth"] += 1

            add_benefits_staff = staff.copy()
            add_benefits_staff["benefits"] += 1

            reduce_prior_auth_time = service_times.copy()
            reduce_prior_auth_time["prior_auth"] = max(
                1,
                service_times["prior_auth"] * 0.8
            )

            scenario_rows = [
                run_named_scenario(
                    "Current State",
                    referrals_per_day,
                    current_staff,
                    current_times
                ),
                run_named_scenario(
                    "Add 1 Prior Auth Staff",
                    referrals_per_day,
                    add_prior_auth_staff,
                    current_times
                ),
                run_named_scenario(
                    "Add 1 Benefits Staff",
                    referrals_per_day,
                    add_benefits_staff,
                    current_times
                ),
                run_named_scenario(
                    "Reduce Prior Auth Time 20%",
                    referrals_per_day,
                    current_staff,
                    reduce_prior_auth_time
                ),
                run_named_scenario(
                    "Demand +15%",
                    int(referrals_per_day * 1.15),
                    current_staff,
                    current_times
                ),
            ]

            scenario_df = pd.DataFrame(scenario_rows)

            st.dataframe(scenario_df, use_container_width=True)

            fig_sla = px.bar(
                scenario_df,
                x="Scenario",
                y="SLA Compliance %",
                title="SLA Compliance by Scenario",
                text="SLA Compliance %"
            )
            st.plotly_chart(fig_sla, use_container_width=True)

            fig_wait = px.bar(
                scenario_df,
                x="Scenario",
                y="Avg Total Wait Minutes",
                title="Average Total Wait by Scenario",
                text="Avg Total Wait Minutes"
            )
            st.plotly_chart(fig_wait, use_container_width=True)

            best_scenario = scenario_df.sort_values(
                ["SLA Compliance %", "Avg Total Wait Minutes"],
                ascending=[False, True]
            ).iloc[0]

            st.success(
                f"Best scenario based on SLA and wait time: "
                f"{best_scenario['Scenario']}."
            )

        with tab4:
            st.subheader("Live Process Flow Animation")

            st.write(
                "Each dot is a sampled synthetic case moving through the simulated process. "
                "The x-axis shows the process step. Larger dots indicate longer queue wait "
                "before service."
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

        with tab5:
            st.subheader("Case-Level Simulation Data")
            st.dataframe(case_df, use_container_width=True)

            csv = case_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Case Data as CSV",
                data=csv,
                file_name="synthetic_simulation_cases.csv",
                mime="text/csv"
            )

else:
    st.info("Set the assumptions in the sidebar, then click Run Simulation.")