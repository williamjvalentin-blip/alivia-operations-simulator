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



---

# Staffing Optimizer

The project includes a separate Streamlit page called **Staffing Optimizer**.

## What It Answers

- What staffing level is needed to meet a target SLA?
- What staffing level is needed to stay under a target utilization level?
- How many additional staff are needed to avoid after-shift completion?
- Which station should receive the next staff member?
- Does the bottleneck shift after adding staff?

## How It Works

The optimizer starts from the current staffing levels. It tests adding one staff member to each allowed station, keeps the option with the best score, and repeats until the selected targets are met or the maximum extra-staff limit is reached.

The optimizer score penalizes:

- SLA below target
- utilization above target
- cases finished after shift
- extra staff
- average wait time
- average cycle time

This is a practical decision-support search, not a formal mathematical proof of a global optimum.

## Example Targets

- Target SLA compliance: 95%
- Target max utilization: 90%
- Max cases finished after shift: 0
- Max extra staff allowed: 8

If you want to test a 100% utilization target, set **Target max utilization %** to 100.

## Optimizer Score Explanation

The Staffing Optimizer includes an **Optimizer Score by Iteration** chart.

The optimizer score is a penalty score. **Lower is better.**

The score is not a dollar cost and not a probability. It is a weighted decision-support score used to compare staffing options during the optimizer search.

The score penalizes:

- SLA below the selected target
- utilization above the selected target
- cases finished after shift
- extra staff added
- average wait time
- average cycle time

Simplified logic:

```text
Optimizer Score =
SLA gap penalty
+ utilization gap penalty
+ after-shift penalty
+ extra-staff penalty
+ wait-time penalty
+ cycle-time penalty
```

How to interpret the chart:

- A falling score means each optimizer iteration is finding a better staffing pattern.
- A flat score means adding staff is not materially improving the selected targets.
- A rising score means the added staff is not worth the improvement under the current scoring weights.
- The preferred solution is usually the lowest score that also meets the SLA, utilization, and after-shift targets.


## Optimization Modes and Guardrails

The app includes an **Optimization** tab with three objective modes:

- **Balanced optimization**
- **Meet SLA with minimum staff**
- **Reduce cycle time**

The optimizer includes guardrails to avoid unreasonable staffing recommendations:

- It focuses first on stations above the target max utilization.
- It rejects staffing additions that would push a station below the selected minimum utilization floor.
- It includes a staff-cost penalty so it does not add people for tiny improvements.
- It shows rejected staffing actions when a recommendation would create overstaffing.

The utilization chart includes:

- Current utilization %
- Recommended utilization %
- Target max utilization line
- Minimum utilization floor line

This prevents recommendations like adding staff to Intake until it falls to very low utilization while other stations remain overloaded.

<!-- OPTIMIZATION_TAB_GUIDE_START -->

---

# Optimization Tab Guide

The app includes an **Optimization** tab. This tab estimates the staffing changes needed to meet selected operational targets while avoiding unrealistic overstaffing.

## What the Optimization Tab Is Intended to Answer

The Optimization tab answers questions such as:

- What staffing level is needed to meet a target SLA?
- What staffing level is needed to keep station utilization under a selected target?
- What staffing level is needed to reduce average cycle time?
- Which station should receive the next staff member?
- Which stations are still overloaded after optimization?
- Which staffing additions are rejected because they would create underutilization?
- Does the bottleneck shift after adding staff?
- Is the recommendation reasonable from a utilization standpoint?

## Optimization Objectives

The user can select one of three optimization objectives.

| Optimization Objective | Main Use | What It Prioritizes | When to Use |
|---|---|---|---|
| **Balanced optimization** | Default recommended mode | SLA, utilization, cycle time, wait time, and reasonable staffing | Use this for the most realistic staffing recommendation. |
| **Meet SLA with minimum staff** | Labor-efficient staffing | Meeting SLA with the fewest added staff | Use this when cost control is important. |
| **Reduce cycle time** | Faster completion | Lower average cycle time while respecting staffing guardrails | Use this when management wants faster turnaround. |

## Optimization Controls

