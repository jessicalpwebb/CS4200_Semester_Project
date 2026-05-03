# CS4200 Semester Project
# Pipeline Hazard Detection Simulator
# This project models a simple 5 stage pipeline and inserts stalls for RAW hazards.

import os
import sys

STAGES = ["IF", "ID", "EX", "MEM", "WB"]

class Instruction:
    def __init__(self, text, number):
        self.text = text.strip()
        self.number = number
        self.op = "nop"
        self.rd = None
        self.rs1 = None
        self.rs2 = None
        self.sources = []
        self.dest = None
        self.parse()

    def parse(self):
        clean = self.text.split("#")[0].strip()
        clean = clean.replace(",", " ").replace("(", " ").replace(")", " ")
        parts = clean.split()

        if len(parts) == 0:
            self.op = "nop"
            self.text = "nop"
            return

        self.op = parts[0].lower()

        # R type: add x1, x2, x3
        if self.op in ["add", "sub", "and", "or", "xor", "slt"] and len(parts) >= 4:
            self.rd = parts[1]
            self.rs1 = parts[2]
            self.rs2 = parts[3]
            self.dest = self.rd
            self.sources = [self.rs1, self.rs2]

        # I type: addi x1, x2, 5
        elif self.op in ["addi", "andi", "ori", "xori"] and len(parts) >= 3:
            self.rd = parts[1]
            self.rs1 = parts[2]
            self.dest = self.rd
            self.sources = [self.rs1]

        # Load: lw x1, 0(x2)
        elif self.op in ["lw", "lb", "lh"] and len(parts) >= 4:
            self.rd = parts[1]
            self.rs1 = parts[3]
            self.dest = self.rd
            self.sources = [self.rs1]

        # Store: sw x1, 0(x2)
        elif self.op in ["sw", "sb", "sh"] and len(parts) >= 4:
            value_reg = parts[1]
            base_reg = parts[3]
            self.sources = [value_reg, base_reg]

        # Branch: beq x1, x2, label
        elif self.op in ["beq", "bne", "blt", "bge"] and len(parts) >= 3:
            self.sources = [parts[1], parts[2]]

    def label(self):
        if self.text == "nop":
            return "nop"
        return "I" + str(self.number) + ": " + self.text


def read_program(filename):
    instructions = []
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if line == "" or line.startswith("#"):
                continue
            instructions.append(Instruction(line, len(instructions) + 1))
    return instructions


def has_raw_hazard(id_inst, ex_inst, mem_inst):
    if id_inst is None or id_inst.op == "nop":
        return False, []

    hazards = []
    for older in [ex_inst, mem_inst]:
        if older is not None and older.dest is not None:
            for src in id_inst.sources:
                if src == older.dest and src != "x0":
                    hazards.append("{} needs {}, which is still being produced by {}".format(
                        id_inst.label(), src, older.label()
                    ))

    return len(hazards) > 0, hazards


def short_label(inst):
    if inst is None:
        return "."
    if inst.op == "nop":
        return "STALL"
    return "I" + str(inst.number)


def run_pipeline(instructions, log_file):
    pipe = [None, None, None, None, None]
    pc = 0
    cycle = 0
    completed = 0
    stall_cycles = 0
    hazard_log = []
    timeline = []

    while completed < len(instructions) or any(stage is not None for stage in pipe):
        cycle += 1

        if pipe[4] is not None and pipe[4].op != "nop":
            completed += 1

        hazard_found, hazards = has_raw_hazard(pipe[1], pipe[2], pipe[3])

        if hazard_found:
            stall_cycles += 1
            hazard_log.extend(["Cycle {}: {}".format(cycle, h) for h in hazards])
            next_pipe = [None, pipe[1], Instruction("nop", 0), pipe[2], pipe[3]]
            # IF is frozen during a stall, so the pc does not move.
            next_pipe[0] = pipe[0]
        else:
            next_pipe = [None, None, pipe[1], pipe[2], pipe[3]]
            next_pipe[1] = pipe[0]
            if pc < len(instructions):
                next_pipe[0] = instructions[pc]
                pc += 1

        pipe = next_pipe
        timeline.append([cycle] + [short_label(x) for x in pipe])

    cpi = cycle / len(instructions) if len(instructions) > 0 else 0

    lines = []
    lines.append("Pipeline Hazard Detection Results")
    lines.append("=================================")
    lines.append("Total instructions: {}".format(len(instructions)))
    lines.append("Total cycles: {}".format(cycle))
    lines.append("Stall cycles: {}".format(stall_cycles))
    lines.append("Pipeline CPI: {:.2f}".format(cpi))
    lines.append("")
    lines.append("Cycle-by-cycle pipeline table:")
    lines.append("Cycle | IF     | ID     | EX     | MEM    | WB")
    lines.append("------|--------|--------|--------|--------|------")
    for row in timeline:
        lines.append("{:<5} | {:<6} | {:<6} | {:<6} | {:<6} | {:<6}".format(*row))

    lines.append("")
    lines.append("Hazards detected:")
    if len(hazard_log) == 0:
        lines.append("No RAW hazards detected.")
    else:
        for h in hazard_log:
            lines.append(h)

    output = "\n".join(lines)
    print(output)

    with open(log_file, "w") as f:
        f.write(output)

    return cycle, stall_cycles, cpi


def compare_programs(program_files):
    print("\nSummary Comparison")
    print("==================")
    for file in program_files:
        instructions = read_program(file)
        name = os.path.basename(file)
        log_name = os.path.join("results", name.replace(".txt", "_results.log"))
        cycles, stalls, cpi = run_pipeline(instructions, log_name)
        print("\n{} -> cycles: {}, stalls: {}, CPI: {:.2f}".format(name, cycles, stalls, cpi))


def main():
    if len(sys.argv) > 1:
        program_files = sys.argv[1:]
    else:
        program_files = [
            os.path.join("programs", "no_hazards.txt"),
            os.path.join("programs", "basic_hazards.txt"),
            os.path.join("programs", "heavy_hazards.txt")
        ]

    if not os.path.exists("results"):
        os.mkdir("results")

    compare_programs(program_files)


if __name__ == "__main__":
    main()
