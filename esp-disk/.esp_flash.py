#!/usr/bin/env python3
"""
Low-level flasher used by ./flash — copies a staged directory tree onto a
MicroPython ESP32 over a single serial connection.

Why this exists instead of plain `mpremote cp`:
  On macOS, mpremote (pyserial) asserts DTR/RTS every time it OPENS the port,
  which trips the ESP32 auto-reset circuit and reboots the board. This project's
  boot.py then spends several seconds in a blocking Wi-Fi connect, so any fresh
  `mpremote` invocation gets locked out of the REPL ("could not enter raw repl").

This script:
  1. Opens the port ONCE with DTR/RTS deasserted, so the board is not reset.
  2. Patiently retries entering the raw REPL (sending Ctrl-C) through the boot
     window — so even if the board is mid-loop or mid-reboot, one attempt lands
     once it returns to an idle prompt.
  3. Recursively writes the staged files, then optionally soft-resets.

Usage:  .esp_flash.py <port> <stage_dir> <reset|noreset>
"""

import os
import sys
import time

import serial
from mpremote.transport_serial import SerialTransport, TransportError


def open_no_reset(port):
    """Open the serial port without pulsing DTR/RTS (no board reset)."""
    t = SerialTransport.__new__(SerialTransport)  # skip __init__'s resetting open
    t.in_raw_repl = False
    t.use_raw_paste = True
    t.device_name = port
    t.mounted = False

    s = serial.serial_for_url(
        port, do_not_open=True, baudrate=115200, timeout=None, interCharTimeout=1
    )
    # Deassert before opening so the auto-reset circuit sees no transition.
    s.dtr = False
    s.rts = False
    s.open()
    t.serial = s
    return t


def grab_repl(t, timeout=25):
    """Keep interrupting until the board yields an idle raw REPL."""
    deadline = time.time() + timeout
    warned = False
    while True:
        try:
            t.enter_raw_repl(soft_reset=False, timeout_overall=2)
            return
        except TransportError:
            if time.time() > deadline:
                raise
            if not warned:
                sys.stderr.write(
                    "\033[33m… board busy, interrupting — tap EN/RST if it hangs\033[0m\n"
                )
                sys.stderr.flush()
                warned = True
            time.sleep(0.15)


def put_tree(t, root):
    """Mirror the local staged tree onto the device root."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        rel = os.path.relpath(dirpath, root)
        remote_dir = "" if rel == "." else "/" + rel.replace(os.sep, "/")
        if remote_dir:
            try:
                t.fs_mkdir(remote_dir)
            except Exception:
                pass  # already exists
        for fn in sorted(filenames):
            local = os.path.join(dirpath, fn)
            remote = (remote_dir + "/" + fn) if remote_dir else "/" + fn
            with open(local, "rb") as fh:
                data = fh.read()
            t.fs_writefile(remote, data)
            print("  → %s (%d bytes)" % (remote.lstrip("/"), len(data)))


def get_tree(t, remote_dir, dest):
    """Recursively copy the device tree under remote_dir into local dest."""
    for entry in t.fs_listdir(remote_dir):
        remote = remote_dir.rstrip("/") + "/" + entry.name
        local = os.path.join(dest, remote.lstrip("/").replace("/", os.sep))
        if entry.st_mode & 0x4000:  # directory bit
            os.makedirs(local, exist_ok=True)
            get_tree(t, remote, dest)
        else:
            data = t.fs_readfile(remote)
            os.makedirs(os.path.dirname(local), exist_ok=True)
            with open(local, "wb") as fh:
                fh.write(data)
            print("  ← %s (%d bytes)" % (remote.lstrip("/"), len(data)))


def hard_reset(t):
    """Pulse EN (via RTS) to hardware-reboot the board — no REPL needed."""
    t.serial.dtr = False  # GPIO0 high -> normal boot (not the bootloader)
    t.serial.rts = True   # EN low  -> hold in reset
    time.sleep(0.1)
    t.serial.rts = False  # EN high -> release -> reboot


def cmd_flash(port, stage, reset):
    t = open_no_reset(port)
    try:
        grab_repl(t)
        put_tree(t, stage)
        t.exit_raw_repl()
        if reset:
            t.serial.write(b"\r\x04")  # Ctrl-D: soft reset to run the new code
    finally:
        t.close()


def cmd_backup(port, dest):
    """Pull the entire device filesystem into local dest, then resume the app."""
    t = open_no_reset(port)
    try:
        grab_repl(t)
        get_tree(t, "/", dest)
        t.exit_raw_repl()
        t.serial.write(b"\r\x04")  # soft reset: leave the board running as found
    finally:
        t.close()


def cmd_stop(port):
    """Interrupt the running program and leave the board paused at the REPL."""
    t = open_no_reset(port)
    try:
        grab_repl(t)        # Ctrl-C breaks the asyncio loop (main.py catches it)
        t.exit_raw_repl()   # back to the friendly REPL, halted, NOT reset
    finally:
        t.close()


def cmd_boot(port):
    """Hardware-reboot the board."""
    t = open_no_reset(port)
    try:
        hard_reset(t)
    finally:
        t.close()


def main():
    argv = sys.argv[1:]
    if len(argv) < 2:
        sys.stderr.write(
            "usage: .esp_flash.py <port> flash <stage_dir> <reset|noreset>\n"
            "       .esp_flash.py <port> backup <dest_dir>\n"
            "       .esp_flash.py <port> stop\n"
            "       .esp_flash.py <port> boot\n"
        )
        return 2
    port, cmd = argv[0], argv[1]

    if cmd == "flash":
        cmd_flash(port, argv[2], argv[3] == "reset")
    elif cmd == "backup":
        cmd_backup(port, argv[2])
    elif cmd == "stop":
        cmd_stop(port)
    elif cmd == "boot":
        cmd_boot(port)
    else:
        sys.stderr.write("unknown command: %s\n" % cmd)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
