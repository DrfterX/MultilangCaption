#!/usr/bin/env python3
"""
Subtitle Display Window — borderless, resizable, semi-transparent overlay.
Accepts optional recognizer command after '--' to auto-manage the process.
"""

import tkinter as tk
from tkinter import Menu
import os, sys, json, subprocess, signal

STATUS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'subtitle_status.txt')
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'subtitle_config.json')

COLOR_PRESETS = [
    ("纯黑", "#000000"), ("深灰", "#1a1a1a"), ("墨蓝", "#0d1b2a"),
    ("深绿", "#0b1a10"), ("深紫", "#1a0f2e"), ("咖啡", "#1e130c"),
    ("暗红", "#1a0c0c"), ("奶油", "#fff8e7"), ("珍珠白", "#f5f0e8"),
    ("柔绿", "#e8f0e3"), ("暖黄", "#fef9e7"), ("淡蓝", "#e8f0fe"),
    ("浅紫", "#f0e8f5"), ("浅粉", "#fde8ec"),
]

FONT_COLOR_PRESETS = [
    ("纯白", "#FFFFFF"), ("浅灰", "#CCCCCC"), ("亮黄", "#FFD700"),
    ("亮绿", "#00FF88"), ("亮蓝", "#66CCFF"), ("亮粉", "#FF99CC"),
    ("橙色", "#FF9933"), ("纯黑", "#000000"), ("深灰", "#444444"),
    ("暗红", "#CC3333"), ("暗蓝", "#3366CC"),
]

DEFAULTS = {
    "font_size": 28, "opacity": 0.82, "always_on_top": True,
    "bg_color": "#0d1b2a", "fg_color": "#FFFFFF",
    "font_family": "Microsoft YaHei",
}

GRIP  = 8   # px — resize edge zone
MIN_W = 200
MIN_H = 40


def load_config():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return {**DEFAULTS, **json.load(f)}
    except: return dict(DEFAULTS)

def save_config(cfg):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except: pass


