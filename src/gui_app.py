from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from src.app_services import PreviewRow, apply_preview_plan, build_preview_rows
from src.gui_viewmodel import (
    format_apply_summary,
    parse_extensions_input,
    validate_folder_path,
)


WARNING_TEXT = {
    "none": "None",
    "reserved-name": "Reserved name",
    "name-conflict-risk": "Conflict risk",
    "hidden-dotfile": "Hidden dotfile",
}


class RenamerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("File Name Renamer")
        self.root.geometry("1000x640")
        self.root.minsize(860, 520)

        self.folder_var = tk.StringVar(value=str(Path.cwd()))
        self.recursive_var = tk.BooleanVar(value=True)
        self.include_hidden_var = tk.BooleanVar(value=False)
        self.separator_var = tk.StringVar(value="_")
        self.case_var = tk.StringVar(value="lower")
        self.extensions_var = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="Select a folder and click Preview.")

        self.current_root: Path | None = None
        self.preview_rows: list[PreviewRow] = []

        self._build_layout()

    def _build_layout(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)

        path_frame = ttk.Frame(self.root, padding=(12, 12, 12, 6))
        path_frame.grid(row=0, column=0, sticky="ew")
        path_frame.columnconfigure(1, weight=1)

        ttk.Label(path_frame, text="Folder").grid(row=0, column=0, padx=(0, 8), sticky="w")
        ttk.Entry(path_frame, textvariable=self.folder_var).grid(row=0, column=1, sticky="ew")
        ttk.Button(path_frame, text="Browse", command=self._on_browse).grid(
            row=0,
            column=2,
            padx=(8, 0),
            sticky="e",
        )

        options = ttk.LabelFrame(self.root, text="Options", padding=(12, 10))
        options.grid(row=1, column=0, padx=12, pady=(0, 8), sticky="ew")
        for col in range(6):
            options.columnconfigure(col, weight=1)

        ttk.Checkbutton(options, text="Recursive", variable=self.recursive_var).grid(
            row=0,
            column=0,
            sticky="w",
        )
        ttk.Checkbutton(options, text="Include Hidden", variable=self.include_hidden_var).grid(
            row=0,
            column=1,
            sticky="w",
        )
        ttk.Label(options, text="Separator").grid(row=0, column=2, padx=(8, 4), sticky="e")
        ttk.Combobox(
            options,
            textvariable=self.separator_var,
            values=["_", "-", "."],
            width=6,
            state="readonly",
        ).grid(row=0, column=3, sticky="w")
        ttk.Label(options, text="Case").grid(row=0, column=4, padx=(8, 4), sticky="e")
        ttk.Combobox(
            options,
            textvariable=self.case_var,
            values=["lower", "upper", "preserve"],
            width=10,
            state="readonly",
        ).grid(row=0, column=5, sticky="w")

        ttk.Label(options, text="Extensions (space/comma separated)").grid(
            row=1,
            column=0,
            columnspan=2,
            pady=(8, 0),
            sticky="w",
        )
        ttk.Entry(options, textvariable=self.extensions_var).grid(
            row=1,
            column=2,
            columnspan=4,
            pady=(8, 0),
            sticky="ew",
        )

        table_frame = ttk.Frame(self.root, padding=(12, 0, 12, 6))
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        self.table = ttk.Treeview(
            table_frame,
            columns=("source", "target", "warning"),
            show="headings",
            height=16,
        )
        self.table.heading("source", text="Source")
        self.table.heading("target", text="Target")
        self.table.heading("warning", text="Warning")
        self.table.column("source", width=360, anchor="w")
        self.table.column("target", width=360, anchor="w")
        self.table.column("warning", width=180, anchor="w")
        self.table.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.table.configure(yscrollcommand=scrollbar.set)

        action_frame = ttk.Frame(self.root, padding=(12, 6, 12, 12))
        action_frame.grid(row=3, column=0, sticky="ew")
        action_frame.columnconfigure(0, weight=1)

        ttk.Label(action_frame, textvariable=self.status_var).grid(row=0, column=0, sticky="w")
        ttk.Button(action_frame, text="Preview", command=self._on_preview).grid(
            row=0,
            column=1,
            padx=(8, 0),
        )
        self.apply_btn = ttk.Button(action_frame, text="Apply", command=self._on_apply)
        self.apply_btn.grid(row=0, column=2, padx=(8, 0))
        self.apply_btn.state(["disabled"])

    def _on_browse(self) -> None:
        selected = filedialog.askdirectory(initialdir=self.folder_var.get() or str(Path.cwd()))
        if selected:
            self.folder_var.set(selected)

    def _on_preview(self) -> None:
        ok, path_or_error = validate_folder_path(self.folder_var.get())
        if not ok:
            messagebox.showerror("Invalid folder", path_or_error)
            return

        root = Path(path_or_error)
        extensions = parse_extensions_input(self.extensions_var.get())

        try:
            rows = build_preview_rows(
                root=root,
                recursive=self.recursive_var.get(),
                include_hidden=self.include_hidden_var.get(),
                extensions=extensions,
                separator=self.separator_var.get(),
                case_mode=self.case_var.get(),
            )
        except Exception as exc:
            messagebox.showerror("Preview failed", str(exc))
            return

        self.current_root = root
        self.preview_rows = rows
        self._render_rows()

        if rows:
            self.status_var.set(f"Preview ready: {len(rows)} file(s) will be renamed.")
            self.apply_btn.state(["!disabled"])
        else:
            self.status_var.set("No filename changes are needed with current options.")
            self.apply_btn.state(["disabled"])

    def _render_rows(self) -> None:
        for child in self.table.get_children():
            self.table.delete(child)

        root = self.current_root
        for row in self.preview_rows:
            self.table.insert(
                "",
                "end",
                values=(
                    self._display_path(row.source, root),
                    self._display_path(row.target, root),
                    WARNING_TEXT.get(row.warning, row.warning),
                ),
            )

    @staticmethod
    def _display_path(path: Path, root: Path | None) -> str:
        if root is None:
            return str(path)
        try:
            return str(path.relative_to(root))
        except ValueError:
            return str(path)

    def _on_apply(self) -> None:
        if not self.preview_rows:
            messagebox.showinfo("Nothing to apply", "Run preview first.")
            return

        confirmed = messagebox.askyesno(
            "Apply rename",
            f"Apply changes to {len(self.preview_rows)} file(s)?",
        )
        if not confirmed:
            return

        summary = apply_preview_plan(self.preview_rows)
        messagebox.showinfo("Rename result", format_apply_summary(summary))
        self._on_preview()


def main() -> int:
    root = tk.Tk()
    style = ttk.Style(root)
    if "vista" in style.theme_names():
        style.theme_use("vista")
    app = RenamerApp(root)
    _ = app
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