| Control | What It Means | Example | How to Interpret |
|---|---|---|---|
| **Target SLA compliance %** | Minimum acceptable percent of cases completed within target time | 95% | The optimizer tries to reach or exceed this service level. |
| **Target max utilization %** | Maximum acceptable utilization for the busiest station | 90% or 92% | If a station is above this line, it is considered overloaded. |
| **Minimum recommended utilization %** | Minimum acceptable utilization after adding staff | 70% | Prevents recommendations that overstaff a station. |
| **Max cases finished after shift** | Maximum allowed cases completed after the shift window | 0 | Helps avoid backlog/overtime risk. |
| **Max extra staff allowed** | Maximum number of extra staff the optimizer may add | 35 | Limits the search so the recommendation stays realistic. |
| **Staff cost penalty** | How conservative the optimizer is about adding staff | Low / Medium / High | Higher penalty means it only adds staff when the improvement is more meaningful. |
| **Target average cycle time hours** | Desired average end-to-end case completion time | Example: 12 hours | Mainly used with the Reduce cycle time objective. |
| **Stations optimizer can adjust** | Which process stations are allowed to receive added staff | Prior Auth, Pharmacy Review, etc. | Use this when only some teams can realistically add headcount. |

## Questions the Optimization Tab Can Answer

| # | Question | What to Adjust | Where to Look for the Answer | What to Look For |
|---:|---|---|---|---|
| 1 | What staffing is needed to meet SLA? | Set **Target SLA compliance %** | Optimization → Optimizer Recommendation | Recommended staffing change and Projected SLA. |
| 2 | What staffing is needed to stay under utilization target? | Set **Target max utilization %** | Optimization → Station Utilization chart | Recommended utilization should fall below the target max utilization line. |
| 3 | What staffing is needed to reduce cycle time? | Select **Reduce cycle time** and set **Target average cycle time hours** | Optimization → Avg Cycle Time metric and Search History | Avg Cycle Hours should decrease across iterations. |
| 4 | Which station should receive the next staff member? | Run the optimizer | Optimization → Optimizer Search History | The **Action** column shows where each added staff member went. |
| 5 | Which stations are still overloaded? | Set utilization target and run optimizer | Optimization → Station Utilization chart | Stations above the target line remain overloaded. |
| 6 | Is the recommendation creating overstaffing? | Set **Minimum recommended utilization %** | Optimization → Station Utilization chart and Rejected Staffing Actions | Stations below the floor may be overstaffed; rejected actions explain what was blocked. |
| 7 | Why did the optimizer reject a staffing action? | Run optimizer with utilization floor | Optimization → Rejected Staffing Actions | Shows the station and reason, such as projected utilization below the floor. |
| 8 | Does the bottleneck shift after adding staff? | Run optimizer | Optimization → Remaining Bottleneck and Search History | If the bottleneck changes, the original constraint was relieved and another station became the next constraint. |
| 9 | Is adding staff worth it? | Change **Staff cost penalty** | Optimization → Optimizer Score and staffing recommendation | Higher cost penalty makes the model more conservative. |
| 10 | Can we avoid overtime/backlog? | Set **Max cases finished after shift** to 0 | Optimization → After Shift Cases | Target is met when after-shift cases are at or below the selected value. |
| 11 | Should we use a safer capacity target? | Use Target max utilization of 85–92% | Optimization → Station Utilization chart | Lower targets create more buffer but may require more staff. |
| 12 | Can stations run closer to full capacity? | Use Target max utilization of 100% | Optimization → Station Utilization chart | Allows higher utilization but creates less buffer for variation. |
| 13 | Which teams are impossible to fix with staffing alone? | Run optimizer with max extra staff allowed | Optimization → Optimizer message and remaining overloaded stations | If targets are not reached, process time reduction may be required. |
| 14 | What if only some teams can add staff? | Limit **Stations optimizer can adjust** | Optimization → Recommendation and Search History | Shows best staffing plan using only allowed stations. |
| 15 | What if adding staff makes Intake too low-utilized? | Set Minimum utilization floor, e.g. 70% | Optimization → Rejected Staffing Actions | The optimizer should reject additions that push Intake below the floor. |
| 16 | How much staff is added in total? | Run optimizer | Optimization → Current vs Recommended Staffing | Look at the **Change** column and Total Staff in Search History. |
| 17 | Which iteration produced the best operating plan? | Run optimizer | Optimization → Optimizer Score by Iteration | Lower score is better; preferred solution meets targets without violating guardrails. |
| 18 | Is the selected target too aggressive? | Run optimizer | Optimization → Optimizer message | If target is not reached within max extra staff, target may be too aggressive or process improvement is needed. |
| 19 | Are we solving the real bottleneck first? | Run optimizer | Optimization → Search History and Station Utilization chart | Added staff should go first to overloaded/high-utilization stations. |
| 20 | What happens if I change demand before optimizing? | Change sidebar **Referrals / prescriptions per day**, then run simulation and optimizer | Executive Summary + Optimization | Higher demand should affect required staffing and utilization. |

