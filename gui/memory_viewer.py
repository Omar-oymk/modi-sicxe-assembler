"""
memory_viewer.py – SIC/XE Memory Visualization Loader
Retro-cyberpunk aesthetic. Single window. Pure Tkinter.
"""

import tkinter as tk
from tkinter import font as tkfont
from pathlib import Path

# ── HTME PARSER ───────────────────────────────────────────────────────────────
class HTMEParser:
    def __init__(self, filepath):
        self.filepath = Path(filepath)

    def parse(self):
        records = []
        for raw in self.filepath.read_text(encoding="utf-8", errors="ignore").splitlines():
            r = self._line(raw.strip())
            if r:
                records.append(r)
        return records

    def _line(self, line):
        if not line:
            return None
        p = line.split(".")
        t = p[0].strip().upper()
        g = lambda i, d="000000": p[i].strip() if i < len(p) else d
        if t == "H":
            return {"type":"H","name":g(1,""),"start":g(2),"length":g(3)}
        if t == "T":
            return {"type":"T","start_addr":g(1),"byte_count":g(2,"00"),
                    "object_code":"".join(x.strip() for x in p[3:]).upper()}
        if t == "M":
            return {"type":"M","start_addr":g(1),"half_bytes":g(2,"00"),"sign":g(3,"+")}
        if t == "E":
            return {"type":"E","entry":g(1)}
        return None


# ── MEMORY LOADER ─────────────────────────────────────────────────────────────
MEM = 1 << 20  # 1 MB

class MemoryLoader:
    def __init__(self):
        self.reset()

    def reset(self):
        self.memory = ["00"] * MEM
        self.states = ["zero"] * MEM   # "zero" | "loaded" | "modified"
        self.program_name = self.program_start = self.program_len = 0
        self.entry_point = self.bytes_loaded = self.mod_count = 0

    def load(self, records):
        self.reset()
        h = next((r for r in records if r["type"]=="H"), None)
        e = next((r for r in records if r["type"]=="E"), None)
        if h:
            self.program_name  = h["name"]
            self.program_start = int(h["start"],  16)
            self.program_len   = int(h["length"], 16)
        for r in records:
            if r["type"] == "T": self._text(r)
        for r in records:
            if r["type"] == "M": self._mod(r)
        if e:
            self.entry_point = int(e["entry"], 16)

    def _text(self, rec):
        addr = int(rec["start_addr"], 16)
        code = rec["object_code"]
        for i in range(0, len(code)-1, 2):
            if addr < MEM:
                self.memory[addr] = code[i:i+2]
                self.states[addr] = "loaded"
                addr += 1
                self.bytes_loaded += 1

    def _mod(self, rec):
        start = int(rec["start_addr"], 16)
        hb    = int(rec["half_bytes"],  16)
        sign  = -1 if rec.get("sign","+").startswith("-") else 1
        nb    = (hb+1)//2
        fb    = hb*4
        tb    = nb*8
        sr    = tb-fb
        mask  = (1<<fb)-1
        raw   = "".join(self.memory[start+i] if start+i<MEM else "00" for i in range(nb))
        val   = int(raw,16)
        field = (((val>>sr)&mask) + sign*self.program_start) & mask
        val   = (val & ~(mask<<sr)) | (field<<sr)
        new   = f"{val:0{nb*2}X}"
        for i in range(nb):
            self.memory[start+i] = new[i*2:i*2+2]
            self.states[start+i] = "modified"
        self.mod_count += 1

    def written_range(self):
        first, last = MEM, 0
        for i,s in enumerate(self.states):
            if s != "zero":
                if i < first: first = i
                if i > last:  last  = i
        return (0,0) if first>last else (first,last)


