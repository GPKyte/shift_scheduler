# Shift Scheduler  

A static employee schedule generator. Given employee schedules and desired coverage, find a desireable schedule that maximizes coverage and minimizes bad schedule decisions. Support is limited to needs of specific organization, but suggestions and pull requests for improvement are welcome!  

### Motivation  

Scheduling part-time workers effectively is a time-consuming and head-ache inducing task in some work environments.

### Goal  

Provide satisfactory employee schedule such that all shifts are filled.  
Even better if each employee gets nearly their desired # number of hours.  

## Process

*Input* is a series of JSON objects describing employee availabilities  

Covert given schedules into indexed objects representing timeslots that one is available to fulfill an equivalent shift-to-cover time slot.  
Leverage graph theory solution to Job Matching, i.e. maximum cardinality, imperfect 1:1 matching of a bipartite graph, to make scheduling choices.  
Interpret matcher's choices into a human-readable table (perhaps in CSV format)  

*Output* is CSV file named by default "new_schedule.csv"  

## Specific Usage  

python3 matcher.py [OPTIONS] -f /full/path/to/employee_availability.json

### Options

*Unsupported*
TODO: Add command interpreter library for easy argument parsing
TODO: Consider separating enough to easily attach web API or similar
TODO: Connect to calendar service and invite employees to their shifts

