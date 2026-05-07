\# Case Study: Specialty Pharmacy Operations Simulation



\## Problem



Specialty pharmacy and healthcare operations often involve multiple steps before a patient receives therapy support, fulfillment, delivery, or coordination.



Common operational problems include:



\- Long cycle times

\- Prior authorization delays

\- Benefits verification bottlenecks

\- Staffing imbalance

\- Queue buildup

\- SLA risk

\- Lack of visibility into where delays occur



\## Solution



I built a discrete-event simulation model using Python and SimPy, with an interactive Streamlit interface.



The model allows a user to change demand, staffing levels, service times, prior authorization rate, and SLA targets.



\## Simulated Process



The simulation models the following workflow:



1\. Intake

2\. Benefits verification

3\. Prior authorization

4\. Pharmacy review

5\. Fulfillment

6\. Delivery / infusion coordination



\## KPIs



The app calculates:



\- Completed cases

\- Average cycle time

\- Average total wait time

\- SLA compliance

\- Bottleneck step

\- Staff utilization

\- Finished-after-shift volume



\## Scenario Analysis



The app compares the current state against improvement scenarios:



\- Add staff to prior authorization

\- Add staff to benefits verification

\- Reduce prior authorization processing time

\- Increase demand by 15%



\## Business Impact



This type of tool helps managers evaluate process changes before investing in staffing, automation, or workflow redesign.



Instead of guessing, the operation can test what-if scenarios and identify the highest-impact constraint.