# ── COLOUR PALETTES ───────────────────────────────────────────────────────────
CYBER = {
    "bg":          "#0a0118",
    "panel":       "#0f0328",
    "header_bg":   "#130435",
    "border":      "#00d4ff",
    "border2":     "#7b2fff",
    "text":        "#e0e8ff",
    "muted":       "#4a6080",
    "addr":        "#ffd700",
    "loaded_bg":   "#002233",
    "loaded_fg":   "#00ffcc",
    "modified_bg": "#1a0033",
    "modified_fg": "#ff6bc8",
    "zero_fg":     "#1e1240",
    "hover_bg":    "#7b2fff",
    "hover_fg":    "#ffffff",
    "col_fg":      "#00d4ff",
    "title_fg":    "#ffffff",
    "row_alt":     "#0c021e",
    "status_bg":   "#050112",
    "btn_bg":      "#1a0635",
    "btn_fg":      "#00d4ff",
    "btn_act":     "#7b2fff",
    "entry_bg":    "#060120",
    "entry_fg":    "#00ffcc",
    "sep":         "#00d4ff",
}
CLASSIC = {
    "bg":          "#0d1117",
    "panel":       "#161b22",
    "header_bg":   "#21262d",
    "border":      "#30363d",
    "border2":     "#388bfd",
    "text":        "#e6edf3",
    "muted":       "#8b949e",
    "addr":        "#f0b429",
    "loaded_bg":   "#0d2137",
    "loaded_fg":   "#58a6ff",
    "modified_bg": "#1e1040",
    "modified_fg": "#d2a8ff",
    "zero_fg":     "#21262d",
    "hover_bg":    "#2d333b",
    "hover_fg":    "#ffffff",
    "col_fg":      "#79c0ff",
    "title_fg":    "#58a6ff",
    "row_alt":     "#0f1318",
    "status_bg":   "#010409",
    "btn_bg":      "#21262d",
    "btn_fg":      "#e6edf3",
    "btn_act":     "#30363d",
    "entry_bg":    "#0d1117",
    "entry_fg":    "#e6edf3",
    "sep":         "#30363d",
}

ADDR_W  = 80    # px – address column fixed width
CELL_H  = 24    # px – row height
HDR_H   = 28    # px – column-header row height


