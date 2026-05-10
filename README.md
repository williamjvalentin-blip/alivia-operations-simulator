\# Alivia-style Specialty Pharmacy Operations Simulator



This is a synthetic healthcare operations simulation built with Python, SimPy, Streamlit, pandas, and Plotly.



The project models a specialty pharmacy-style workflow inspired by public healthcare/pharmacy operations concepts. It does not use real patient data.



\## Purpose



The simulator helps operations leaders test staffing, demand, bottleneck, cycle time, wait time, and SLA scenarios before making process or staffing decisions.



\## Simulated Workflow



1\. Referral / prescription intake

2\. Benefits verification

3\. Prior authorization

4\. Pharmacy review

5\. Medication fulfillment

6\. Delivery / infusion coordination



\## What the App Shows



\- Completed cases

\- Average cycle time

\- Average total wait time

\- SLA compliance

\- Finished-after-shift cases

\- Bottleneck step

\- Utilization by process step

\- Queue wait by process step

\- Scenario comparison



\## What-If Scenarios



The app compares:



\- Current state

\- Add 1 prior authorization staff

\- Add 1 benefits verification staff

\- Reduce prior authorization time by 20%

\- Demand increase of 15%



\## Business Value



This tool can help healthcare, pharmacy, service, logistics, or back-office operations teams answer questions like:



\- Where is the bottleneck?

\- How much staffing pressure exists?

\- What happens if demand increases?

\- Which improvement scenario has the biggest impact?

\- Are we likely to meet service-level targets?



\## Important Note



This project uses synthetic data only. It does not include real patient data, protected health information, or clinical recommendations.



## Live Process Flow Animation

The app includes a visual animation that samples synthetic cases and shows how work moves through the process steps. Larger dots indicate longer queue wait before service. This helps managers visually understand where work accumulates and where bottlenecks may be forming.

---

# Question Bank: What This Simulator Can Answer

This section explains what business questions the simulator can answer, where to look in the app, which metric/column provides the answer, and how to interpret the result.

