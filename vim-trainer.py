#!/usr/bin/env python3
"""
Vim Keystroke Trainer - Fixed addstr + Clean Persistent Version
No addwstr, proper cleanup after each exercise, rinse-and-repeat reliable.

Run: python3 vim_trainer_clean.py
"""

import curses
import time
from typing import List, Dict

# Special key names (ASCII control codes)
ESC     = 'ESC'
ENTER   = 'ENTER'
CTRL_V  = 'CTRL_V'  # \x16
CTRL_R  = 'CTRL_R'  # \x12

exercises: List[Dict[str, any]] = [
    # 1. Insert Modes
    {'desc': 'Insert mode (i)', 'sequence': ['i']},
    {'desc': 'Append mode (a)', 'sequence': ['a']},
    {'desc': 'Insert line start (I)', 'sequence': ['I']},
    {'desc': 'Append line end (A)', 'sequence': ['A']},
    {'desc': 'New line below (o)', 'sequence': ['o']},
    {'desc': 'New line above (O)', 'sequence': ['O']},
    
    # 2. Mode Exit + Commands
    {'desc': 'Normal mode (Esc)', 'sequence': [ESC]},
    {'desc': 'Save (:w)', 'sequence': [':', 'w', ENTER]},
    {'desc': 'Quit force (:q!)', 'sequence': [':', 'q', '!', ENTER]},
    {'desc': 'spf13 save (,w)', 'sequence': [',', 'w']},
    
    # 3. Movement (hjkl + words)
    {'desc': 'Left (h)', 'sequence': ['h']},
    {'desc': 'Down (j)', 'sequence': ['j']},
    {'desc': 'Up (k)', 'sequence': ['k']},
    {'desc': 'Right (l)', 'sequence': ['l']},
    {'desc': 'Next word (w)', 'sequence': ['w']},
    {'desc': 'Prev word (b)', 'sequence': ['b']},
    {'desc': 'Word end (e)', 'sequence': ['e']},
    {'desc': '3 words fwd (3w)', 'sequence': ['3', 'w']},
    {'desc': 'Line start (0)', 'sequence': ['0']},
    {'desc': 'First non-blank (^)', 'sequence': ['^']},
    {'desc': 'Line end ($)', 'sequence': ['$']},
    {'desc': 'File top (gg)', 'sequence': ['g', 'g']},
    {'desc': 'File bottom (G)', 'sequence': ['G']},
    
    # 4. Editing (d/c/y)
    {'desc': 'Delete word (dw)', 'sequence': ['d', 'w']},
    {'desc': 'Delete inner word (diw)', 'sequence': ['d', 'i', 'w']},
    {'desc': 'Delete to EOL (D)', 'sequence': ['D']},
    {'desc': 'Delete line (dd)', 'sequence': ['d', 'd']},
    {'desc': 'Change word (cw)', 'sequence': ['c', 'w']},
    {'desc': 'Change quotes (ci")', 'sequence': ['c', 'i', '"']},
    {'desc': 'Change Sq.  (ci[)', 'sequence': ['c', 'i', '[']},
    {'desc': 'Yank line (yy)', 'sequence': ['y', 'y']},
    {'desc': 'Paste after (p)', 'sequence': ['p']},
    {'desc': 'Undo (u)', 'sequence': ['u']},
    {'desc': 'Redo (Ctrl+r)', 'sequence': [CTRL_R]},
    {'desc': 'Repeat (.)', 'sequence': ['.']},
    
    # 5. Visual + spf13
    {'desc': 'Visual char (v)', 'sequence': ['v']},
    {'desc': 'Visual line (V)', 'sequence': ['V']},
    {'desc': 'Visual block (Ctrl+v)', 'sequence': [CTRL_V]},
    {'desc': 'spf13 quit (,q)', 'sequence': [',', 'q']},
    {'desc': 'spf13 NERDTree (,n)', 'sequence': [',', 'n']},
    {'desc': 'spf13 comment (,/)', 'sequence': [',', '/']},
]

def get_key_name(key: str) -> str:
    """Map curses key to internal name - ONLY addstr-safe chars"""
    if key == '\x1b':      return ESC
    if key == '\n':        return ENTER
    if key == '\x16':      return CTRL_V   # Ctrl+V
    if key == '\x12':      return CTRL_R   # Ctrl+R
    if len(key) == 1 and (32 <= ord(key) <= 126):  # Printable ASCII only
        return key
    return '?'  # Unknown -> safe fallback

def display_sequence(seq: List[str]) -> str:
    """Safe display string (no unicode issues)"""
    parts = []
    for s in seq:
        if s == ESC:     parts.append('<Esc>')
        elif s == ENTER: parts.append('<Ent>')
        elif s == CTRL_V: parts.append('<C-v>')
        elif s == CTRL_R: parts.append('<C-r>')
        else:            parts.append(s)
    return ''.join(parts)

def cleanup_line(stdscr, row: int, col: int = 0):
    """Clear line from position onward - safe"""
    stdscr.move(row, col)
    stdscr.clrtoeol()
    stdscr.refresh()

