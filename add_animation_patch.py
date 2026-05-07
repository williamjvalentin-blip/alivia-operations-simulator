from pathlib import Path

sim_path = Path("simulation.py")
app_path = Path("app.py")
readme_path = Path("README.md")

sim = sim_path.read_text(encoding="utf-8")

sim = sim.replace(
    "return case_df, pd.DataFrame(), {}",
    "return case_df, pd.DataFrame(), pd.DataFrame(), {}"
)

sim = sim.replace(
    "return case_df, step_summary, summary",
    "return case_df, step_df, step_summary, summary"
)

sim_path.write_text(sim, encoding="utf-8")


app = app_path.read_text(encoding="utf-8")

# Update all simulation calls from 3 returned values to 4 returned values.
app = app.replace(
    "case_df, step_summary, summary = run_operations_simulation(",
    "case_df, step_df, step_summary, summary = run_operations_simulation("
)

animation_helper = r'''

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
'''

if "def build_process_animation" not in app:
    app = app.replace(
        "from simulation import run_operations_simulation\n",
        "from simulation import run_operations_simulation\n" + animation_helper + "\n",
        1,
    )

old_tabs = '''        tab1, tab2, tab3, tab4 = st.tabs([
            "Bottleneck Analysis",
            "Cycle Time",
            "Scenario Comparison",
            "Raw Data"
        ])'''

new_tabs = '''        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Bottleneck Analysis",
            "Cycle Time",
            "Scenario Comparison",
            "Live Process Flow",
            "Raw Data"
        ])'''

if "Live Process Flow" not in app:
    app = app.replace(old_tabs, new_tabs)

old_raw_data_start = '''        with tab4:
            st.subheader("Case-Level Simulation Data")'''

new_animation_block = '''        with tab4:
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
            st.subheader("Case-Level Simulation Data")'''

if "Live Process Flow Animation" not in app:
    app = app.replace(old_raw_data_start, new_animation_block)

app_path.write_text(app, encoding="utf-8")


if readme_path.exists():
    readme = readme_path.read_text(encoding="utf-8")

    addition = """

## Live Process Flow Animation

The app includes a visual animation that samples synthetic cases and shows how work moves through the process steps. Larger dots indicate longer queue wait before service. This helps managers visually understand where work accumulates and where bottlenecks may be forming.
"""

    if "Live Process Flow Animation" not in readme:
        readme += addition
        readme_path.write_text(readme, encoding="utf-8")

print("Animation patch completed.")