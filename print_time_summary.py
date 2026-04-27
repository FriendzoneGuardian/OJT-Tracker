"""
OJT Time Summary — Thermal Printer (Epson TM-82X)
Uses Win32Raw via python-escpos for the "Generic / Text Only" driver.
Designed to be ECONOMICAL: compact layout, minimal whitespace, short paper.
"""

import os
import sqlite3
from datetime import datetime
from escpos.printer import Win32Raw

# ─── CONFIG ────────────────────────────────────────
PRINTER_NAME = "Generic / Text Only"
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "ojt_tracker.db")
TARGET_HOURS = 486.0  # Default; overridden by DB settings if available
VERSION = "1.7.3"
LINE = "-" * 42


def format_hm(decimal_hrs):
    """Convert decimal hours (8.5) to H:MM (8:30)."""
    h = int(decimal_hrs)
    m = int(round((decimal_hrs - h) * 60))
    if m == 60:
        h += 1
        m = 0
    return f"{h}:{m:02d}"


def connect_db():
    if not os.path.exists(DB_PATH):
        print(f"[ERR] DB not found: {DB_PATH}")
        return None
    return sqlite3.connect(DB_PATH)


def fetch_summary():
    """Pull all stats needed for the receipt from the SQLite DB."""
    conn = connect_db()
    if not conn:
        return None

    cur = conn.cursor()

    # ── Settings ──
    cur.execute("SELECT target_hours, user_name FROM settings LIMIT 1")
    row = cur.fetchone()
    target = row[0] if row else TARGET_HOURS
    user_name = (row[1] or "").strip() if row else ""

    # ── Totals ──
    cur.execute("SELECT COALESCE(SUM(total_hours),0), COUNT(*) FROM ojt_entry")
    total_hrs, total_days = cur.fetchone()

    # ── Current month hours ──
    first_of_month = datetime.now().strftime("%Y-%m-01")
    cur.execute(
        "SELECT COALESCE(SUM(total_hours),0), COUNT(*) FROM ojt_entry WHERE date >= ?",
        (first_of_month,),
    )
    month_hrs, month_days = cur.fetchone()

    # ── All entries (Proof of OJT) ──
    cur.execute(
        "SELECT date, morn_in, morn_out, aftie_in, aftie_out, total_hours "
        "FROM ojt_entry ORDER BY date ASC"
    )
    recent = cur.fetchall()

    # ── Average pace (last 14 working entries) ──
    cur.execute(
        "SELECT COALESCE(AVG(total_hours),0) FROM "
        "(SELECT total_hours FROM ojt_entry ORDER BY date DESC LIMIT 14)"
    )
    avg_pace = cur.fetchone()[0]

    conn.close()

    remaining = max(0, target - total_hrs)
    days_left = int(remaining / avg_pace) if avg_pace > 0 else 0
    pct = (total_hrs / target * 100) if target > 0 else 0

    return {
        "target": target,
        "total_hrs": total_hrs,
        "total_days": total_days,
        "remaining": remaining,
        "month_hrs": month_hrs,
        "month_days": month_days,
        "avg_pace": avg_pace,
        "days_left": days_left,
        "pct": pct,
        "recent": recent,
        "user_name": user_name,
    }


def progress_bar(pct, width=20):
    """Tiny ASCII progress bar that fits 32-col thermal paper."""
    filled = int(width * min(pct, 100) / 100)
    return "[" + "#" * filled + "." * (width - filled) + "]"


