# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Go demo project for demonstrating **bpftrace** (BPF tracing) on Go binaries. The app runs a loop calling `Calculate` → `Multiply`, and bpftrace scripts attach uprobes/uretprobes to inspect arguments and return values at runtime.

## Build & Run

```bash
# Build (produces ./myapp binary)
go build -o myapp main.go

# Run the target application
./myapp

# Run bpftrace script (requires root, in a separate terminal)
sudo bpftrace bprftrace/trace.bt
```

## Architecture

- **`main.go`** — Single-file Go app with `Calculate` and `Multiply` functions. `Calculate` uses `//go:noinline` to prevent compiler inlining, which is required for uprobe attachment.
- **`bprftrace/trace.bt`** — bpftrace script that attaches uprobe/uretprobe to `main.Calculate` and `main.Multiply` in the compiled `myapp` binary. Reads function arguments via `reg("ax")`, `reg("bx")` and return values via `retval`.

## Key Constraints

- Functions traced by bpftrace **must** have `//go:noinline` to remain visible as symbols in the binary.
- The bpftrace script references `../myapp` as a relative path — run it from the `bprftrace/` directory, or adjust the path.
- Argument registers (`ax`, `bx`) follow the Go calling convention on x86_64 Linux.