def main(stdscr):
    # Setup
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # ✓ Correct
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # ✗ Wrong  
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Header
    
    max_y, max_x = stdscr.getmaxyx()
    current_line = 0
    
    def safe_print(text: str, row: int, col: int = 0, color: int = 0, truncate: bool = True):
        nonlocal current_line
        if truncate and len(text) > max_x - col - 1:
            text = text[:max_x - col - 5] + "..."
        if row >= max_y - 3:  # Prevent overflow
            stdscr.clear()
            row = 0
            nonlocal current_line
            current_line = 0
            safe_print("=== NEW PAGE, KEEP GOING! ===", row, 0, 3)
            row += 1
        
        try:
            stdscr.move(row, col)
            if color:
                stdscr.attron(curses.color_pair(color))
            stdscr.addstr(row, col, text)
            if color:
                stdscr.attroff(curses.color_pair(color))
            stdscr.refresh()
        except curses.error:
            pass  # Silent fail on edge cases
    
    # Header (stays at top)
    safe_print("=== VIM KEYSTROKE TRAINER (spf13-vim) ===", 0, 0, 3)
    safe_print("Press exact sequence. Wrong key = skip. All history preserved.", 1, 0, 3)
    safe_print("", 2, 0)
    current_line = 3

    # Stats
    total = len(exercises)
    correct = 0
    total_time = 0.0
    errors = 0

    for i, ex in enumerate(exercises, 1):
        # Exercise header
        safe_print(f"[{i:2d}/{total}] {ex['desc']:<35}", current_line, 0)
        safe_print(f"    Expect: {display_sequence(ex['sequence'])}", current_line + 1, 0)
        input_row = current_line + 2
        result_row = current_line + 3
        current_line = result_row + 1
        
        # Input tracking
        seq = ex['sequence']
        typed = []
        start_time = time.time()
        pos = 0
        success = True
        
        # Typing loop
        while pos < len(seq):
            try:
                key = stdscr.getkey()
            except curses.error:
                continue
                
            mapped = get_key_name(key)
            
            # Clean input line
            cleanup_line(stdscr, input_row)
            
            # Show typed + current
            typed_disp = ''.join([t if len(t)==1 else f'<{t}>' for t in typed])
            curr_disp = mapped if len(mapped)==1 else f'<{mapped}>'
            full_disp = typed_disp + curr_disp
            
            safe_print(f"    Typed:  {full_disp}", input_row, 0)
            
            col_offset = 13 + len(typed_disp)  # "    Typed:  " = 12 chars
            if mapped == seq[pos]:
                # GREEN correct key
                stdscr.move(input_row, col_offset)
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(input_row, col_offset, curr_disp)
                stdscr.attroff(curses.color_pair(1))
                typed.append(mapped)
                pos += 1
            else:
                # RED wrong key
                stdscr.move(input_row, col_offset)
                stdscr.attron(curses.color_pair(2))
                stdscr.addstr(input_row, col_offset, curr_disp)
                stdscr.attroff(curses.color_pair(2))
                success = False
                safe_print("    ✗ WRONG - Press any key to skip...", result_row, 0, 2)
                stdscr.refresh()
                stdscr.getch()  # Wait
                break
                
            stdscr.refresh()
        
        # Result
        elapsed = time.time() - start_time
        cleanup_line(stdscr, result_row)
        
        if success:
            correct += 1
            total_time += elapsed
            safe_print(f"    ✓ CORRECT!  {elapsed:5.2f}s", result_row, 0, 1)
        else:
            errors += 1
            safe_print(f"    ✗ FAILED                    ", result_row, 0, 2)
        
        safe_print("", current_line, 0)  # Spacer
        current_line += 1
        stdscr.refresh()

    # Final grade - always at bottom
    final_row = max(10, current_line)
    safe_print("═" * 60, final_row, 0, 3)
    safe_print("           TRAINING COMPLETE! FINAL GRADE", final_row + 1, 0, 3)
    safe_print("═" * 60, final_row + 2, 0, 3)
    
    accuracy = (correct / total * 100) if total else 0
    avg_time = total_time / correct if correct else 0
    
    safe_print(f"Accuracy:  {accuracy:6.1f}%  ({correct}/{total})", final_row + 3, 0, 3)
    safe_print(f"Avg time:  {avg_time:7.2f}s per correct exercise", final_row + 4, 0, 3)
    safe_print(f"Errors:    {errors:3d}", final_row + 5, 0, 3)
    
    # Progress tips
    if accuracy > 90:
        safe_print("🎉 EXPERT LEVEL! You're Vim-ready!", final_row + 7, 0, 1)
    elif accuracy > 70:
        safe_print("👍 GOOD! Practice daily for mastery.", final_row + 7, 0, 1)
    else:
        safe_print("📚 Keep practicing! Focus on errors above.", final_row + 7, 0, 3)
    
    safe_print("Press any key to exit...", final_row + 9, 0, 3)
    stdscr.refresh()
    stdscr.getch()

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("\nSession cancelled.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()