# Dynamic Task Viewer
Repository to learn *kivy* + *trio*.

This contains additional one-time use personal scripts, will create separate repository if this grows bigger.

---
## Goal
Simply Executing multiple scripts with the concurrency achieved with use of *trio*,
to provide ease-of-life multiple readouts from various sources ranging from real-time statistics from
web to mere time calculations.

---

## Current State
![](Demo.webp)

Demonstration of core structure. Features following:
- Dynamic reload of scripts stored in [folder](Schedules). Will update existing or add else to GUI.
- Proper start & stop of each script by use of ```trio.CancelScope```.
- Continuity decided by each task, rather than outer loop polling each tasks for execution.
  Demonstrated above with different numbers of calls on each task.

As I never used *kivy* nor *trio* before, this repository will be scratching board for
getting hang of both modules for this kind of usage.
