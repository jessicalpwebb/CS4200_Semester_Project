# CS4200 Semester Project: Pipeline Hazard Detection Simulator

This project is a small Python simulator for a basic 5-stage CPU pipeline.
It focuses on RAW data hazards and shows how stalls affect pipeline performance.

## Topic
Pipeline Hazard Detection

## What it simulates
The simulator models these five pipeline stages:

IF -> ID -> EX -> MEM -> WB

The program checks for RAW hazards when an instruction needs a register that is still being produced by an older instruction in the pipeline. When this happens, the simulator freezes IF/ID and inserts a stall bubble.

## Files
- `main.py` - main simulator code
- `programs/no_hazards.txt` - test program with mostly independent instructions
- `programs/basic_hazards.txt` - test program with a few dependencies
- `programs/heavy_hazards.txt` - test program with repeated dependencies
- `results/` - output logs generated when the program runs

## How to run
From this folder, run:

```bash
python main.py
```

To run one program only:

```bash
python main.py programs/basic_hazards.txt
```

## Output metrics
The simulator prints:
- total instructions
- total cycles
- stall cycles
- pipeline CPI
- cycle-by-cycle pipeline table
- hazards detected

## Why this fits computer architecture
This project explores pipeline hazards, instruction dependencies, stalls, CPI, and performance tradeoffs. It shows how dependencies between instructions can reduce pipeline efficiency even when the program has the same instruction count.
