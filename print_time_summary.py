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
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "ojt_tracker.db")
TARGET_HOURS = 486.0  # Default; overridden by DB settings if available
VERSION = "1.9.1"
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


def get_best_printer():
    import subprocess
    import json
    
    fallback = "Generic / Text Only"
    
    try:
        # Get printers via PowerShell
        cmd = 'powershell -NoProfile -Command "Get-CimInstance Win32_Printer | Select-Object Name, Default | ConvertTo-Json"'
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        out = result.stdout.strip()
        
        if not out:
            return fallback
            
        printers = json.loads(out)
        if isinstance(printers, dict):
            printers = [printers]  # Handle single printer case
            
        # 1. Check Default Printer
        for p in printers:
            if p.get("Default"):
                name = p.get("Name", "").upper()
                # Ignore virtual printers
                if "PDF" not in name and "XPS" not in name and "ONENOTE" not in name:
                    print(f"[*] Selected Default Printer: {p['Name']}")
                    return p["Name"]
                    
        # 2. Check for any ECPOS-Capable / Thermal Printers
        pos_keywords = ["POS", "THERMAL", "BIXOLON", "EPSON", "TM-", "ZJIANG", "XP-", "XPRINTER", "RECEIPT"]
        for p in printers:
            name = p.get("Name", "").upper()
            if any(kw in name for kw in pos_keywords):
                print(f"[*] Found POS/Thermal Printer: {p['Name']}")
                return p["Name"]
                
    except Exception as e:
        print(f"[WARN] Printer auto-detect failed: {e}")
        
    # 3. Hard Coded Fallback
    print(f"[*] Using Hard Coded Printer: {fallback}")
    return fallback


