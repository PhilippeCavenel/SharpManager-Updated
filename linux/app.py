"""Linux UI for the PC-1403 continuous cassette stream experiment.

Modified 6 October 2026 from the archived macOS V5.2 application:
Linux USB port discovery, English UI, setup guidance and startup diagnostics.
SharpManager: Copyright 2024 Wayne Venables / Codaris Computing.
See LICENSE-SharpManager.txt and ../NOTICE; PocketTools has separate terms.
"""

from pathlib import Path
import queue
import re
import subprocess
import sys
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from protocol import Driver


def resource_dir():
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))


TOOLS = resource_dir() / "PocketTools"


def run_tool(command, cwd):
    executable = TOOLS / command[0]
    if not executable.is_file():
        raise RuntimeError(f"Missing tool: {executable.name}. Run ./setup-linux.sh first.")
    result = subprocess.run([str(executable), *command[1:]], cwd=cwd,
                            capture_output=True, text=True, timeout=35)
    if result.returncode:
        raise RuntimeError(f"{executable.name} ({result.returncode}) :\n{result.stdout}\n{result.stderr}")


def check_basic(source):
    previous = 0
    for raw in source.splitlines():
        line = raw.strip()
        if not line:
            continue
        match = re.match(r"^(\d+)(.+)$", line)
        if not match or not previous < int(match[1]) <= 65279:
            raise ValueError(f"BASIC lines must have increasing line numbers: {line}")
        previous = int(match[1])
    if not previous:
        raise ValueError("The BASIC file is empty")


def encode_basic(path):
    source = Path(path).read_text(encoding="utf-8-sig")
    check_basic(source)
    name = re.sub("[^A-Z0-9]", "", Path(path).stem.upper())[:7] or "PROGRAM"
    with tempfile.TemporaryDirectory(prefix="sharp-basic-") as folder:
        work = Path(folder)
        (work / "source.bas").write_text(source, encoding="utf-8")
        run_tool(["bas2img", "--pc=1403", "source.bas", "program.img"], folder)
        run_tool(["bin2wav", "--pc=1403", "--tap", f"--name={name}",
                  "program.img", "program.tap"], folder)
        return (work / "program.tap").read_bytes()


def decode_basic(tape):
    if len(tape) < 10 or tape[0] not in (0x70, 0x72):
        raise ValueError("Protected or non-BASIC cassette; keep the .tap file")
    with tempfile.TemporaryDirectory(prefix="sharp-basic-") as folder:
        work = Path(folder)
        (work / "received.tap").write_bytes(tape)
        run_tool(["wav2bin", "--pc=1403", "--tap", "--type=bas",
                  "--utf8=yes", "--width=0", "received.tap", "received.bas"], folder)
        source = (work / "received.bas").read_text(encoding="utf-8-sig")
        check_basic(source)
        return source


def ports():
    from serial.tools import list_ports
    # USB serial adapters on Linux use ttyUSB (FTDI) or ttyACM. The editable
    # combobox also accepts a stable /dev/serial/by-id/... path typed by hand.
    found = {}
    for port in list_ports.comports(include_links=True):
        if port.device.startswith(("/dev/ttyUSB", "/dev/ttyACM", "/dev/serial/")):
            found[port.device] = getattr(port, "vid", None) == 0x0403
    return sorted(found, key=lambda device: (not found[device], device))


