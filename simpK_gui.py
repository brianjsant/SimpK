"""
SimpK IDE — A complete graphical environment for the SimpK language.
Run with:  python simpk_gui.py
"""
 
import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
 
# Add src to path so we can import SimpK modules
SRC_DIR = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, SRC_DIR)
 
from lexer import Lexer, LexerError
from parser import Parser, ParseError
from ast_nodes import format_ast
from evaluator import Evaluator, SimpKError
 
# ── Color palette ──────────────────────────────────────────────────────────────
BG        = '#1a1b26'   # deep navy background
BG2       = '#16161e'   # darker sidebar / panel
BG3       = '#24253a'   # slightly lighter panel
ACCENT    = '#7aa2f7'   # blue accent (like Tokyo Night)
ACCENT2   = '#bb9af7'   # purple accent
GREEN     = '#9ece6a'
RED       = '#f7768e'
YELLOW    = '#e0af68'
CYAN      = '#7dcfff'
FG        = '#c0caf5'
FG_DIM    = '#565f89'
SELECTION = '#283457'
 
# ── Syntax highlighting token colors ──────────────────────────────────────────
SYNTAX = {
    'keyword':  ACCENT2,
    'number':   YELLOW,
    'operator': CYAN,
    'comment':  FG_DIM,
    'function': GREEN,
    'paren':    FG,
    'bracket':  YELLOW,
}
 
KEYWORDS = {'func', 'return', 'if', 'then', 'else', 'print', 'input'}
 
 
# ═══════════════════════════════════════════════════════════════════════════════
# Syntax Highlighter
# ═══════════════════════════════════════════════════════════════════════════════
 
def highlight(text_widget):
    """Apply syntax highlighting to the entire editor content."""
    content = text_widget.get('1.0', 'end-1c')
 
    # Remove all existing tags
    for tag in ('keyword', 'number', 'operator', 'comment', 'function',
                'paren', 'bracket', 'string'):
        text_widget.tag_remove(tag, '1.0', 'end')
 
    import re
 
    patterns = [
        ('comment',  r'#[^\n]*'),
        ('number',   r'\b\d+\.?\d*\b'),
        ('keyword',  r'\b(?:func|return|if|then|else|print|input)\b'),
        ('function', r'\b[a-zA-Z_]\w*(?=\s*\()'),
        ('operator', r'[+\-*/=<>!]+'),
        ('paren',    r'[()]'),
        ('bracket',  r'[\[\]]'),
    ]
 
    for tag, pattern in patterns:
        for m in re.finditer(pattern, content):
            start_idx = f'1.0+{m.start()}c'
            end_idx   = f'1.0+{m.end()}c'
            text_widget.tag_add(tag, start_idx, end_idx)
 
 
# ═══════════════════════════════════════════════════════════════════════════════
# Main Application
# ═══════════════════════════════════════════════════════════════════════════════
 