def print_summary():
    data = fetch_summary()
    if not data:
        print("[ERR] Could not fetch summary.")
        return

    printer_name = get_best_printer()

    try:
        p = Win32Raw(printer_name)
        p.open()
    except Exception as e:
        print(f"[ERR] Printer connection failed for '{printer_name}': {e}")
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

    # Pre-load ruleset for the table
    ruleset_path = os.path.join(os.path.dirname(__file__), "data", "ruleset.json")
    ruleset = None
    if os.path.exists(ruleset_path):
        try:
            import json
            with open(ruleset_path, "r", encoding="utf-8") as f:
                ruleset = json.load(f)
        except: pass

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
        # Header adjusted for -D (Deductions) if ruleset exists
        if ruleset:
            p.text("DATE          IN    OUT    H:MM   -D\n")
        else:
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

            # Daily Transmutation Calculation for the table row
            d_str = ""
            if ruleset:
                def time_to_mins(t_str):
                    if not t_str: return None
                    try: h, m = map(int, t_str.split(':')); return h * 60 + m
                    except: return None

                m_start = time_to_mins(ruleset.get('morning_start') or ruleset.get('standard_shift_start'))
                m_end = time_to_mins(ruleset.get('morning_end'))
                a_start = time_to_mins(ruleset.get('afternoon_start'))
                a_end = time_to_mins(ruleset.get('afternoon_end') or ruleset.get('standard_shift_end'))
                penalty_rate = ruleset.get('penalty_per_15_mins_minutes', 0)
                grace = ruleset.get('grace_period_minutes', 0)
                fixed_daily = ruleset.get('fixed_daily_deduction_minutes', 0)

                # Normalize/Check
                cur_m_in = time_to_mins(row[1])
                cur_m_out = time_to_mins(row[2])
                cur_a_in = time_to_mins(row[3])
                cur_a_out = time_to_mins(row[4])
                if cur_a_in is not None and cur_a_in < 12*60: cur_a_in += 12*60
                if cur_a_out is not None and cur_a_out < 12*60: cur_a_out += 12*60

                diffs = []
                if cur_m_in and m_start and cur_m_in > m_start: diffs.append(cur_m_in - m_start)
                if cur_m_out and m_end and cur_m_out < m_end: diffs.append(m_end - cur_m_out)
                if cur_a_in and a_start and cur_a_in > a_start: diffs.append(cur_a_in - a_start)
                if cur_a_out and a_end and cur_a_out < a_end: diffs.append(a_end - cur_a_out)

                day_penalty = fixed_daily
                for diff in diffs:
                    if diff > grace and penalty_rate > 0:
                        day_penalty += ((diff + 14) // 15) * penalty_rate
                
                if day_penalty > 0:
                    d_str = f"{day_penalty/60.0:.1f}h"
            
            if ruleset:
                # Column widths: 10 (date), 6 (in), 6 (out), 8 (hrs), 12 (deduct) = 42 total
                p.text(f"{date_str:<10}    {m_in:>5} {a_out:>5}   {hm_str:>5}   {d_str:>4}\n")
            else:
                p.text(f"{date_str:<12}   {m_in:>5}    {a_out:>5}   {hm_str:>6}\n")
            
        p.text(LINE + "\n")

    # ─── TRANSMUTATION SUMMARY (Policy Deductions) ──────
    if ruleset:
        try:
            p.set(align="center", bold=True)
            p.text(">>> TRANSMUTATION LOG <<<\n")
            p.set(align="left", bold=False)

            def time_to_mins(t_str):
                if not t_str: return None
                try:
                    h, m = map(int, t_str.split(':'))
                    return h * 60 + m
                except: return None

            m_start = time_to_mins(ruleset.get('morning_start') or ruleset.get('standard_shift_start'))
            m_end = time_to_mins(ruleset.get('morning_end'))
            a_start = time_to_mins(ruleset.get('afternoon_start'))
            a_end = time_to_mins(ruleset.get('afternoon_end') or ruleset.get('standard_shift_end'))
            penalty_rate = ruleset.get('penalty_per_15_mins_minutes', 0)
            grace = ruleset.get('grace_period_minutes', 0)
            fixed_daily = ruleset.get('fixed_daily_deduction_minutes', 0)

            total_deduct_mins = 0
            for row in data["recent"]:
                # date, m_in, m_out, a_in, a_out, hrs
                m_in = time_to_mins(row[1])
                m_out = time_to_mins(row[2])
                a_in = time_to_mins(row[3])
                a_out = time_to_mins(row[4])

                if a_in is not None and a_in < 12*60: a_in += 12*60
                if a_out is not None and a_out < 12*60: a_out += 12*60

                diffs = []
                if m_in and m_start and m_in > m_start: diffs.append(m_in - m_start)
                if m_out and m_end and m_out < m_end: diffs.append(m_end - m_out)
                if a_in and a_start and a_in > a_start: diffs.append(a_in - a_start)
                if a_out and a_end and a_out < a_end: diffs.append(a_end - a_out)

                day_penalty = fixed_daily
                for diff in diffs:
                    if diff > grace and penalty_rate > 0:
                        units = (diff + 14) // 15
                        day_penalty += units * penalty_rate
                total_deduct_mins += day_penalty

            deduct_hrs = total_deduct_mins / 60.0
            adjusted_hrs = data["total_hrs"] - deduct_hrs
            
            p.text(f"  Penalty Rate: {penalty_rate}m / 15m block\n")
            if fixed_daily > 0:
                p.text(f"  Fixed/Day   : {fixed_daily}m (Break/Down)\n")
            p.text(f"  TOTAL TRANSMUTATION: -{deduct_hrs:.1f} hrs\n")
            p.set(bold=True)
            p.text(f"  CREDITED    : {adjusted_hrs:.1f} hrs\n")
            p.set(bold=False)
            
            # Progress based on Adjusted
            adj_pct = (adjusted_hrs / data["target"] * 100) if data["target"] > 0 else 0
            p.text(f"  ACTUAL EXP  : {adj_pct:.1f}% COMPLETE\n")
            p.text(LINE + "\n")
        except Exception as e:
            p.text(f"[Ruleset Error: {str(e)[:20]}]\n")
    else:
        # Fallback to simple Rank if no ruleset
        p.text(LINE + "\n")
        p.set(align="center", bold=True)
        p.text(">>> PROGRESS SUMMARY <<<\n")
        p.set(align="left", bold=False)
        p.text(f"  EXP: {data['pct']:.1f}% COMPLETE\n")
        p.text(LINE + "\n")

    # ─── FOOTER ───────────────────────────────────
    p.set(align="center")
    p.text("-- END OF LOG --\n")
    p.text("Keep up the good work!\n")

    p.cut()
    print("[OK] Time Summary printed.")


if __name__ == "__main__":
    print_summary()
