# Assignment 3: commands to run in your Codespace (on YOUR fork)

Copy `labs/` and `governance/` from this zip into the repo root (it only adds new files).
Every number in the report comes from these commands. The seed is fixed, so your output should match.

```bash
python -m pip install matplotlib          # the charts need it; not in requirements.txt

# 1. The grid, the per-hospital add-on, the charts
python labs/a3_harness.py                 # results/a3_results.csv  (54 rows)
python labs/a3_who_pays.py                # results/a3_who_pays.csv (108 rows)
python labs/a3_charts.py                  # results/chart_a_*.png and chart_b_*.png

# 2. Lab 3, all six skews, with fine-tuning
for s in none label quantity feature concept realistic; do python labs/lab3_skew.py --skew $s --finetune; done

# 3. Extra experiment: Lab 7 under attack with two charters
python run_federation.py --attack boost
python run_federation.py --attack backdoor
python run_federation.py --policy governance/a3_charter_B.json
python run_federation.py --policy governance/a3_charter_B.json --attack boost
python run_federation.py --policy governance/a3_charter_B.json --attack backdoor
python run_federation.py --policy governance/a3_charter_forbidden.json --attack boost      # STOPPED at pre-check
# follow-ups that explain why trimmed_mean did not matter
python run_federation.py --policy governance/a3_charter_B_mean.json --attack boost
python run_federation.py --policy governance/a3_charter_B_mean.json --attack backdoor
python run_federation.py --policy governance/a3_charter_B_trimmed_nodp.json --attack boost
python run_federation.py --policy governance/a3_charter_B_trimmed_nodp.json --attack backdoor

# 4. Numbers cited in the governance clauses
python labs/lab6_dp.py
python labs/lab5_leak.py
python labs/lab5_leak.py --batch 8
python labs/lab5_poison.py

# 5. Commit (results/ is git-ignored, so force-add it)
git add -f results/a3_results.csv results/a3_who_pays.csv results/chart_a_accuracy_vs_hospitals.png results/chart_b_worst_hospital_vs_skew.png
git add labs/a3_who_pays.py labs/a3_charts.py governance/a3_charter_*.json
git commit -m "Assignment 3: results, charts, charters"
git push
```