class SimpKIDE:
    def __init__(self, root):
        self.root = root
        self.root.title('SimpK IDE')
        self.root.geometry('1100x720')
        self.root.configure(bg=BG)
        self.root.minsize(800, 560)
 
        self._current_file = None
        self._input_var = tk.StringVar()
        self._input_event = threading.Event()
        self._waiting_for_input = False
 
        self._build_ui()
        self._load_example()
 
    # ── UI Construction ────────────────────────────────────────────────────────
 
    def _build_ui(self):
        # Top toolbar
        self._build_toolbar()
 
        # Main area: editor + right panel
        main = tk.Frame(self.root, bg=BG)
        main.pack(fill='both', expand=True, padx=0, pady=0)
 
        # Left: line numbers + editor
        editor_frame = tk.Frame(main, bg=BG2)
        editor_frame.pack(side='left', fill='both', expand=True)
 
        self._build_editor(editor_frame)
 
        # Right: output + AST tabs
        right = tk.Frame(main, bg=BG2, width=380)
        right.pack(side='right', fill='both')
        right.pack_propagate(False)
 
        self._build_right_panel(right)
 
        # Bottom status bar
        self._build_statusbar()
 
    def _build_toolbar(self):
        tb = tk.Frame(self.root, bg=BG3, height=46)
        tb.pack(fill='x', side='top')
        tb.pack_propagate(False)
 
        # Logo
        tk.Label(
            tb, text='  SimpK', bg=BG3, fg=ACCENT,
            font=('Courier', 15, 'bold')
        ).pack(side='left', padx=(8, 0))
 
        tk.Label(
            tb, text='IDE', bg=BG3, fg=ACCENT2,
            font=('Courier', 15, 'bold')
        ).pack(side='left')
 
        tk.Frame(tb, bg=FG_DIM, width=1).pack(side='left', fill='y', padx=12, pady=8)
 
        btn_cfg = dict(bg=BG3, fg=FG, relief='flat', font=('Courier', 11),
                       padx=10, pady=4, cursor='hand2', activebackground=SELECTION,
                       activeforeground=FG)
 
        buttons = [
            ('▶  Run',     self._run_program,   GREEN),
            ('⟳  Lex',    self._show_tokens,   ACCENT),
            ('⌥  Parse',  self._show_ast,       ACCENT2),
            ('◼  Clear',  self._clear_output,   YELLOW),
            ('⊕  Open',   self._open_file,      FG),
            ('⊘  Save',   self._save_file,      FG),
        ]
 
        for label, cmd, fg_col in buttons:
            b = tk.Button(tb, text=label, command=cmd, **btn_cfg)
            b.configure(fg=fg_col)
            b.pack(side='left', padx=2, pady=6)
            b.bind('<Enter>', lambda e, w=b: w.config(bg=SELECTION))
            b.bind('<Leave>', lambda e, w=b, orig=BG3: w.config(bg=orig))
 
        # Help button right side
        tk.Button(
            tb, text='?  Examples', command=self._show_examples,
            bg=BG3, fg=FG_DIM, relief='flat', font=('Courier', 10),
            padx=8, pady=4, cursor='hand2'
        ).pack(side='right', padx=8)
 
    def _build_editor(self, parent):
        header = tk.Frame(parent, bg=BG3, height=28)
        header.pack(fill='x')
        header.pack_propagate(False)
 
        self._file_label = tk.Label(
            header, text='  untitled.simpk',
            bg=BG3, fg=FG_DIM, font=('Courier', 10)
        )
        self._file_label.pack(side='left', padx=4)
 
        # Editor + scrollbar + line numbers
        editor_area = tk.Frame(parent, bg=BG)
        editor_area.pack(fill='both', expand=True)
 
        # Line numbers
        self._line_nums = tk.Text(
            editor_area, width=4, bg=BG2, fg=FG_DIM,
            font=('Courier', 13), relief='flat',
            state='disabled', cursor='arrow', selectbackground=BG2,
            padx=4, pady=8
        )
        self._line_nums.pack(side='left', fill='y')
 
        scrollbar = ttk.Scrollbar(editor_area)
        scrollbar.pack(side='right', fill='y')
 
        self._editor = tk.Text(
            editor_area, bg=BG, fg=FG,
            font=('Courier', 13), relief='flat',
            insertbackground=ACCENT, selectbackground=SELECTION,
            undo=True, wrap='none',
            pady=8, padx=8,
            yscrollcommand=self._sync_scroll
        )
        self._editor.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self._editor.yview)
 
        # Configure syntax tags
        for tag, color in SYNTAX.items():
            self._editor.tag_configure(tag, foreground=color)
 
        # Bindings
        self._editor.bind('<KeyRelease>', self._on_edit)
        self._editor.bind('<Control-Return>', lambda e: self._run_program())
        self._editor.bind('<Control-s>', lambda e: self._save_file())
        self._editor.bind('<Tab>', self._insert_tab)
 
    def _sync_scroll(self, *args):
        # Keep line numbers in sync
        self._line_nums.yview_moveto(args[0])
        self._update_line_numbers()
        # Also pass to built-in scroll
        pass
 
    def _update_line_numbers(self):
        content = self._editor.get('1.0', 'end-1c')
        lines = content.count('\n') + 1
        nums = '\n'.join(str(i) for i in range(1, lines + 1))
        self._line_nums.config(state='normal')
        self._line_nums.delete('1.0', 'end')
        self._line_nums.insert('1.0', nums)
        self._line_nums.config(state='disabled')
 
    def _build_right_panel(self, parent):
        header = tk.Frame(parent, bg=BG3, height=28)
        header.pack(fill='x')
        header.pack_propagate(False)
 
        tk.Label(
            header, text='  Output', bg=BG3, fg=ACCENT,
            font=('Courier', 10, 'bold')
        ).pack(side='left', padx=4, pady=4)
 
        # Notebook for Output / AST / Tokens
        style = ttk.Style()
        style.theme_use('default')
        style.configure('SimpK.TNotebook', background=BG2, borderwidth=0)
        style.configure('SimpK.TNotebook.Tab',
                        background=BG3, foreground=FG_DIM,
                        padding=[10, 4], font=('Courier', 10))
        style.map('SimpK.TNotebook.Tab',
                  background=[('selected', BG)],
                  foreground=[('selected', ACCENT)])
 
        nb = ttk.Notebook(parent, style='SimpK.TNotebook')
        nb.pack(fill='both', expand=True)
 
        # Output tab
        out_frame = tk.Frame(nb, bg=BG)
        nb.add(out_frame, text='Output')
        self._output = tk.Text(
            out_frame, bg=BG, fg=GREEN,
            font=('Courier', 12), relief='flat',
            state='disabled', wrap='word',
            padx=10, pady=8, insertbackground=GREEN
        )
        self._output.pack(fill='both', expand=True)
        self._output.tag_configure('error',  foreground=RED)
        self._output.tag_configure('info',   foreground=ACCENT)
        self._output.tag_configure('input',  foreground=YELLOW)
        self._output.tag_configure('result', foreground=GREEN)
 
        # Input row (shown when program calls input())
        self._input_frame = tk.Frame(out_frame, bg=BG3)
        self._input_entry = tk.Entry(
            self._input_frame, textvariable=self._input_var,
            bg=BG, fg=YELLOW, insertbackground=YELLOW,
            font=('Courier', 12), relief='flat', bd=4
        )
        self._input_entry.pack(side='left', fill='x', expand=True, padx=4, pady=4)
        tk.Button(
            self._input_frame, text='↵ Enter',
            command=self._submit_input,
            bg=ACCENT, fg=BG, font=('Courier', 10, 'bold'),
            relief='flat', padx=8, cursor='hand2'
        ).pack(side='right', padx=4, pady=4)
        self._input_entry.bind('<Return>', lambda e: self._submit_input())
 
        # AST tab
        ast_frame = tk.Frame(nb, bg=BG)
        nb.add(ast_frame, text='AST')
        self._ast_out = tk.Text(
            ast_frame, bg=BG, fg=ACCENT2,
            font=('Courier', 11), relief='flat',
            state='disabled', wrap='none',
            padx=10, pady=8
        )
        self._ast_out.pack(fill='both', expand=True)
 
        # Tokens tab
        tok_frame = tk.Frame(nb, bg=BG)
        nb.add(tok_frame, text='Tokens')
        self._tok_out = tk.Text(
            tok_frame, bg=BG, fg=CYAN,
            font=('Courier', 11), relief='flat',
            state='disabled', wrap='none',
            padx=10, pady=8
        )
        self._tok_out.pack(fill='both', expand=True)
 
    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg=ACCENT, height=22)
        bar.pack(fill='x', side='bottom')
        bar.pack_propagate(False)
        self._status = tk.Label(
            bar, text='  Ready — Ctrl+Enter to run',
            bg=ACCENT, fg=BG, font=('Courier', 9, 'bold'), anchor='w'
        )
        self._status.pack(side='left', fill='both')
 
        self._cursor_pos = tk.Label(
            bar, text='Ln 1, Col 1',
            bg=ACCENT, fg=BG, font=('Courier', 9, 'bold')
        )
        self._cursor_pos.pack(side='right', padx=8)
 
    # ── Editor helpers ─────────────────────────────────────────────────────────
 
    def _insert_tab(self, event):
        self._editor.insert('insert', '    ')
        return 'break'
 
    def _on_edit(self, event=None):
        self._update_line_numbers()
        highlight(self._editor)
        # Update cursor position
        pos = self._editor.index('insert')
        line, col = pos.split('.')
        self._cursor_pos.config(text=f'Ln {line}, Col {int(col)+1}')
 
    def _get_source(self):
        return self._editor.get('1.0', 'end-1c')
 
    # ── Output helpers ─────────────────────────────────────────────────────────
 
    def _write(self, text, tag='result'):
        self._output.config(state='normal')
        self._output.insert('end', text + '\n', tag)
        self._output.see('end')
        self._output.config(state='disabled')
 
    def _clear_output(self):
        self._output.config(state='normal')
        self._output.delete('1.0', 'end')
        self._output.config(state='disabled')
 
    def _set_text(self, widget, text):
        widget.config(state='normal')
        widget.delete('1.0', 'end')
        widget.insert('1.0', text)
        widget.config(state='disabled')
 
    # ── Input handling ─────────────────────────────────────────────────────────
 
    def _show_input_bar(self):
        self._waiting_for_input = True
        self._input_var.set('')
        self._input_frame.pack(fill='x', side='bottom')
        self._input_entry.focus_set()
        self._write('▶ Waiting for input...', 'input')
 
    def _hide_input_bar(self):
        self._waiting_for_input = False
        self._input_frame.pack_forget()
 
    def _submit_input(self):
        if not self._waiting_for_input:
            return
        val = self._input_var.get()
        self._write(f'  ← {val}', 'input')
        self._hide_input_bar()
        self._input_event.set()
 
    def _gui_input_callback(self):
        """Called by the evaluator thread; blocks until user submits input."""
        self._input_event.clear()
        self.root.after(0, self._show_input_bar)
        self._input_event.wait()   # block evaluator thread
        return self._input_var.get()
 
    # ── Run ────────────────────────────────────────────────────────────────────
 
    def _run_program(self):
        self._clear_output()
        source = self._get_source()
        if not source.strip():
            self._write('(empty program)', 'info')
            return
 
        self._status.config(text='  Running...')
        self._write('── Running SimpK ──', 'info')
 
        def run():
            try:
                lexer  = Lexer(source)
                tokens = lexer.tokenize()
                parser = Parser(tokens)
                ast    = parser.parse_program()
 
                def output_cb(s):
                    self.root.after(0, lambda: self._write(s, 'result'))
 
                ev = Evaluator(
                    output_callback=output_cb,
                    input_callback=self._gui_input_callback
                )
                ev.eval(ast)
                self.root.after(0, lambda: self._status.config(text='  Done ✓'))
                self.root.after(0, lambda: self._write('── Done ──', 'info'))
 
            except (LexerError, ParseError) as e:
                msg = f'Parse Error: {e}'
                self.root.after(0, lambda m=msg: self._write(m, 'error'))
                self.root.after(0, lambda: self._status.config(text='  Parse error'))
 
            except SimpKError as e:
                msg = f'Runtime Error: {e}'
                self.root.after(0, lambda m=msg: self._write(m, 'error'))
                self.root.after(0, lambda: self._status.config(text='  Runtime error'))
 
            except Exception as e:
                msg = f'Internal Error: {e}'
                self.root.after(0, lambda m=msg: self._write(m, 'error'))
                self.root.after(0, lambda: self._status.config(text='  Error'))
 
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
 
    # ── Lex ────────────────────────────────────────────────────────────────────
 
    def _show_tokens(self):
        source = self._get_source()
        try:
            tokens = Lexer(source).tokenize()
            lines = [str(t) for t in tokens]
            self._set_text(self._tok_out, '\n'.join(lines))
            self._status.config(text=f'  Lexed — {len(tokens)} tokens')
        except LexerError as e:
            self._set_text(self._tok_out, f'Lex Error: {e}')
            self._status.config(text='  Lex error')
 
    # ── Parse / AST ───────────────────────────────────────────────────────────
 
    def _show_ast(self):
        source = self._get_source()
        try:
            tokens = Lexer(source).tokenize()
            ast    = Parser(tokens).parse_program()
            self._set_text(self._ast_out, format_ast(ast))
            self._status.config(text='  Parsed — AST ready')
        except (LexerError, ParseError) as e:
            self._set_text(self._ast_out, f'Error: {e}')
            self._status.config(text='  Parse error')
 
    # ── File I/O ───────────────────────────────────────────────────────────────
 
    def _open_file(self):
        path = filedialog.askopenfilename(
            filetypes=[('SimpK files', '*.simpk'), ('All files', '*.*')]
        )
        if path:
            with open(path, 'r', encoding='utf-8') as f:
                source = f.read()
            self._editor.delete('1.0', 'end')
            self._editor.insert('1.0', source)
            self._current_file = path
            self._file_label.config(text=f'  {os.path.basename(path)}')
            self._on_edit()
 
    def _save_file(self):
        if self._current_file:
            path = self._current_file
        else:
            path = filedialog.asksaveasfilename(
                defaultextension='.simpk',
                filetypes=[('SimpK files', '*.simpk'), ('All files', '*.*')]
            )
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self._get_source())
            self._current_file = path
            self._file_label.config(text=f'  {os.path.basename(path)}')
            self._status.config(text=f'  Saved — {os.path.basename(path)}')
 
    # ── Examples ──────────────────────────────────────────────────────────────
 
    def _show_examples(self):
        win = tk.Toplevel(self.root)
        win.title('SimpK Examples')
        win.configure(bg=BG)
        win.geometry('560x500')
 
        tk.Label(
            win, text='SimpK Example Programs',
            bg=BG, fg=ACCENT, font=('Courier', 14, 'bold')
        ).pack(pady=(16, 4))
 
        tk.Label(
            win, text='Click an example to load it into the editor',
            bg=BG, fg=FG_DIM, font=('Courier', 10)
        ).pack(pady=(0, 12))
 
        examples = [
            ('Basic arithmetic', """\
x = 5
y = 10
print(x + y)
"""),
            ('Conditional (if/then/else)', """\
x = 4
result = if x > 3 then 1 else 0
print(result)
"""),
            ('Function: square', """\
func square(x) {
    return x * x
}
print(square(7))
"""),
            ('Function: max of two', """\
func mymax(a, b) {
    return if a > b then a else b
}
print(mymax(10, 25))
"""),
            ('Recursive factorial', """\
func fact(n) {
    return if n < 2 then 1 else n * fact(n - 1)
}
print(fact(6))
"""),
            ('List element-wise ops', """\
nums = [1, 2, 3, 4, 5]
doubled = nums * 2
print(doubled)
print(nums + 10)
"""),
            ('List indexing & update', """\
nums = [10, 20, 30]
print(nums[1])
nums[2] = 99
print(nums)
"""),
            ('Built-in functions', """\
data = [3, 1, 4, 1, 5, 9, 2, 6]
print(len(data))
print(sum(data))
print(max(data))
print(min(data))
"""),
            ('Floats & division', """\
x = 7
y = 2
print(x / y)
pi = 3.14
r = 5
area = pi * r * r
print(area)
"""),
            ('List equality check', """\
a = [1, 2, 3]
b = [1, 2, 3]
print(a == b)
"""),
        ]
 
        frame = tk.Frame(win, bg=BG)
        frame.pack(fill='both', expand=True, padx=16, pady=8)
 
        for name, code in examples:
            row = tk.Frame(frame, bg=BG3, pady=2)
            row.pack(fill='x', pady=3)
 
            tk.Label(
                row, text=name, bg=BG3, fg=FG,
                font=('Courier', 11), width=28, anchor='w'
            ).pack(side='left', padx=10, pady=6)
 
            def load(c=code, w=win):
                self._editor.delete('1.0', 'end')
                self._editor.insert('1.0', c.strip())
                self._on_edit()
                w.destroy()
 
            tk.Button(
                row, text='Load →', command=load,
                bg=ACCENT, fg=BG, font=('Courier', 10, 'bold'),
                relief='flat', padx=10, cursor='hand2'
            ).pack(side='right', padx=10, pady=4)
 
    # ── Default example ───────────────────────────────────────────────────────
 
    def _load_example(self):
        default = """\
# Welcome to SimpK!
# Press Ctrl+Enter or click ▶ Run to execute.
 
func square(x) {
    return x * x
}
 
nums = [1, 2, 3, 4, 5]
print(nums * 2)
 
result = square(9)
print(result)
 
answer = if result > 50 then 1 else 0
print(answer)
"""
        self._editor.insert('1.0', default.strip())
        self._on_edit()
 
 
# ═══════════════════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════════════════
 
if __name__ == '__main__':
    root = tk.Tk()
    app = SimpKIDE(root)
    root.mainloop()
