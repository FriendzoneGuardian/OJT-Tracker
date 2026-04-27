import os
from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import pandas as pd
import io

# Ensure portable data storage
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

SNAPSHOT_DIR = os.path.join(DATA_DIR, 'snapshots')
if not os.path.exists(SNAPSHOT_DIR):
    os.makedirs(SNAPSHOT_DIR)

VERSION = "1.8.0 (Chart Surgeon)"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(DATA_DIR, 'ojt_tracker.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_hours = db.Column(db.Float, default=486.0)
    include_saturday = db.Column(db.Boolean, default=False)
    include_sunday = db.Column(db.Boolean, default=False)
    allow_overtime = db.Column(db.Boolean, default=False)
    projection_strategy = db.Column(db.String(20), default='rolling') # 'rolling' or 'manual'
    manual_speed = db.Column(db.Float, default=8.0)
    user_name = db.Column(db.String(100), default='')

    @classmethod
    def get_settings_obj(cls):
        setting = cls.query.first()
        if not setting:
            setting = cls(
                target_hours=486.0, 
                include_saturday=False, 
                include_sunday=False,
                allow_overtime=False,
                projection_strategy='rolling',
                manual_speed=8.0,
                user_name=''
            )
            db.session.add(setting)
            db.session.commit()
        return setting

class Holiday(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    name = db.Column(db.String(100))

class ExcludedDate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    reason = db.Column(db.String(100))

class OJTEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    morn_in = db.Column(db.String(5))
    morn_out = db.Column(db.String(5))
    aftie_in = db.Column(db.String(5))
    aftie_out = db.Column(db.String(5))
    total_hours = db.Column(db.Float, default=0.0)
    is_night_shift = db.Column(db.Boolean, default=False)

    def calculate_hours(self, allow_overtime=False):
        def to_minutes(time_str, normalize_afternoon=False):
            if not time_str: return None
            try:
                h, m = map(int, time_str.split(':'))
                # Auto-Normalization: If it's a small hour like 1:00 in an afternoon context
                if normalize_afternoon and h < 10:
                    h += 12
                return h * 60 + m
            except:
                return None
        
        # Determine valid inputs
        # Normalization is only for standard shifts where 1:00 in afternoon definitely means 13:00.
        # For Night shifts, we let the crossover logic handle small hours.
        is_night = getattr(self, 'is_night_shift', False)
        
        m_in = to_minutes(self.morn_in)
        m_out = to_minutes(self.morn_out)
        a_in = to_minutes(self.aftie_in, normalize_afternoon=not is_night)
        a_out = to_minutes(self.aftie_out, normalize_afternoon=not is_night)
        
        total_mins = 0
        
        if is_night:
            # Night Owl Mode: Find the earliest In and latest Out among provided fields
            times = [m_in, m_out, a_in, a_out]
            valid_times = [x for x in times if x is not None]
            
            if len(valid_times) >= 2:
                start_point = valid_times[0]
                end_point = valid_times[-1]
                
                # Midnight crossover detection
                if end_point < start_point:
                    total_mins = (end_point + 1440) - start_point
                else:
                    total_mins = end_point - start_point
        else:
            # Standard Mode with Continuity Bridging
            # 1. Blocks Calculation
            m_block = (m_out - m_in) if (m_in is not None and m_out is not None) else 0
            a_block = (a_out - a_in) if (a_in is not None and a_out is not None) else 0
            
            # 2. Continuity Bridging (The 3-Punch / Missing Mid-Day Fix)
            # If we have a clear Start (m_in) and End (a_out), and at least one other punch is missing or redundant
            # but they collectively imply a single continuous span.
            if m_in is not None and a_out is not None:
                # If middle is partially missing (e.g. In --:-- In Out OR In Out --:-- Out)
                # or if the user simply logs 3 punches (In, mid-In, Out)
                if m_out is None or a_in is None:
                    # Bridge the entire span
                    span = a_out - m_in
                    if a_out < m_in: span += 1440 # Midnight walk
                    total_mins = span
                else:
                    # Both blocks exist, sum them
                    total_mins = max(0, m_block) + max(0, a_block)
            else:
                # Only one block or scattered punches
                total_mins = max(0, m_block) + max(0, a_block)
                
                # Phantom Logic: If only m_in and a_out provided (bridged above, 
                # but adding a fallback for safety if m_out/a_in are both None)
                if total_mins == 0 and m_in is not None and a_out is not None:
                    span = a_out - m_in
                    if a_out < m_in: span += 1440
                    total_mins = span

        calculated = float(total_mins) / 60.0
        
        # Overtime Cap Logic
        if not allow_overtime:
            self.total_hours = min(12.0, calculated)
        else:
            self.total_hours = calculated

# [v1.6.10 Rollback] cleanup_past_dates() was removed to preserve historical context for absence tracking.
# We no longer "time-travel" delete our past holidays!

with app.app_context():
    print("[BOOT] Phase 1: Validating Database Schema...")
    db.create_all()
    
    print("[BOOT] Phase 2: Running Clockwork Migrations...")
    try:
        from sqlalchemy import text
        # Settings table
        cols = db.session.execute(text("PRAGMA table_info(settings)")).fetchall()
        col_names = [c[1] for c in cols]
        if 'allow_overtime' not in col_names:
            db.session.execute(text("ALTER TABLE settings ADD COLUMN allow_overtime BOOLEAN DEFAULT 0"))
        if 'projection_strategy' not in col_names:
            db.session.execute(text("ALTER TABLE settings ADD COLUMN projection_strategy VARCHAR(20) DEFAULT 'rolling'"))
        if 'manual_speed' not in col_names:
            db.session.execute(text("ALTER TABLE settings ADD COLUMN manual_speed FLOAT DEFAULT 8.0"))
        if 'user_name' not in col_names:
            db.session.execute(text("ALTER TABLE settings ADD COLUMN user_name VARCHAR(100) DEFAULT ''"))
            
        # OJTEntry table
        cols_entry = db.session.execute(text("PRAGMA table_info(ojt_entry)")).fetchall()
        col_names_entry = [c[1] for c in cols_entry]
        if 'is_night_shift' not in col_names_entry:
            db.session.execute(text("ALTER TABLE ojt_entry ADD COLUMN is_night_shift BOOLEAN DEFAULT 0"))
        
        db.session.commit()
    except Exception as e:
        print(f"Migration Notice: {e}")

    print("[BOOT] Phase 3: Preserving Temporal Archives...")
    # cleanup_past_dates() -> Removed in v1.6.10 for data integrity
    # Seed 2026 Philippine Holidays
    print("[BOOT] Phase 4: Synchronizing Holidays...")
    if Holiday.query.count() == 0:
        ph_holidays = [
            ('2026-01-01', 'New Year\'s Day'),
            ('2026-02-17', 'Chinese New Year'),
            ('2026-02-25', 'EDSA People Power Revolution Anniversary'),
            ('2026-04-02', 'Maundy Thursday'),
            ('2026-04-03', 'Good Friday'),
            ('2026-04-04', 'Black Saturday'),
            ('2026-04-09', 'Araw ng Kagitingan'),
            ('2026-05-01', 'Labor Day'),
            ('2026-06-12', 'Independence Day'),
            ('2026-08-21', 'Ninoy Aquino Day'),
            ('2026-08-31', 'National Heroes Day'),
            ('2026-11-01', 'All Saints\' Day'),
            ('2026-11-02', 'All Souls\' Day'),
            ('2026-11-30', 'Bonifacio Day'),
            ('2026-12-08', 'Feast of the Immaculate Conception of Mary'),
            ('2026-12-25', 'Christmas Day'),
            ('2026-12-30', 'Rizal Day'),
            ('2026-12-31', 'Last Day of the Year')
        ]
        for date_str, name in ph_holidays:
            h = Holiday(date=datetime.strptime(date_str, '%Y-%m-%d').date(), name=name)
            db.session.add(h)
        db.session.commit()
    print("[BOOT] Engine Ready. Launching Handshake...")

@app.route('/')
def index():
    return render_template('index.html', version=VERSION)

@app.route('/api/entries', methods=['GET'])
def get_entries():
    entries = OJTEntry.query.order_by(OJTEntry.date.desc()).all()
    output = []
    for e in entries:
        output.append({
            'id': e.id,
            'date': e.date.strftime('%Y-%m-%d'),
            'morn_in': e.morn_in,
            'morn_out': e.morn_out,
            'aftie_in': e.aftie_in,
            'aftie_out': e.aftie_out,
            'total_hours': round(e.total_hours, 2)
        })
    return jsonify(output)

@app.route('/api/entries', methods=['POST'])
def add_entry():
    data = request.json
    date_obj = datetime.strptime(data['date'], '%Y-%m-%d').date()
    
    entry = OJTEntry.query.filter_by(date=date_obj).first()
    if not entry:
        entry = OJTEntry(date=date_obj)
        db.session.add(entry)
    
    entry.morn_in = data.get('morn_in')
    entry.morn_out = data.get('morn_out')
    entry.aftie_in = data.get('aftie_in')
    entry.aftie_out = data.get('aftie_out')
    entry.is_night_shift = bool(data.get('is_night_shift', False))
    
    settings = Settings.get_settings_obj()
    entry.calculate_hours(allow_overtime=settings.allow_overtime)
    
    db.session.commit()
    return jsonify({'message': 'Success', 'entry_id': entry.id})

@app.route('/api/entries/recalculate', methods=['POST'])
def recalculate_all():
    try:
        entries = OJTEntry.query.all()
        settings = Settings.get_settings_obj()
        for e in entries:
            e.calculate_hours(allow_overtime=settings.allow_overtime)
        db.session.commit()
        return jsonify({'status': 'success', 'message': f'Recalculated {len(entries)} entries.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/entries/<int:entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    entry = OJTEntry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    return jsonify({'message': 'Entry deleted'})

@app.route('/api/stats')
def get_stats():
    total_rendered = db.session.query(db.func.sum(OJTEntry.total_hours)).scalar() or 0
    settings = Settings.get_settings_obj()
    target_hours = settings.target_hours
    left = max(0, target_hours - total_rendered)
    
    # Precise Trajectory Analysis
    entries = OJTEntry.query.order_by(OJTEntry.date.desc()).limit(14).all() # Last 14 entries for avg
    avg_per_day = 0
    expected_end = None
    
    if settings.projection_strategy == 'manual':
        avg_per_day = settings.manual_speed
    elif entries:
        avg_per_day = sum(e.total_hours for e in entries) / len(entries)
    
    if avg_per_day > 0:
        # Iterative projection skipping weekends, holidays, and exclusions
        holidays = {h.date for h in Holiday.query.all()}
        exclusions = {x.date for x in ExcludedDate.query.all()}
        
        non_working_dates = holidays.union(exclusions)
        
        # Buffer for ghost days (precision hardening)
        hours_rem = left - 0.001 
        curr_date = datetime.now().date()
        
        # Limit safely to avoid infinite loops (max 2 years forward)
        max_days = 730
        day_count = 0
        
        while hours_rem > 0 and day_count < max_days:
            curr_date += timedelta(days=1)
            day_count += 1
            
            # Check for weekends (5 = Saturday, 6 = Sunday)
            is_working_weekend = False
            if curr_date.weekday() == 5 and settings.include_saturday:
                is_working_weekend = True
            if curr_date.weekday() == 6 and settings.include_sunday:
                is_working_weekend = True

            if curr_date.weekday() >= 5 and not is_working_weekend:
                continue
            
            # Check for specific non-working dates
            if curr_date in non_working_dates:
                continue
            
            hours_rem -= avg_per_day
        
        if day_count < max_days:
            expected_end = curr_date.strftime('%Y-%m-%d')
        else:
            expected_end = "Projected too far"

    # Monthly stats
    now = datetime.now()
    first_day_curr = now.replace(day=1)
    last_month = first_day_curr - timedelta(days=1)
    first_day_prev = last_month.replace(day=1)
    
    curr_month_hours = db.session.query(db.func.sum(OJTEntry.total_hours)).filter(OJTEntry.date >= first_day_curr).scalar() or 0
    prev_month_hours = db.session.query(db.func.sum(OJTEntry.total_hours)).filter(OJTEntry.date >= first_day_prev, OJTEntry.date < first_day_curr).scalar() or 0
    
    return jsonify({
        'total_rendered': round(total_rendered, 1),
        'total_left': round(left, 1),
        'curr_month': round(curr_month_hours, 1),
        'prev_month': round(prev_month_hours, 1),
        'target': target_hours,
        'avg_per_day': round(avg_per_day, 1),
        'expected_end': expected_end,
        'projection_strategy': settings.projection_strategy
    })

@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    setting = Settings.get_settings_obj()
    
    if request.method == 'POST':
        data = request.json
        setting.target_hours = float(data.get('target_hours', setting.target_hours))
        setting.include_saturday = bool(data.get('include_saturday', False))
        setting.include_sunday = bool(data.get('include_sunday', False))
        setting.allow_overtime = bool(data.get('allow_overtime', False))
        setting.projection_strategy = data.get('projection_strategy', 'rolling')
        setting.manual_speed = float(data.get('manual_speed', 8.0))
        setting.user_name = str(data.get('user_name', setting.user_name or ''))
        db.session.commit()
    
    return jsonify({
        'target_hours': setting.target_hours,
        'include_saturday': setting.include_saturday,
        'include_sunday': setting.include_sunday,
        'allow_overtime': setting.allow_overtime,
        'projection_strategy': setting.projection_strategy,
        'manual_speed': setting.manual_speed,
        'user_name': setting.user_name or ''
    })

@app.route('/api/holidays', methods=['GET', 'POST'])
def handle_holidays():
    if request.method == 'POST':
        data = request.json
        date_obj = datetime.strptime(data['date'], '%Y-%m-%d').date()
        holiday = Holiday(date=date_obj, name=data.get('name', 'Holiday'))
        db.session.add(holiday)
        db.session.commit()
        return jsonify({'message': 'Success'})
    
    holidays = Holiday.query.order_by(Holiday.date).all()
    return jsonify([{'id': h.id, 'date': h.date.strftime('%Y-%m-%d'), 'name': h.name} for h in holidays])

@app.route('/api/holidays/sync', methods=['POST'])
def sync_holidays():
    try:
        data = request.json or {}
        year = data.get('year', datetime.now().year)
        
        import subprocess
        import sys
        import json
        
        script_path = os.path.join(BASE_DIR, 'scraper.py')
        result = subprocess.run([sys.executable, script_path, str(year)], capture_output=True, text=True)
        
        if result.returncode != 0:
            return jsonify({'error': 'Scraper failed to execute'}), 500
            
        output_lines = result.stdout.strip().split('\n')
        json_output = None
        for line in reversed(output_lines):
            try:
                json_output = json.loads(line)
                break
            except Exception:
                continue
                
        if not json_output or 'error' in json_output:
            return jsonify({'error': json_output.get('error', 'Unknown error parsing scraper output')}), 500
            
        holidays_scraped = json_output.get('holidays', [])
        added_count = 0
        
        for h in holidays_scraped:
            date_obj = datetime.strptime(h['date'], '%Y-%m-%d').date()
            # Check for duplicate
            if not Holiday.query.filter_by(date=date_obj).first():
                db.session.add(Holiday(date=date_obj, name=h['name']))
                added_count += 1
                
        db.session.commit()
        return jsonify({'message': f'Successfully synced {added_count} new holidays for {year}.', 'count': added_count})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cleanup_year', methods=['POST'])
def cleanup_year():
    try:
        today = datetime.now().date()
        Holiday.query.filter(Holiday.date <= today).delete()
        ExcludedDate.query.filter(ExcludedDate.date <= today).delete()
        db.session.commit()
        return jsonify({'message': 'Year-end sweep complete! Past holidays and exclusions gracefully removed.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/holidays/<int:id>', methods=['DELETE'])
def delete_holiday(id):
    holiday = Holiday.query.get_or_404(id)
    db.session.delete(holiday)
    db.session.commit()
    return jsonify({'message': 'Deleted'})

@app.route('/api/exclusions', methods=['GET', 'POST'])
def handle_exclusions():
    if request.method == 'POST':
        data = request.json
        date_obj = datetime.strptime(data['date'], '%Y-%m-%d').date()
        exc = ExcludedDate(date=date_obj, reason=data.get('reason', 'Excluded'))
        db.session.add(exc)
        db.session.commit()
        return jsonify({'message': 'Success'})
    
    exclusions = ExcludedDate.query.order_by(ExcludedDate.date).all()
    return jsonify([{'id': e.id, 'date': e.date.strftime('%Y-%m-%d'), 'reason': e.reason} for e in exclusions])

@app.route('/api/exclusions/<int:id>', methods=['DELETE'])
def delete_exclusion(id):
    exc = ExcludedDate.query.get_or_404(id)
    db.session.delete(exc)
    db.session.commit()
    return jsonify({'message': 'Deleted'})

@app.route('/api/chart-data')
def get_chart_data():
    """Returns raw JSON data for Chart.js rendering on the frontend."""
    days = int(request.args.get('days', 90))
    start_date = (datetime.now() - timedelta(days=days)).date()
    
    entries = OJTEntry.query.filter(OJTEntry.date >= start_date).order_by(OJTEntry.date).all()
    
    if not entries:
        return jsonify({'labels': [], 'hours': [], 'cumulative': [], 'monthly': {}, 'weekday': {}})

    # Daily data (for line/bar charts)
    labels = [e.date.strftime('%m-%d') for e in entries]
    hours = [round(e.total_hours, 2) for e in entries]
    
    # Cumulative running total (for combo chart)
    # Need ALL entries for accurate cumulative, not just the windowed ones
    all_entries = OJTEntry.query.order_by(OJTEntry.date).all()
    cum_total = 0
    cum_map = {}
    for e in all_entries:
        cum_total += e.total_hours
        cum_map[e.date.strftime('%m-%d')] = round(cum_total, 2)
    cumulative = [cum_map.get(l, 0) for l in labels]
    
    # Monthly aggregation (for horizontal bar)
    monthly_data = {}
    for e in all_entries:
        month_key = e.date.strftime('%b %Y')  # e.g. "Apr 2026"
        monthly_data[month_key] = round(monthly_data.get(month_key, 0) + e.total_hours, 2)
    
    # Weekday aggregation (for polar/radial)
    weekday_sums = {}
    weekday_counts = {}
    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    for e in all_entries:
        wd = day_names[e.date.weekday()]
        weekday_sums[wd] = weekday_sums.get(wd, 0) + e.total_hours
        weekday_counts[wd] = weekday_counts.get(wd, 0) + 1
    weekday_avg = {d: round(weekday_sums.get(d, 0) / max(weekday_counts.get(d, 1), 1), 2) for d in day_names}
    
    # Heatmap grid (8-week GitHub-style)
    weeks = 8
    today = datetime.now().date()
    # Find start: go back to the Monday of (weeks-1) weeks ago
    start_of_window = today - timedelta(days=today.weekday() + (7 * (weeks - 1)))
    entry_map = {e.date: e.total_hours for e in all_entries}
    
    heatmap_grid = []  # 7 rows (Mon-Sun) x 8 cols (weeks)
    for d in range(7):
        row = []
        for w in range(weeks):
            target_date = start_of_window + timedelta(weeks=w, days=d)
            if target_date > today:
                row.append(-1)  # Future
            elif target_date in entry_map:
                row.append(round(entry_map[target_date], 2))
            else:
                row.append(0)
        heatmap_grid.append(row)
    
    # Week labels for heatmap x-axis
    week_labels = []
    for w in range(weeks):
        week_start = start_of_window + timedelta(weeks=w)
        week_labels.append(week_start.strftime('%m/%d'))
    
    settings = Settings.get_settings_obj()
    
    return jsonify({
        'labels': labels,
        'hours': hours,
        'cumulative': cumulative,
        'target': settings.target_hours,
        'monthly': monthly_data,
        'weekday': weekday_avg,
        'heatmap': heatmap_grid,
        'heatmap_weeks': week_labels,
    })

@app.route('/api/export')
def export_entries():
    try:
        entries = OJTEntry.query.order_by(OJTEntry.date).all()
        data = []
        for e in entries:
            data.append({
                'Date': str(e.date) if e.date else '',
                'Morning In': str(e.morn_in or ''),
                'Morning Out': str(e.morn_out or ''),
                'Afternoon In': str(e.aftie_in or ''),
                'Afternoon Out': str(e.aftie_out or ''),
                'Night Shift': 'Yes' if getattr(e, 'is_night_shift', False) else 'No',
                'Total Hours': float(e.total_hours or 0.0)
            })
        df = pd.DataFrame(data)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='OJT Log')
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'OJT_Log_{datetime.now().strftime("%Y-%m-%d")}.xlsx'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/multi')
def export_multi():
    try:
        fmt = request.args.get('format', 'xlsx')
        entries = OJTEntry.query.order_by(OJTEntry.date).all()
        data = []
        for e in entries:
            data.append({
                'Date': str(e.date) if e.date else '',
                'Morning In': str(e.morn_in or ''),
                'Morning Out': str(e.morn_out or ''),
                'Afternoon In': str(e.aftie_in or ''),
                'Afternoon Out': str(e.aftie_out or ''),
                'Night Shift': 'Yes' if getattr(e, 'is_night_shift', False) else 'No',
                'Total Hours': float(e.total_hours or 0.0)
            })
        df = pd.DataFrame(data)
        
        output = io.BytesIO()
        
        if fmt == 'csv':
            df.to_csv(output, index=False)
            output.seek(0)
            return send_file(output, mimetype='text/csv', as_attachment=True, download_name=f'OJT_Export_{datetime.now().strftime("%Y%m%d")}.csv')
        
        elif fmt == 'txt':
            text = f"OJT TRACKER SUMMARY - {datetime.now().strftime('%Y-%m-%d')}\n"
            text += "="*40 + "\n"
            for _, row in df.iterrows():
                shift_tag = " [NIGHT]" if row.get('Night Shift') == 'Yes' else ""
                text += f"{row['Date']}{shift_tag} | {row['Total Hours']}h | (AM: {row['Morning In']}-{row['Morning Out']} | PM: {row['Afternoon In']}-{row['Afternoon Out']})\n"
            output.write(text.encode('utf-8'))
            output.seek(0)
            return send_file(output, mimetype='text/plain', as_attachment=True, download_name=f'OJT_Summary_{datetime.now().strftime("%Y%m%d")}.txt')
        
        else: # Default XLSX
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='OJT Log')
            output.seek(0)
            return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name=f'OJT_Log_{datetime.now().strftime("%Y%m%d")}.xlsx')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/snapshot', methods=['POST'])
def create_snapshot():
    import shutil
    db_path = os.path.join(DATA_DIR, 'ojt_tracker.db')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_path = os.path.join(SNAPSHOT_DIR, f"snapshot_{timestamp}.db.bak")
    shutil.copy2(db_path, snapshot_path)
    return jsonify({'status': 'success', 'file': f"snapshot_{timestamp}.db.bak"})

@app.route('/api/snapshots')
def list_snapshots():
    files = [f for f in os.listdir(SNAPSHOT_DIR) if f.endswith('.db.bak')]
    files.sort(reverse=True)
    return jsonify(files)

@app.route('/api/import', methods=['POST'])
def import_data():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    temp_path = os.path.join(DATA_DIR, 'temp_import_' + file.filename)
    file.save(temp_path)

    imported_count = 0
    skipped_count = 0

    try:
        if temp_path.endswith('.db') or temp_path.endswith('.db.bak'):
            # SQLite Import
            import sqlite3
            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()
            cursor.execute("SELECT date, morn_in, morn_out, aftie_in, aftie_out, total_hours FROM ojt_entry")
            rows = cursor.fetchall()
            for row in rows:
                date_str = row[0]
                # Check for duplicate
                exists = OJTEntry.query.filter_by(date=datetime.strptime(date_str, '%Y-%m-%d').date()).first()
                if not exists:
                    new_entry = OJTEntry(
                        date=datetime.strptime(date_str, '%Y-%m-%d').date(),
                        morn_in=row[1],
                        morn_out=row[2],
                        aftie_in=row[3],
                        aftie_out=row[4]
                    )
                    # Calibration Sync
                    new_entry.calculate_hours(allow_overtime=Settings.get_settings_obj().allow_overtime)
                    db.session.add(new_entry)
                    imported_count += 1
                else:
                    skipped_count += 1
            conn.close()

        elif temp_path.endswith('.csv'):
            df = pd.read_csv(temp_path)
            for _, row in df.iterrows():
                dt = pd.to_datetime(row['Date']).date()
                exists = OJTEntry.query.filter_by(date=dt).first()
                if not exists:
                    new_entry = OJTEntry(
                        date=dt,
                        morn_in=row.get('Morning In', row.get('morn_in')),
                        morn_out=row.get('Morning Out', row.get('morn_out')),
                        aftie_in=row.get('Afternoon In', row.get('aftie_in')),
                        aftie_out=row.get('Afternoon Out', row.get('aftie_out'))
                    )
                    # Calibration Sync
                    new_entry.calculate_hours(allow_overtime=Settings.get_settings_obj().allow_overtime)
                    db.session.add(new_entry)
                    imported_count += 1
                else:
                    skipped_count += 1

        elif temp_path.endswith('.xlsx') or temp_path.endswith('.xls'):
            df = pd.read_excel(temp_path)
            for _, row in df.iterrows():
                dt = pd.to_datetime(row['Date']).date()
                exists = OJTEntry.query.filter_by(date=dt).first()
                if not exists:
                    new_entry = OJTEntry(
                        date=dt,
                        morn_in=row.get('Morning In', row.get('morn_in')),
                        morn_out=row.get('Morning Out', row.get('morn_out')),
                        aftie_in=row.get('Afternoon In', row.get('aftie_in')),
                        aftie_out=row.get('Afternoon Out', row.get('aftie_out'))
                    )
                    # Calibration Sync
                    new_entry.calculate_hours(allow_overtime=Settings.get_settings_obj().allow_overtime)
                    db.session.add(new_entry)
                    imported_count += 1
                else:
                    skipped_count += 1
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return jsonify({
        'status': 'success',
        'imported': imported_count,
        'skipped': skipped_count
    })

if __name__ == '__main__':
    # Stealth mode for Electron: Suppress banner and logging if not in debug
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
        
    app.run(host='127.0.0.1', port=8080, debug=False)
