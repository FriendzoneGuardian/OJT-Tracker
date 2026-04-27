# 🖨️ Thermal Printing Guide

**OJT-Tracker** includes a standalone thermal printing script (`print_time_summary.py`) for the **Epson TM-82X** (or any printer using the **Generic / Text Only** Windows driver).

## Setup

### Prerequisites
```bash
pip install python-escpos
```

Ensure your printer is installed in Windows as **"Generic / Text Only"**.

### Running
```bash
python print_time_summary.py
```

---

## Receipt Layout

The receipt prints on **58mm thermal paper** using a 42-column ESC/POS layout.

### Sections

#### 1. Header
```
OJT TRACKER - 1.7.3
   Time Summary
   [User Name]
Apr 27, 2026  01:32 PM
------------------------------------------
```

#### 2. Stats Block
```
Target     : 486 hrs
Rendered   : 264.0 hrs (35d)
Remaining  : 222.0 hrs (27d left)

Avg/Day    : 7.8 hrs (7:48)
```

#### 3. Progress Bar
```
[###########.........] 54.3%
------------------------------------------
```

#### 4. Official OJT Log
Full chronological entry history, grouped by month with inline monthly stats:

```
       OFFICIAL OJT LOG
DATE           IN       OUT      H:MM
------[MAR (3)] -- [64.5h/13d]------
03-01-26      08:00    17:00     8:00
03-02-26      08:00    16:30     7:30
...
------[APR (4)] -- [48.0h/7d]-------
04-01-26      08:00    17:00     8:00
```

#### 5. Level Summary
```
------------------------------------------
        >>> LEVEL SUMMARY <<<
  RANK   : JUNIOR
  STATUS : GRINDING
  EXP    : 54.3% COMPLETE
------------------------------------------
```

- **RANK** progression: NOVICE → APPRENTICE → JUNIOR → SENIOR → MASTER → GODLIKE
- **STATUS**: GRINDING if you have an entry for today, IDLE otherwise.

#### 6. Footer
```
      -- END OF LOG --
    Keep up the good work!
```

---

## Configuration

At the top of `print_time_summary.py`:

```python
PRINTER_NAME = "Generic / Text Only"  # Must match Windows printer name exactly
DB_PATH = ...                          # Auto-resolved from project root
VERSION  = "1.7.3"                    # Keep in sync with app.py
```

> **Note**: To change the paper width, update `LINE = "-" * 42`. The 42-column layout is calibrated for 58mm thermal paper at default font size.