def print_summary():
    data = fetch_summary()
    if not data:
        print("[ERR] Could not fetch summary.")
        return

    try:
        p = Win32Raw(PRINTER_NAME)
    except Exception as e:
        print(f"[ERR] Printer: {e}")
        return

    now = datetime.now()

    # ─── HEADER (compact) ─────────────────────────
    p.set(align="center", bold=True, width=2, height=1)
    p.text(f"OJT TRACKER - {VERSION}\n")
    p.set(align="center", bold=False, width=1, height=1)
    p.text("Time Summary\n")
    if data["user_name"]:
        p.set(bold=True)
        p.text(data["user_name"] + "\n")
        p.set(bold=False)
    p.text(now.strftime("%b %d, %Y  %I:%M %p") + "\n")
    p.text(LINE + "\n")

    # ─── STATS BLOCK ──────────────────────────────
    p.set(align="left", bold=False)
    p.text(f"Target     : {data['target']:.0f} hrs\n")
    p.text(f"Rendered   : {data['total_hrs']:.1f} hrs ({data['total_days']}d)\n")
    p.text(f"Remaining  : {data['remaining']:.1f} hrs ({data['days_left']}d left)\n")
    p.text("\n")  # Whitespace as requested
    p.text(f"Avg/Day    : {data['avg_pace']:.1f} hrs ({format_hm(data['avg_pace'])})\n")

    # ─── PROGRESS BAR ─────────────────────────────
    p.set(align="center")
    p.text(f"{progress_bar(data['pct'])} {data['pct']:.1f}%\n")
    p.text(LINE + "\n")

    # ─── FULL HISTORY (Proof Table) ───────────────
    if data["recent"]:
        # Pre-calculate monthly stats for breakers
        monthly_stats = {}
        for row in data["recent"]:
            m_key = datetime.strptime(row[0], "%Y-%m-%d").strftime("%Y-%m")
            if m_key not in monthly_stats:
                monthly_stats[m_key] = {"hrs": 0, "days": 0}
            monthly_stats[m_key]["hrs"] += row[5]
            monthly_stats[m_key]["days"] += 1

        p.set(align="center", bold=True)
        p.text("OFFICIAL OJT LOG\n")
        p.set(align="left", bold=True)
        # Header expanded for 42 cols
        p.text("DATE           IN       OUT      H:MM\n")
        p.set(bold=False)
        
        current_month = None
        for row in data["recent"]:
            date_raw = row[0]  # YYYY-MM-DD
            dt_obj = datetime.strptime(date_raw, "%Y-%m-%d")
            
            # Month Separation Logic
            month_key = dt_obj.strftime("%Y-%m")
            if current_month != month_key:
                current_month = month_key
                m_name = dt_obj.strftime("%b").upper()
                m_num = dt_obj.month
                m_info = monthly_stats[month_key]
                # Format: -----[MAR (3)] ---- [13/14d]---
                # User used 13/14d, maybe worked/total days? 
                # I'll use [TotalHrs / Days] to keep it consistent with previous info
                m_stat_str = f"[{m_info['hrs']:.1f}h/{m_info['days']}d]"
                sep_text = f"---[{m_name} ({m_num})] -- {m_stat_str}---"
                
                p.set(align="center")
                p.text(sep_text.center(42, "-") + "\n")
                p.set(align="left")

            # Date Format: MM-DD-YY
            date_str = dt_obj.strftime("%m-%d-%y")
            
            m_in = row[1] or "--:--"
            a_out = row[4] or row[2] or "--:--" 
            hrs = row[5]
            hm_str = format_hm(hrs)
            
            # Column widths: 12 (date), 10 (in), 10 (out), 10 (hrs) = 42 total
            p.text(f"{date_str:<12}   {m_in:>5}    {a_out:>5}   {hm_str:>6}\n")
            
        p.text(LINE + "\n")

    # ─── GAME-LIKE SUMMARY (Fun but Formal) ───────
    p.text(LINE + "\n")
    p.set(align="center", bold=True)
    p.text(">>> LEVEL SUMMARY <<<\n")
    p.set(align="left", bold=False)
    
    # Logic for Ranks
    pct = data["pct"]
    if pct >= 100: rank = "GODLIKE"
    elif pct >= 90: rank = "MASTER"
    elif pct >= 75: rank = "SENIOR"
    elif pct >= 50: rank = "JUNIOR"
    elif pct >= 25: rank = "APPRENTICE"
    else: rank = "NOVICE"

    # Status check
    has_today = False
    if data["recent"]:
        last_date = data["recent"][-1][0]
        if last_date == datetime.now().strftime("%Y-%m-%d"):
            has_today = True
    
    status = "GRINDING" if has_today else "IDLE"

    p.text(f"  RANK   : {rank}\n")
    p.text(f"  STATUS : {status}\n")
    p.text(f"  EXP    : {pct:.1f}% COMPLETE\n")
    p.text(LINE + "\n")

    # ─── FOOTER ───────────────────────────────────
    p.set(align="center")
    p.text("-- END OF LOG --\n")
    p.text("Keep up the good work!\n")

    p.cut()
    print("[OK] Time Summary printed.")


if __name__ == "__main__":
    print_summary()
