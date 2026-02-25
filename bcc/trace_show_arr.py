#!/usr/bin/env python3
"""
BCC script to trace service.showArr in bprf_demo Go binary.
Captures the []string slice argument and prints each string element.

Usage:
    # Build the server first
    cd /home/fenrir/code/lc/bprf_demo && go build -o myapp server.go

    # Run the server
    ./myapp

    # In another terminal, run this tracer (requires root)
    sudo python3 bprftrace/trace_show_arr.py ./myapp

    # Trigger the API
    curl 'http://localhost:8080/hello/arr?name=test'
"""

from bcc import BPF
import sys

BINARY = sys.argv[1] if len(sys.argv) > 1 else "./myapp"
SYMBOL = "bprf_demo/service.showArr"

bpf_program = """
#include <uapi/linux/ptrace.h>

#define MAX_STR_LEN  128
#define MAX_ELEMENTS 8

struct event_t {
    u32 pid;
    u32 slice_len;
    u32 slice_cap;
    u32 actual_elements;
    u64 str_lens[MAX_ELEMENTS];
    char str_data[MAX_ELEMENTS][MAX_STR_LEN];
};

// Use per-cpu array to avoid 512-byte stack limit
BPF_PERCPU_ARRAY(heap, struct event_t, 1);
BPF_PERF_OUTPUT(events);

int trace_show_arr(struct pt_regs *ctx) {
    int zero = 0;
    struct event_t *event = heap.lookup(&zero);
    if (!event) return 0;

    event->pid = bpf_get_current_pid_tgid() >> 32;

    // Go register-based calling convention (amd64, Go 1.17+):
    // []string param => AX = data pointer, BX = length, CX = capacity
    u64 slice_ptr = PT_REGS_PARM1(ctx);  // rdi mapped to AX in Go ABI
    u64 slice_len = PT_REGS_PARM2(ctx);  // rsi mapped to BX in Go ABI
    u64 slice_cap = PT_REGS_PARM3(ctx);  // rdx mapped to CX in Go ABI

    event->slice_len = (u32)slice_len;
    event->slice_cap = (u32)slice_cap;

    u32 n = (u32)slice_len;
    if (n > MAX_ELEMENTS) n = MAX_ELEMENTS;
    event->actual_elements = n;

    // Go string in memory: { *byte (8 bytes), len int (8 bytes) } = 16 bytes
    // The slice data pointer points to a contiguous array of these 16-byte structs
    #pragma unroll
    for (int i = 0; i < MAX_ELEMENTS; i++) {
        if (i < n) {
            u64 str_ptr = 0;
            u64 str_len = 0;

            // Read string header from slice element i
            bpf_probe_read_user(&str_ptr, sizeof(str_ptr),
                                (void *)(slice_ptr + i * 16));
            bpf_probe_read_user(&str_len, sizeof(str_len),
                                (void *)(slice_ptr + i * 16 + 8));

            event->str_lens[i] = str_len;

            // Read actual string bytes (fixed-size read, Python trims by str_len)
            if (str_ptr != 0) {
                u64 to_read = str_len < MAX_STR_LEN ? str_len : MAX_STR_LEN;
                bpf_probe_read_user(&event->str_data[i], to_read,
                                    (void *)str_ptr);
            }
        }
    }

    events.perf_submit(ctx, event, sizeof(*event));
    return 0;
}
"""

# Compile and attach
b = BPF(text=bpf_program)
b.attach_uprobe(name=BINARY, sym=SYMBOL, fn_name="trace_show_arr")

print(f"Tracing {SYMBOL} in {BINARY} ...")
print(f"Test:  curl 'http://localhost:8080/hello/arr?name=test'")
print(f"Press Ctrl+C to stop.\n")


def print_event(cpu, data, size):
    event = b["events"].event(data)
    print(f"[PID {event.pid}] showArr called  |  "
          f"len={event.slice_len}  cap={event.slice_cap}")

    for i in range(event.actual_elements):
        str_len = min(event.str_lens[i], MAX_STR_LEN)
        raw = bytes(event.str_data[i][:str_len])
        s = raw.decode("utf-8", errors="replace")
        print(f"  arr[{i}] (len={event.str_lens[i]}): \"{s}\"")
    print()


MAX_STR_LEN = 128

b["events"].open_perf_buffer(print_event)

try:
    while True:
        b.perf_buffer_poll()
except KeyboardInterrupt:
    print("\nDone.")