## How the Optimizer Works

The optimizer starts with the current staffing levels from the sidebar.

Then it repeats this process:

1. Runs the current simulation.
2. Finds stations above the selected max-utilization target.
3. Tests adding one staff member to eligible stations.
4. Rejects staffing additions that would push a station below the minimum utilization floor.
5. Scores each candidate staffing plan.
6. Keeps the best-scoring option.
7. Repeats until targets are met or the max extra staff limit is reached.

This is a practical decision-support search. It is not a formal mathematical proof of a global optimum.

## Guardrails Added to Avoid Unreasonable Recommendations

The optimizer includes guardrails so it does not recommend adding staff to a station that is already underutilized while other stations remain overloaded.

| Guardrail | Purpose |
|---|---|
| **Focus on overloaded stations first** | If any station is above the target utilization line, the optimizer prioritizes those stations. |
| **Minimum utilization floor** | Prevents adding staff when the result would make that station too underutilized. |
| **Rejected Staffing Actions table** | Shows when the optimizer blocks a staffing action and explains why. |
| **Staff cost penalty** | Prevents adding extra people for small improvements. |
| **Station utilization chart** | Makes it visible whether the recommendation is reasonable. |

## Optimizer Score Explanation

The **Optimizer Score by Iteration** chart shows a penalty score.

**Lower is better.**

The score is not a dollar cost and not a probability. It is a weighted decision-support score used to compare staffing options.

The score penalizes:

- SLA below target
- utilization above target
- utilization below the minimum floor
- cases finished after shift
- extra staff added
- average wait time
- average cycle time

Simplified logic:

```text
Optimizer Score =
SLA gap penalty
+ utilization-above-target penalty
+ utilization-below-floor penalty
+ after-shift penalty
+ extra-staff penalty
+ wait-time penalty
+ cycle-time penalty
```

## How to Interpret the Optimization Charts

| Chart / Table | What It Tells You |
|---|---|
| **Current vs Recommended Staffing** | Shows how many staff are recommended by station. |
| **Station Utilization: Current vs Recommended** | Shows whether each station moves closer to the utilization target. |
| **Target max utilization line** | Stations above this line are still overloaded. |
| **Minimum utilization floor line** | Stations below this line may be overstaffed. |
| **Rejected Staffing Actions** | Shows which staffing additions were blocked and why. |
| **Optimizer Search History** | Shows each iteration and where the optimizer added staff. |
| **SLA / Max Utilization / Cycle Time chart** | Shows whether operational performance improves over iterations. |
| **Optimizer Score by Iteration** | Shows whether the overall staffing plan is improving. Lower is better. |

## Recommended Default Settings

For a realistic staffing recommendation, start with:

| Setting | Recommended Default |
|---|---:|
| Optimization Objective | Balanced optimization |
| Target SLA compliance % | 95% |
| Target max utilization % | 90–92% |
| Minimum recommended utilization % | 70% |
| Max cases finished after shift | 0 |
| Max extra staff allowed | 35 |
| Staff cost penalty | Medium |

For cycle-time reduction, use:

| Setting | Recommended Default |
|---|---:|
| Optimization Objective | Reduce cycle time |
| Target average cycle time hours | Lower than current average |
| Minimum recommended utilization % | 70% |
| Staff cost penalty | High |

## Example Interpretation

If the utilization chart shows:

```text
Current:
Pharmacy Review = 442%
Prior Authorization = 335%
Intake = 82%

Recommended:
Pharmacy Review = 124%
Prior Authorization = 93%
Intake = 82%
```

Then the recommendation is reasonable because it focused on overloaded stations.

If the recommendation shows:

```text
Recommended Intake utilization = 42%
```

while other stations are still above target, that would be unreasonable. The minimum utilization floor and rejected-actions logic are designed to prevent that.

<!-- OPTIMIZATION_TAB_GUIDE_END -->