# ── APP ───────────────────────────────────────────────────────────────────────
class MemoryViewerApp:
    def __init__(self, root):
        self.root   = root
        self.C      = CYBER
        self.loader = MemoryLoader()
        self.parser = HTMEParser(
            Path(__file__).parent.parent / "output" / "HTME.txt"
        )
        self.rows        = []
        self.hovered     = None
        self.cell_rects  = {}
        self.cell_texts  = {}
        self._cell_w     = 36   # computed dynamically

        self._build()
        self._load()

    # ── build UI ──────────────────────────────────────────────────────────────
    def _build(self):
        C = self.C
        r = self.root
        r.title("SIC/XE MEMORY VIEWER")
        r.configure(bg=C["bg"])
        r.minsize(800, 480)

        self.f_mono  = tkfont.Font(family="Courier New", size=11, weight="bold")
        self.f_title = tkfont.Font(family="Courier New", size=13, weight="bold")
        self.f_ui    = tkfont.Font(family="Courier New", size=10)
        self.f_small = tkfont.Font(family="Courier New", size=9)

        # ── top border line (decorative) ──────────────────────────────────
        self._top_line = tk.Frame(r, bg=C["border"], height=2)
        self._top_line.pack(fill="x")

        # ── header ────────────────────────────────────────────────────────
        self._hdr = tk.Frame(r, bg=C["header_bg"])
        self._hdr.pack(fill="x")

        tk.Label(self._hdr, text="◆ SIC/XE MEMORY VIEWER",
                 font=self.f_title, bg=C["header_bg"], fg=C["title_fg"],
                 padx=14, pady=8).pack(side="left")

        tk.Label(self._hdr, text="HTME LOADER · HEX DUMP",
                 font=self.f_ui, bg=C["header_bg"], fg=C["muted"],
                 pady=8).pack(side="left")

        # theme toggle on the right
        self._theme_btn = tk.Button(
            self._hdr, text="◈ DARK", command=self._toggle_theme,
            font=self.f_ui, bg=C["btn_bg"], fg=C["btn_fg"],
            activebackground=C["btn_act"], relief="flat", padx=10, cursor="hand2")
        self._theme_btn.pack(side="right", padx=14, pady=6)

        # ── toolbar ───────────────────────────────────────────────────────
        self._tb = tk.Frame(r, bg=C["panel"])
        self._tb.pack(fill="x")

        tk.Label(self._tb, text="JUMP:", font=self.f_ui,
                 bg=C["panel"], fg=C["col_fg"], padx=12).pack(side="left")
        self._jump_var = tk.StringVar()
        self._jump_ent = tk.Entry(
            self._tb, textvariable=self._jump_var, width=8,
            font=self.f_mono, bg=C["entry_bg"], fg=C["entry_fg"],
            insertbackground=C["entry_fg"], relief="flat", bd=3)
        self._jump_ent.pack(side="left", pady=5, ipady=2)
        self._jump_ent.bind("<Return>", lambda _: self._jump())

        for txt, cmd in [("GO", self._jump), ("⟳ RELOAD", self._load)]:
            b = tk.Button(self._tb, text=txt, command=cmd, font=self.f_ui,
                          bg=C["btn_bg"], fg=C["btn_fg"],
                          activebackground=C["btn_act"],
                          relief="flat", padx=10, cursor="hand2")
            b.pack(side="left", padx=4, pady=5, ipady=2)

        self._stats_lbl = tk.Label(self._tb, text="", font=self.f_small,
                                   bg=C["panel"], fg=C["muted"])
        self._stats_lbl.pack(side="right", padx=14)

        # ── border ────────────────────────────────────────────────────────
        tk.Frame(r, bg=C["border"], height=2).pack(fill="x")

        # ── fixed column header canvas ─────────────────────────────────────
        self._col_cv = tk.Canvas(r, bg=C["header_bg"], height=HDR_H,
                                 highlightthickness=0)
        self._col_cv.pack(fill="x")

        tk.Frame(r, bg=C["border2"], height=1).pack(fill="x")

        # ── scrollable hex grid (fills rest of window) ────────────────────
        self._grid_frame = tk.Frame(r, bg=C["bg"])
        self._grid_frame.pack(fill="both", expand=True)

        self._vsb = tk.Scrollbar(self._grid_frame, orient="vertical",
                                  bg=C["panel"], troughcolor=C["bg"],
                                  width=12)
        self._vsb.pack(side="right", fill="y")

        self._cv = tk.Canvas(self._grid_frame, bg=C["bg"],
                              highlightthickness=0,
                              yscrollcommand=self._vsb.set)
        self._cv.pack(side="left", fill="both", expand=True)
        self._vsb.config(command=self._cv.yview)

        self._cv.bind("<Motion>",     self._hover)
        self._cv.bind("<Leave>",      self._leave)
        self._cv.bind("<MouseWheel>", lambda e:
                      self._cv.yview_scroll(-1*(e.delta//120), "units"))
        self._cv.bind("<Configure>",  self._on_resize)

        # ── bottom border ─────────────────────────────────────────────────
        tk.Frame(r, bg=C["border"], height=2).pack(fill="x")

        # ── status bar ────────────────────────────────────────────────────
        self._sb = tk.Frame(r, bg=C["status_bg"])
        self._sb.pack(fill="x")

        self._hover_lbl = tk.Label(
            self._sb, text="▸  HOVER OVER A BYTE TO INSPECT",
            font=self.f_small, bg=C["status_bg"], fg=C["muted"],
            anchor="w", padx=12, pady=4)
        self._hover_lbl.pack(side="left")

        self._right_lbl = tk.Label(
            self._sb, text="", font=self.f_small,
            bg=C["status_bg"], fg=C["muted"], anchor="e", padx=12)
        self._right_lbl.pack(side="right")

    # ── data ──────────────────────────────────────────────────────────────────
    def _load(self):
        try:
            records = self.parser.parse()
            self.loader.load(records)
        except FileNotFoundError as ex:
            self._hover_lbl.config(text=f"⚠  {ex}")
            return
        first, last = self.loader.written_range()
        rs = (first // 16) * 16
        re = ((last  // 16) + 1) * 16
        self.rows = list(range(rs, re, 16))
        self._draw_col_header()
        self._render()
        lo = self.loader
        self._stats_lbl.config(
            text=(f"PROG: {lo.program_name}  START:{lo.program_start:06X}"
                  f"  LEN:{lo.program_len:06X}  BYTES:{lo.bytes_loaded}"
                  f"  MODS:{lo.mod_count}"))
        self._right_lbl.config(
            text=f"ENTRY:{lo.entry_point:06X}  ROWS:{len(self.rows)}")

    # ── column header ─────────────────────────────────────────────────────────
    def _draw_col_header(self):
        cv = self._col_cv
        C  = self.C
        cv.delete("all")
        cv.config(bg=C["header_bg"])
        w  = cv.winfo_width() or 900
        cw = self._cell_w
        ym = HDR_H // 2

        cv.create_text(ADDR_W//2, ym, text="ADDRESS",
                       font=self.f_small, fill=C["muted"], anchor="center")
        cv.create_line(ADDR_W, 0, ADDR_W, HDR_H, fill=C["border"], width=1)

        x0 = ADDR_W + 4
        for col in range(16):
            cx = x0 + col*cw + cw//2
            cv.create_text(cx, ym, text=f"{col:02X}",
                           font=self.f_mono, fill=C["col_fg"], anchor="center")

    # ── grid ──────────────────────────────────────────────────────────────────
    def _render(self):
        cv = self.C
        canvas = self._cv
        canvas.delete("all")
        self.cell_rects.clear()
        self.cell_texts.clear()
        self.hovered = None

        if not self.rows:
            canvas.create_text(20, 20, text="NO DATA — check output/HTME.txt",
                               fill=cv["muted"], font=self.f_mono, anchor="nw")
            return

        # compute cell width from canvas width
        cw_total = canvas.winfo_width() or 900
        cw = max(28, (cw_total - ADDR_W - 4) // 16)
        self._cell_w = cw

        total_h = len(self.rows) * CELL_H
        total_w = ADDR_W + 4 + 16*cw
        canvas.config(scrollregion=(0, 0, total_w, total_h))

        mem    = self.loader.memory
        states = self.loader.states
        C      = self.C

        for ri, base in enumerate(self.rows):
            y0 = ri * CELL_H
            ym = y0 + CELL_H//2

            # alternating row bg
            if ri % 2 == 0:
                canvas.create_rectangle(0, y0, total_w, y0+CELL_H,
                                        fill=C["row_alt"], outline="")

            # address
            canvas.create_text(ADDR_W-6, ym, text=f"{base:06X}",
                               font=self.f_mono, fill=C["addr"], anchor="e")
            canvas.create_line(ADDR_W, y0, ADDR_W, y0+CELL_H,
                               fill=C["border"], width=1)

            x0 = ADDR_W + 4
            for col in range(16):
                addr  = base + col
                byte  = mem[addr]    if addr < MEM else "00"
                state = states[addr] if addr < MEM else "zero"

                cx  = x0 + col*cw
                cxm = cx + cw//2

                bg = self._bg(state)
                fg = self._fg(state)

                rid = canvas.create_rectangle(
                    cx+1, y0+2, cx+cw-1, y0+CELL_H-2,
                    fill=bg, outline="")
                tid = canvas.create_text(
                    cxm, ym, text=byte,
                    font=self.f_mono, fill=fg, anchor="center")

                self.cell_rects[(ri, col)] = rid
                self.cell_texts[(ri, col)] = tid

        # redraw col header with correct cw
        self._draw_col_header()

    # ── colours ───────────────────────────────────────────────────────────────
    def _bg(self, state):
        return {"loaded": self.C["loaded_bg"],
                "modified": self.C["modified_bg"]}.get(state, "")

    def _fg(self, state):
        return {"loaded":   self.C["loaded_fg"],
                "modified": self.C["modified_fg"],
                "zero":     self.C["zero_fg"]}.get(state, self.C["muted"])

    # ── hover ─────────────────────────────────────────────────────────────────
    def _hover(self, event):
        canvas = self._cv
        C      = self.C
        cx     = canvas.canvasx(event.x)
        cy     = canvas.canvasy(event.y)
        x0     = ADDR_W + 4
        cw     = self._cell_w

        ri  = int(cy // CELL_H)
        col = int((cx - x0) // cw) if cx >= x0 else -1

        if 0 <= ri < len(self.rows) and 0 <= col <= 15:
            cell = (ri, col)
            if cell != self.hovered:
                if self.hovered:
                    self._restore(*self.hovered)
                self.hovered = cell
                rid = self.cell_rects.get(cell)
                tid = self.cell_texts.get(cell)
                if rid: canvas.itemconfig(rid, fill=C["hover_bg"])
                if tid: canvas.itemconfig(tid, fill=C["hover_fg"])

            addr  = self.rows[ri] + col
            byte  = self.loader.memory[addr] if addr < MEM else "00"
            state = self.loader.states[addr]  if addr < MEM else "zero"
            dec   = int(byte, 16)
            self._hover_lbl.config(
                text=f"▸  ADDR: {addr:06X}h   VAL: {byte}h = {dec}d   [{state.upper()}]")
        else:
            if self.hovered:
                self._restore(*self.hovered)
                self.hovered = None
            self._hover_lbl.config(text="▸  HOVER OVER A BYTE TO INSPECT")

    def _leave(self, _e):
        if self.hovered:
            self._restore(*self.hovered)
            self.hovered = None
        self._hover_lbl.config(text="▸  HOVER OVER A BYTE TO INSPECT")

    def _restore(self, ri, col):
        addr  = self.rows[ri] + col if ri < len(self.rows) else 0
        state = self.loader.states[addr] if addr < MEM else "zero"
        rid   = self.cell_rects.get((ri, col))
        tid   = self.cell_texts.get((ri, col))
        if rid: self._cv.itemconfig(rid, fill=self._bg(state))
        if tid: self._cv.itemconfig(tid, fill=self._fg(state))

    # ── resize ────────────────────────────────────────────────────────────────
    def _on_resize(self, _e):
        if self.rows:
            self._render()

    # ── jump ──────────────────────────────────────────────────────────────────
    def _jump(self):
        raw = self._jump_var.get().strip().lstrip("0xX")
        if not raw:
            return
        try:
            addr = int(raw, 16)
            base = (addr // 16) * 16
            if base not in self.rows:
                self._hover_lbl.config(text=f"⚠  ADDRESS {addr:06X}h NOT IN LOADED RANGE")
                return
            ri   = self.rows.index(base)
            frac = (ri * CELL_H) / (len(self.rows) * CELL_H) if self.rows else 0
            self._cv.yview_moveto(frac)
            self._flash((ri, addr % 16))
        except ValueError:
            self._hover_lbl.config(text="⚠  INVALID HEX ADDRESS")

    def _flash(self, cell, n=6):
        cv  = self._cv
        rid = self.cell_rects.get(cell)
        tid = self.cell_texts.get(cell)
        if not rid:
            return
        colors = [self.C["addr"], self.C["hover_bg"]] * (n // 2)
        def step(i=0):
            if i >= len(colors):
                self._restore(*cell)
                return
            cv.itemconfig(rid, fill=colors[i])
            if tid: cv.itemconfig(tid, fill="#ffffff")
            self.root.after(110, step, i+1)
        step()

    # ── theme ─────────────────────────────────────────────────────────────────
    def _toggle_theme(self):
        self.C = CLASSIC if self.C is CYBER else CYBER
        label  = "◈ CYBER" if self.C is CLASSIC else "◈ DARK"
        for w in self.root.winfo_children():
            w.destroy()
        self._build()
        self._theme_btn.config(text=label)
        self._load()


def main():
    root = tk.Tk()
    # Start with a default size, but allow it to be overridden by the window manager
    try:
        root.state()
    except Exception:
        root.geometry("1200x700")
    MemoryViewerApp(root)
    root.mainloop()

# ── ENTRY POINT ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()