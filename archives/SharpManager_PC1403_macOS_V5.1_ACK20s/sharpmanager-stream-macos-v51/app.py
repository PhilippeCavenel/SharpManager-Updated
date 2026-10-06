"""macOS UI for the PC-1403 continuous cassette stream experiment."""

import os
from pathlib import Path
import queue
import re
import subprocess
import sys
import tempfile
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from protocol import Driver


def resource_dir():
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))


TOOLS = resource_dir() / "PocketTools"


def run_tool(command, cwd):
    executable = TOOLS / command[0]
    if not executable.is_file():
        raise RuntimeError(f"Outil manquant : {executable.name}. Relance build-macos.command.")
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
            raise ValueError(f"Lignes BASIC numérotées et croissantes requises : {line}")
        previous = int(match[1])
    if not previous:
        raise ValueError("Le fichier BASIC est vide")


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
        raise ValueError("Cassette non BASIC ou protégée ; conserve le fichier .tap")
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
    return sorted({p.device for p in list_ports.comports() if p.device.startswith("/dev/cu.")})


class Application:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SharpManager PC-1403 · macOS V5.1 flux continu")
        self.root.geometry("760x520")
        self.events = queue.Queue()
        self.driver = Driver(lambda kind, data: self.events.put((kind, data)))
        self.busy = False
        self.port = tk.StringVar()
        top = ttk.Frame(self.root, padding=12)
        top.pack(fill="x")
        ttk.Label(top, text="Port FTDI").pack(side="left")
        self.selection = ttk.Combobox(top, textvariable=self.port, width=32)
        self.selection.pack(side="left", padx=8)
        ttk.Button(top, text="Actualiser", command=self.refresh).pack(side="left")
        ttk.Button(top, text="Connecter", command=lambda: self.start("connect", self.port.get())).pack(side="left", padx=4)
        ttk.Button(top, text="Déconnecter", command=lambda: self.start("disconnect")).pack(side="left")
        ttk.Button(top, text="Ping", command=lambda: self.start("ping")).pack(side="left", padx=4)
        row = ttk.Frame(self.root, padding=(12, 2))
        row.pack(fill="x")
        ttk.Button(row, text="Envoyer .tap", command=self.send_tap).pack(side="left")
        ttk.Button(row, text="Envoyer BASIC .bas", command=self.send_basic).pack(side="left", padx=8)
        ttk.Button(row, text="Recevoir CSAVE", command=self.receive).pack(side="left")
        ttk.Label(self.root, text="Journal et sortie LPRINT", padding=(12, 12, 12, 2)).pack(anchor="w")
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
        if available and self.port.get() not in available:
            self.port.set(next((p for p in available if "usbserial" in p.lower()), available[0]))

    def start(self, action, *args):
        if self.busy:
            return
        if action == "connect" and not args[0]:
            messagebox.showerror("Port FTDI", "Choisis le port /dev/cu.* du câble FTDI")
            return
        self.busy = action != "disconnect"
        self.driver.submit(action, *args)

    def send_tap(self):
        path = filedialog.askopenfilename(filetypes=[("Cassette Sharp", "*.tap")])
        if path:
            self.confirm_send(lambda: Path(path).read_bytes())

    def send_basic(self):
        path = filedialog.askopenfilename(filetypes=[("Programme BASIC", "*.bas")])
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
        if messagebox.askokcancel("Chargement du PC-1403",
                                  "Sur le Sharp en mode RUN, lance CLOAD puis appuie sur OK pour envoyer."):
            self.start("send", tape)

    def receive(self):
        if self.busy:
            return
        messagebox.showinfo("Sauvegarde du PC-1403",
                            "Clique sur OK, puis lance CSAVE sur le Sharp en mode RUN.\n"
                            "Le logiciel enregistrera le .tap et, si possible, le .bas correspondant.")
        self.start("receive")

    def save_received(self, tape):
        path = filedialog.asksaveasfilename(defaultextension=".tap", initialfile="PROGRAM.tap",
                                            filetypes=[("Cassette Sharp", "*.tap")])
        if not path:
            self.append("Réception conservée en mémoire ; aucun fichier enregistré.\n")
            return
        Path(path).write_bytes(tape)
        self.append(f"Cassette enregistrée : {path}\n")
        try:
            source = decode_basic(tape)
            basic_path = str(Path(path).with_suffix(".bas"))
            # Never silently replace an existing BASIC file.
            if Path(basic_path).exists():
                if not messagebox.askyesno("Fichier existant", f"Remplacer {basic_path} ?"):
                    return
            Path(basic_path).write_text(source, encoding="utf-8")
            self.append(f"BASIC enregistré : {basic_path}\n")
        except Exception as exc:
            self.append(f"Décodage BASIC indisponible : {exc}\nLe .tap est conservé.\n")

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
                    self.append("ERREUR : " + value + "\n")
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
    Application().root.mainloop()