class Application:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SharpManager PC-1403 · Linux V5.2 continuous stream")
        self.root.geometry("760x520")
        self.events = queue.Queue()
        self.driver = Driver(lambda kind, data: self.events.put((kind, data)))
        self.busy = False
        self.port = tk.StringVar()
        top = ttk.Frame(self.root, padding=12)
        top.pack(fill="x")
        ttk.Label(top, text="FTDI port").pack(side="left")
        self.selection = ttk.Combobox(top, textvariable=self.port, width=32)
        self.selection.pack(side="left", padx=8)
        ttk.Button(top, text="Refresh", command=self.refresh).pack(side="left")
        ttk.Button(top, text="Connect", command=lambda: self.start("connect", self.port.get().strip())).pack(side="left", padx=4)
        ttk.Button(top, text="Disconnect", command=lambda: self.start("disconnect")).pack(side="left")
        ttk.Button(top, text="Ping", command=lambda: self.start("ping")).pack(side="left", padx=4)
        row = ttk.Frame(self.root, padding=(12, 2))
        row.pack(fill="x")
        ttk.Button(row, text="Send .tap", command=self.send_tap).pack(side="left")
        ttk.Button(row, text="Send BASIC .bas", command=self.send_basic).pack(side="left", padx=8)
        ttk.Button(row, text="Receive CSAVE", command=self.receive).pack(side="left")
        ttk.Label(self.root, text="Log and LPRINT output", padding=(12, 12, 12, 2)).pack(anchor="w")
        self.output = tk.Text(self.root, wrap="word", state="disabled")
        self.output.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.refresh()
        self.root.after(80, self.poll)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def append(self, message):
        self.output.configure(state="normal")
        self.output.insert("end", message)
        self.output.see("end")
        self.output.configure(state="disabled")

    def refresh(self):
        available = ports()
        self.selection["values"] = available
        # Keep manually entered by-id paths when refreshing the device list.
        if available and not self.port.get():
            self.port.set(available[0])

    def start(self, action, *args):
        if self.busy:
            return
        if action == "connect" and not args[0]:
            messagebox.showerror("FTDI port", "Choose the FTDI port, for example /dev/ttyUSB0")
            return
        self.busy = True
        self.driver.submit(action, *args)

    def send_tap(self):
        path = filedialog.askopenfilename(filetypes=[("Sharp cassette", "*.tap")])
        if path:
            self.confirm_send(lambda: Path(path).read_bytes())

    def send_basic(self):
        path = filedialog.askopenfilename(filetypes=[("BASIC program", "*.bas")])
        if path:
            self.confirm_send(lambda: encode_basic(path))

    def confirm_send(self, get_bytes):
        if self.busy:
            return
        try:
            tape = get_bytes()
        except Exception as exc:
            messagebox.showerror("Conversion", str(exc))
            return
        if messagebox.askokcancel("Load the PC-1403",
                                  "On the Sharp in RUN mode, enter CLOAD, then click OK to send."):
            self.start("send", tape)

    def receive(self):
        if self.busy:
            return
        messagebox.showinfo("Save from the PC-1403",
                            "Click OK, then enter CSAVE on the Sharp in RUN mode.\n"
                            "The application will save the .tap and, if possible, its BASIC source.")
        self.start("receive")

    def save_received(self, tape):
        path = filedialog.asksaveasfilename(defaultextension=".tap", initialfile="PROGRAM.tap",
                                            filetypes=[("Sharp cassette", "*.tap")])
        if not path:
            self.append("Save cancelled; no file was written.\n")
            return
        try:
            Path(path).write_bytes(tape)
        except OSError as exc:
            messagebox.showerror("Save cassette", str(exc))
            return
        self.append(f"Cassette saved: {path}\n")
        try:
            source = decode_basic(tape)
            basic_path = str(Path(path).with_suffix(".bas"))
            # Never silently replace an existing BASIC file.
            if Path(basic_path).exists():
                if not messagebox.askyesno("Existing file", f"Replace {basic_path}?"):
                    return
            Path(basic_path).write_text(source, encoding="utf-8")
            self.append(f"BASIC saved: {basic_path}\n")
        except Exception as exc:
            self.append(f"BASIC decoding unavailable: {exc}\nThe .tap file was kept.\n")

    def poll(self):
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "log":
                    self.append(value + "\n")
                elif kind == "print":
                    self.append(value)
                elif kind == "received":
                    self.save_received(value)
                elif kind == "error":
                    self.append("ERROR: " + value + "\n")
                    messagebox.showerror("SharpManager", value)
                elif kind == "done":
                    self.busy = False
        except queue.Empty:
            pass
        self.root.after(80, self.poll)

    def close(self):
        self.driver.submit("quit")
        self.root.destroy()


if __name__ == "__main__":
    if not sys.platform.startswith("linux"):
        sys.exit("Use the macOS or Windows version on this operating system.")
    try:
        Application().root.mainloop()
    except tk.TclError as exc:
        sys.exit(f"Cannot start the graphical interface: {exc}\n"
                 "Run SharpManager in an Ubuntu desktop session with python3-tk installed.")
