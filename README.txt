# Shift Scheduler

Situation: It is difficult and confusing to schedule part-time workers effectively
We are given n workers and m shifts, shifts may be the same time as another, (e.g. 2 scheduled employees in an hour)
Shifts are broken into 15 minute blocks for matching

Goal: Provide satisfactory weekly employee schedule such that all shifts are filled and hours evenly distributed~~or match given preferences

Process: Use maximum bipartite matching algorithm to match shifts as provided by employee availability
Translate availability into workable blocks which become vertices in our bipartite graph, match those (create edges) to shifts at the same time

Intermedite handling will be necessary until later