| # | Question / information needed | Where to look in the app | Metric / column to read | How to interpret the answer |
|---:|---|---|---|---|
| 1 | How many cases/referrals were completed? | Executive Summary | Completed Cases | Shows total throughput under the selected assumptions. |
| 2 | How long does the average case take from start to finish? | Executive Summary | Avg Cycle Time | Lower is better. This is the end-to-end process time. |
| 3 | Are we meeting the service target? | Executive Summary | SLA Compliance | Higher is better. Below 90% suggests service-level risk. |
| 4 | What is the main bottleneck? | Executive Summary | Bottleneck | The step limiting flow the most under current assumptions. |
| 5 | How overloaded is the worst step? | Executive Summary | Max Utilization | 90%+ means the step is under heavy pressure. |
| 6 | How many cases spill past the shift? | Executive Summary | Finished After Shift | Higher number means backlog/overtime risk. |
| 7 | Where are cases waiting the longest? | Bottleneck Analysis | avg_queue_wait_minutes | Highest value shows where cases sit in queue before being worked. |
| 8 | Which step has the highest workload pressure? | Bottleneck Analysis | utilization_pct | Highest utilization usually indicates the constrained resource. |
| 9 | Which step takes the longest to perform once started? | Bottleneck Analysis | avg_service_minutes | High service time means the work itself is slow, not just waiting. |
| 10 | Is the problem waiting time or processing time? | Bottleneck Analysis | Compare avg_queue_wait_minutes vs avg_service_minutes | High wait = capacity issue. High service time = process/complexity issue. |
| 11 | Is Prior Authorization causing the delay? | Bottleneck Analysis | Prior Authorization row: queue wait, service time, utilization | If these are highest, PA is the main constraint. |
| 12 | Should we add Prior Authorization staff? | Scenario Comparison | Current State vs Add 1 Prior Auth Staff | If SLA improves and wait drops, PA staffing helps. |
| 13 | Should we add Benefits Verification staff? | Scenario Comparison | Current State vs Add 1 Benefits Staff | If this improves more than PA staffing, Benefits may be the constraint. |
| 14 | Is process improvement better than hiring? | Scenario Comparison | Add 1 Prior Auth Staff vs Reduce Prior Auth Time 20% | Better scenario depends on SLA, wait, cycle time, and cost feasibility. |
| 15 | What happens if demand increases? | Scenario Comparison | Demand +15% row | If SLA drops, wait rises, or after-shift cases rise, growth creates risk. |
| 16 | Which scenario gives the best operational result? | Scenario Comparison | SLA Compliance, Avg Wait, Avg Cycle Time | Best scenario has highest SLA and lowest wait/cycle time. |
| 17 | Does fixing one step create another bottleneck? | Scenario Comparison | Bottleneck column across scenarios | If bottleneck changes, the original constraint was relieved and a new constraint emerged. |
| 18 | What happens if I manually increase demand? | Sidebar + Executive Summary | Referrals / prescriptions per day, then summary metrics | Higher demand should affect SLA, wait, utilization, and after-shift cases. |
| 19 | What happens if more cases require prior authorization? | Sidebar + Bottleneck Analysis | Percent requiring prior authorization | More PA cases usually increases PA wait/utilization. |
| 20 | What happens if the SLA target is tighter? | Sidebar + Executive Summary | Target completion time in hours | Lower target makes SLA harder to meet. |
| 21 | What happens if the shift is shorter or longer? | Sidebar + Executive Summary | Shift hours | Shorter shift usually increases after-shift cases/utilization. |
| 22 | How sensitive is the process to intake staffing? | Sidebar + Bottleneck Analysis | Intake staff | Watch Intake utilization, queue wait, and overall SLA. |
| 23 | How sensitive is the process to benefits staffing? | Sidebar + Bottleneck Analysis | Benefits verification staff | Watch Benefits utilization, queue wait, and scenario improvement. |
| 24 | How sensitive is the process to prior auth staffing? | Sidebar + Bottleneck Analysis | Prior authorization staff | Watch PA utilization, queue wait, and bottleneck shift. |
| 25 | How sensitive is the process to pharmacy review staffing? | Sidebar + Bottleneck Analysis | Pharmacy review staff | Watch whether the bottleneck shifts after PA is improved. |
| 26 | How sensitive is the process to fulfillment staffing? | Sidebar + Bottleneck Analysis | Fulfillment staff | Useful when fulfillment becomes bottleneck after earlier steps improve. |
| 27 | How sensitive is the process to delivery coordination staffing? | Sidebar + Bottleneck Analysis | Delivery coordination staff | Watch Delivery utilization and finished-after-shift cases. |
| 28 | What happens if intake is faster? | Sidebar + Bottleneck Analysis | Lower Intake minutes | See whether intake wait/utilization drops and whether another step becomes bottleneck. |
| 29 | What happens if benefits verification is faster? | Sidebar + Bottleneck Analysis | Lower Benefits verification minutes | Useful to test checklist/automation impact. |
| 30 | What happens if prior authorization is faster? | Sidebar or Scenario Comparison | Lower Prior authorization minutes or use Reduce Prior Auth Time 20% | If this improves SLA, PA processing speed matters. |
| 31 | What happens if pharmacy review is faster? | Sidebar + Bottleneck Analysis | Lower Pharmacy review minutes | Useful if Pharmacy Review appears as the next bottleneck. |
| 32 | What happens if fulfillment is faster? | Sidebar + Bottleneck Analysis | Lower Fulfillment minutes | Tests fulfillment automation or workflow improvement. |
| 33 | What happens if delivery coordination is faster? | Sidebar + Bottleneck Analysis | Lower Delivery coordination minutes | Tests scheduling/delivery process improvement. |
| 34 | How much total waiting occurs per case? | Executive Summary | Avg Total Wait | Higher means queueing/capacity problems. |
| 35 | What does the distribution of cycle time look like? | Cycle Time tab | Cycle Time Distribution chart | Wide/right-skewed distribution means some cases take much longer than average. |
| 36 | Are there outlier cases with long cycle time? | Cycle Time tab | Cycle Time by Case chart | Spikes show cases that experience unusually long delays. |
| 37 | Can I inspect the simulated case-level data? | Raw Data tab | Case-level table | Use this to see individual case cycle times and completion results. |
| 38 | Can I export the simulation results? | Raw Data tab | Download Case Data as CSV | Downloads synthetic simulation output. |
| 39 | Can I visually see process flow? | Live Process Flow tab, if added | Animated flow chart | Accumulation or larger dots near a step indicates congestion/waiting. |
| 40 | What is the first operational fix to test? | Scenario Comparison + Bottleneck Analysis | Highest bottleneck + best scenario improvement | Fix the highest-pressure step that produces the best scenario result. |

## Most Important Business Decision Questions

| Business decision | Use this answer path |
|---|---|
| Do we need more staff? | Scenario Comparison ? Add staff scenarios |
| Where should we add staff? | Bottleneck Analysis ? highest utilization/wait |
| Should we automate instead of hiring? | Compare Add Staff vs Reduce Processing Time |
| Can we handle growth? | Scenario Comparison ? Demand +15% |
| Where is the bottleneck? | Executive Summary + Bottleneck Analysis |
| Are we meeting SLA? | Executive Summary ? SLA Compliance |
| Will we need overtime? | Executive Summary ? Finished After Shift |
| What should we fix first? | Bottleneck + best scenario improvement |

## How to Use the App

1. Set assumptions in the left sidebar.
2. Click **Run Simulation**.
3. Read **Executive Summary** for overall health.
4. Read **Bottleneck Analysis** for root cause.
5. Read **Scenario Comparison** for what action works best.

