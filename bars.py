#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
# Copyright (c) 2016, Nicolas P. Rougier
# Distributed under the (new) BSD License.
# -----------------------------------------------------------------------------
import sys, math, time
import curses

ROWS, COLS = 32, 100


def make_progress_str(value, length=40, title=" ", vmin=0.0, vmax=1.0):
    """
    Text progress bar

    Parameters
    ----------
    value : float
        Current value to be displayed as progress

    vmin : float
        Minimum value

    vmax : float
        Maximum value

    length: int
        Bar length (in character)

    title: string
        Text to be prepend to the bar
    """
    # Block progression is 1/8
    blocks = ["", "▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"]
    vmin = vmin or 0.0
    vmax = vmax or 1.0
    lsep, rsep = "▏", "▕"

    # Normalize value
    value = min(max(value, vmin), vmax)
    value = (value - vmin) / float(vmax - vmin)

    v = value * length
    x = math.floor(v)  # integer part
    y = v - x  # fractional part
    base = 0.125  # 0.125 = 1/8
    prec = 3
    i = int(round(base * math.floor(float(y) / base), prec) / base)
    bar = "█" * x + blocks[i]
    n = length - len(bar)
    bar = lsep + bar + " " * n + rsep

    return title + bar + " %.1f%%" % (value * 100)


def main():
    global screen

    stdscr = curses.initscr()
    screen = stdscr.subwin(ROWS, COLS, 0, 0)  # Frame the interface area at fixed VT100 size
    # screen = stdscr.subwin(25, 79, 0, 0)  #

    screen.box()
    screen.hline(2, 1, curses.ACS_HLINE, COLS-2)
    N = 1000
    for i in range(N):
        screen.addstr(4, 2, make_progress_str(i, vmin=0, vmax=N-1))
        screen.addstr(5, 2, make_progress_str(N-i, vmin=0, vmax=N-1))
        screen.addstr(6, 2, make_progress_str(i, vmin=0, vmax=N-1))
        screen.addstr(7, 2, make_progress_str(N-i, vmin=0, vmax=N-1))


        screen.refresh()
        time.sleep(0.0025)
    screen.refresh()

def resize_terminal(rows=23, cols=79):
    sys.stdout.write("\x1b[8;{rows};{cols}t".format(rows=ROWS, cols=COLS))
    sys.stdout.flush()
    time.sleep(0.001) # delay keeps curses from breaking on wrong terminal window size



# -----------------------------------------------------------------------------
if __name__ == '__main__':
    try:
        resize_terminal(ROWS, COLS)
    except Exception as exc:
        print("Fatal: Unable to resize window, terminating")
        raise exc

    try:
        main()
    except KeyboardInterrupt:
        print("~terminated~")
    finally:
        curses.endwin()
