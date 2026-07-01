# Asynchronous Programming Learning Repository

> A personal learning space for Python programming, asynchronous execution, concurrency models, and weekly classroom labs.

This repository collects class examples, lab exercises, and study notes from my asynchronous programming course.  
It is designed to grow week by week as new topics, assignments, and experiments are added.

---

## Overview

The main goal of this repository is to keep learning materials organized in one place:

- weekly Python examples
- classroom lab files
- concurrency model comparisons
- study guides written in Markdown
- small simulations that make abstract concepts easier to understand

The content is intentionally practical. Most examples are written as small runnable programs so the behavior can be observed directly from terminal output.

---

## Topics Covered

Current and future topics may include:

| Topic | Description |
|---|---|
| Synchronous Programming | Step-by-step execution, useful as a baseline for comparison |
| Threading | Running multiple workflows in threads within one process |
| Multiprocessing | Running independent workflows in separate processes |
| Asyncio | Coroutine-based asynchronous programming with an event loop |
| Event Loop | The core mechanism that schedules asynchronous tasks |
| Coroutine & Task | Python async building blocks used by `asyncio` |
| Timing Comparison | Measuring how different execution styles affect runtime |
| Simulation Labs | Coffee shop and restaurant-style examples for easier understanding |

---

## Repository Structure

```text
.
├── Week1/
│   ├── coffee*.py
│   ├── pid*.py
│   ├── ps*.py
│   └── up*.py
│
├── Week2/
│   ├── asyncio01.py - asyncio10.py
│   └── restaurant_01_*.py
│
├── *.md
│   └── Study guides, lab explanations, and walkthrough notes
│
└── README.md
```

> More folders and weeks will be added as the course continues.

---

## Current Learning Modules

| Module | Focus |
|---|---|
| `Week1/` | Comparing synchronous, threading, multiprocessing, and asyncio patterns |
| `Week2/` | Understanding `asyncio`, coroutine objects, tasks, and restaurant workflow simulations |
| Markdown Guides | Beginner-friendly explanations and lab walkthroughs |

---

## Study Guides

| Guide | Purpose |
|---|---|
| `Week1_UP1-4_Lab_Guide.md` | Week 1 lab guide and explanation of core execution patterns |
| `Week2_Asyncio_Restaurant_Lab_Guide.md` | Beginner-friendly guide for Week 2 asyncio concepts and restaurant labs |
| `Week2_Restaurant_01_Code_Study_Guide.md` | Code walkthrough for the restaurant examples across simple, thread, process, and asyncio versions |

---

## How to Run Examples

Run any Python file directly from the repository root:

```bash
python3 Week2/asyncio01.py
python3 Week2/restaurant_01_asyncio.py
```

Run multiple Week 2 asyncio examples:

```bash
for f in Week2/asyncio{01..10}.py; do
  echo "===== $f ====="
  python3 "$f"
  echo
done
```

Check syntax for a group of files:

```bash
python3 -m py_compile Week2/*.py
```

---

## Learning Style

This repository focuses on learning by comparison:

```text
simple / synchronous
        ↓
threading
        ↓
multiprocessing
        ↓
asyncio
```

Many examples use the same scenario across different execution models. This makes it easier to see:

- what changes in the code
- what changes in the output order
- what changes in total runtime
- which model is easier to understand for each kind of task

---

## Notes

- This is a learning repository, not a production software project.
- Some files are intentionally simple so the core concept is easier to see.
- Output order may differ between runs when using threads, processes, or async tasks.
- More weeks, labs, and notes will be added over time.

---

## Author

Created as part of my Computer Engineering coursework and asynchronous programming practice.