class SubtitleWindow:
    def __init__(self, recognizer_cmd=None):
        self.cfg = load_config()
        self._last_content = ""
        self._resize_edge = None
        self._resize_start = (0,0,0,0,0,0)
        self._dx = self._dy = 0
        self.running = True
        self._proc = None                # recognizer subprocess
        self._recognizer_cmd = recognizer_cmd

        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.configure(bg=self.cfg["bg_color"])
        self.root.attributes('-alpha', self.cfg["opacity"])
        self.root.attributes('-topmost', self.cfg["always_on_top"])

        bc = self._lighter(self.cfg["bg_color"], 35)
        self.outer = tk.Frame(self.root, bg=bc, bd=0, highlightthickness=0)
        self.outer.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        self.inner = tk.Frame(self.outer, bg=self.cfg["bg_color"], bd=0)
        self.inner.pack(fill=tk.BOTH, expand=True)

        ft = (self.cfg["font_family"], self.cfg["font_size"])
        self.text = tk.Text(
            self.inner, font=ft, fg=self.cfg["fg_color"], bg=self.cfg["bg_color"],
            wrap=tk.CHAR, relief=tk.FLAT, borderwidth=0, highlightthickness=0,
            state=tk.DISABLED, padx=12, pady=10, width=1, height=1,
        )
        self.text.pack(fill=tk.BOTH, expand=True)

        geo = self.cfg.get("geometry", "800x180+200+150")
        try:              self.root.geometry(geo)
        except Exception: self.root.geometry("800x180+200+150")

        for w in (self.root, self.outer, self.inner, self.text):
            w.bind("<Button-1>", self._on_left_down)
            w.bind("<B1-Motion>", self._on_left_drag)
            w.bind("<Motion>", self._on_motion)
            w.bind("<Button-3>", self._show_menu)

        self.root.bind("<Leave>", self._on_leave)
        self.root.bind("<Configure>", lambda e: self._redraw_if_needed())
        self.root.bind("<Control-equal>", lambda e: self.font_bigger())
        self.root.bind("<Control-plus>",  lambda e: self.font_bigger())
        self.root.bind("<Control-minus>", lambda e: self.font_smaller())
        self.root.bind("<Control-Right>", lambda e: self.opacity_up())
        self.root.bind("<Control-Left>",  lambda e: self.opacity_down())
        self.root.bind("<Escape>",        lambda e: self._on_close())

        self._build_menu()

    # ─── colour ─────────────────────────────────────────────────
    @staticmethod
    def _lighter(h, amt=30):
        try:
            r,g,b = int(h[1:3],16),int(h[3:5],16),int(h[5:7],16)
            return f'#{min(r+amt,255):02x}{min(g+amt,255):02x}{min(b+amt,255):02x}'
        except: return '#444'
    @staticmethod
    def _is_dark(h):
        try:
            r,g,b = int(h[1:3],16),int(h[3:5],16),int(h[5:7],16)
            return (r+g+b)/3<128
        except: return True

    def _apply_colors(self, bg):
        self.cfg["bg_color"] = bg
        self.root.configure(bg=bg)
        self.outer.configure(bg=self._lighter(bg,35))
        self.inner.configure(bg=bg)
        self.text.configure(bg=bg)

    def _apply_font_color(self, fg):
        self.cfg["fg_color"] = fg
        self.text.configure(fg=fg)

    # ─── edge ───────────────────────────────────────────────────
    def _detect_edge(self, event):
        w,h = self.root.winfo_width(), self.root.winfo_height()
        x = event.x_root - self.root.winfo_rootx()
        y = event.y_root - self.root.winfo_rooty()
        n,s,we,e = y<=GRIP, y>=h-GRIP, x<=GRIP, x>=w-GRIP
        if n and we: return 'nw'
        if n and e:  return 'ne'
        if s and we: return 'sw'
        if s and e:  return 'se'
        if n: return 'n'
        if s: return 's'
        if we:return 'w'
        if e: return 'e'
        return None

    CURSOR_MAP = {
        'n':'size_ns','s':'size_ns',
        'e':'size_we','w':'size_we',
        'ne':'size_ne_sw','nw':'size_nw_se',
        'se':'size_nw_se','sw':'size_ne_sw',
    }

    def _on_motion(self, event):
        if self._resize_edge: return
        e = self._detect_edge(event)
        cur = self.CURSOR_MAP.get(e, "arrow")
        try:
            event.widget.config(cursor=cur)
        except Exception:
            self.root.config(cursor=cur)

    def _on_leave(self, event):
        if not self._resize_edge:
            self.root.config(cursor="arrow")

    def _on_left_down(self, event):
        e = self._detect_edge(event)
        if e:
            self._resize_edge = e
            self._resize_start = (
                event.x_root, event.y_root,
                self.root.winfo_x(), self.root.winfo_y(),
                self.root.winfo_width(), self.root.winfo_height(),
            )
        else:
            self._resize_edge = None
            self._dx = event.x_root - self.root.winfo_x()
            self._dy = event.y_root - self.root.winfo_y()

    def _on_left_drag(self, event):
        if self._resize_edge:
            self._do_resize(event)
        else:
            x = event.x_root - self._dx
            y = event.y_root - self._dy
            self.root.geometry(f"+{x}+{y}")

    def _do_resize(self, event):
        sx,sy,ox,oy,ow,oh = self._resize_start
        dx,dy = event.x_root-sx, event.y_root-sy
        e = self._resize_edge
        nx,ny,nw,nh = ox,oy,ow,oh
        if 'w' in e: nx=ox+dx; nw=ow-dx
        if 'e' in e: nw=ow+dx
        if 'n' in e: ny=oy+dy; nh=oh-dy
        if 's' in e: nh=oh+dy
        nw,nh = max(nw,MIN_W), max(nh,MIN_H)
        self.root.geometry(f"{nw}x{nh}+{nx}+{ny}")

    # ─── menu (Chinese) ────────────────────────────────────────
    def _build_menu(self):
        m = Menu(self.root, tearoff=0, font=('Microsoft YaHei', 10))
        m.add_command(label="字号 +   Ctrl+=", command=self.font_bigger)
        m.add_command(label="字号 -   Ctrl+-", command=self.font_smaller)
        m.add_separator()
        m.add_command(label="不透明度 +   Ctrl+→", command=self.opacity_up)
        m.add_command(label="不透明度 -   Ctrl+←", command=self.opacity_down)
        m.add_separator()
        cm = Menu(m, tearoff=0, font=('Microsoft YaHei', 10))
        for name, hexc in COLOR_PRESETS:
            cm.add_command(
                label=f"{name}  {hexc}",
                command=lambda c=hexc: self._apply_colors(c),
                background=hexc,
                foreground='#FFF' if self._is_dark(hexc) else '#000',
                activebackground=hexc,
            )
        m.add_cascade(label="底色", menu=cm)
        m.add_separator()
        fcm = Menu(m, tearoff=0, font=('Microsoft YaHei', 10))
        for fname, fhex in FONT_COLOR_PRESETS:
            fcm.add_command(
                label=f"{fname}  {fhex}",
                command=lambda c=fhex: self._apply_font_color(c),
                foreground=fhex,
                activeforeground=fhex,
            )
        m.add_cascade(label="字体颜色", menu=fcm)
        m.add_separator()
        self._top_var = tk.BooleanVar(value=self.cfg["always_on_top"])
        m.add_checkbutton(label="窗口置顶", variable=self._top_var,
                          command=self.toggle_always_on_top)
        m.add_separator()
        m.add_command(label="重置大小", command=self.reset_size)
        m.add_command(label="退出程序", command=self._on_close)
        self.ctx_menu = m

    def _show_menu(self, event):
        self.ctx_menu.tk_popup(event.x_root, event.y_root)

    # ─── UI actions ────────────────────────────────────────────
    def font_bigger(self):
        self.cfg["font_size"] = min(self.cfg["font_size"]+2, 72); self._apply_font()
    def font_smaller(self):
        self.cfg["font_size"] = max(self.cfg["font_size"]-2, 12); self._apply_font()
    def opacity_up(self):
        self.cfg["opacity"] = min(round(self.cfg["opacity"]+0.05,2), 1.0)
        self.root.attributes('-alpha', self.cfg["opacity"])
    def opacity_down(self):
        self.cfg["opacity"] = max(round(self.cfg["opacity"]-0.05,2), 0.25)
        self.root.attributes('-alpha', self.cfg["opacity"])
    def toggle_always_on_top(self):
        self.cfg["always_on_top"] = self._top_var.get()
        self.root.attributes('-topmost', self.cfg["always_on_top"])
    def reset_size(self):
        self.root.geometry("800x180+200+150")
    def _apply_font(self):
        self.text.configure(font=(self.cfg["font_family"], self.cfg["font_size"]))

    def _on_close(self):
        self.running = False
        self.cfg["geometry"] = self.root.geometry()
        save_config(self.cfg)
        self._kill_recognizer()
        self.root.destroy()

    # ─── recognizer subprocess ─────────────────────────────────
    def _start_recognizer(self):
        if not self._recognizer_cmd:
            return
        try:
            self._proc = subprocess.Popen(
                self._recognizer_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0,
            )
        except Exception:
            pass

    def _kill_recognizer(self):
        if self._proc and self._proc.poll() is None:
            try:
                self._proc.terminate()
                self._proc.wait(timeout=3)
            except Exception:
                try: self._proc.kill()
                except: pass

    # ─── text display ──────────────────────────────────────────
    def _redraw_if_needed(self):
        if self._last_content:
            self._render(self._last_content)

    def _render(self, content):
        try:
            self.text.configure(state=tk.NORMAL)
            current = self.text.get("1.0","end-1c")
            if content == current:
                self.text.configure(state=tk.DISABLED); return
            mn = min(len(current), len(content))
            split = 0
            for i in range(mn):
                if current[i] != content[i]:
                    split = i; break
            else:
                split = mn
            if split < len(current):
                self.text.delete(f"1.0 + {split} chars","end-1c")
            if split < len(content):
                self.text.insert(f"1.0 + {split} chars",content[split:])
            self.text.configure(state=tk.DISABLED)
            self.text.see("end-1c")
        except Exception:
            try:
                self.text.configure(state=tk.NORMAL)
                self.text.delete("1.0",tk.END)
                if content: self.text.insert(tk.END,content)
                self.text.configure(state=tk.DISABLED)
                self.text.see("end-1c")
            except: pass

    def set_text(self, content):
        content = content.replace('\n',' ').replace('\r',' ')
        while '  ' in content: content = content.replace('  ',' ')
        content = content.strip()
        if content == self._last_content: return
        self._last_content = content
        self._render(content)

    def _read_status(self):
        try:
            if os.path.exists(STATUS_FILE):
                with open(STATUS_FILE,'r',encoding='utf-8') as f:
                    return f.read().strip()
        except: pass
        return ""

    def poll_file(self):
        if not self.running: return
        self.set_text(self._read_status())
        self.root.after(60, self.poll_file)

    def run(self):
        self._start_recognizer()
        self.set_text("识别中...")
        self.poll_file()
        self.root.mainloop()


def main():
    # Parse: subtitle_window.py [-- recognizer args...]
    rec_cmd = None
    args = sys.argv[1:]
    try:
        sep = args.index('--')
        rec_cmd = args[sep+1:]
    except ValueError:
        rec_cmd = None

    SubtitleWindow(recognizer_cmd=rec_cmd).run()


if __name__ == "__main__":
    main()
