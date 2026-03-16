import os
from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import io
import base64

# Ensure portable data storage
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

SNAPSHOT_DIR = os.path.join(DATA_DIR, 'snapshots')
if not os.path.exists(SNAPSHOT_DIR):
    os.makedirs(SNAPSHOT_DIR)

VERSION = "1.5.0"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(DATA_DIR, 'ojt_tracker.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_hours = db.Column(db.Float, default=486.0)
    include_saturday = db.Column(db.Boolean, default=False)
    include_sunday = db.Column(db.Boolean, default=False)

    @classmethod
    def get_settings_obj(cls):
        setting = cls.query.first()
        if not setting:
            setting = cls(target_hours=486.0, include_saturday=False, include_sunday=False)
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

    def calculate_hours(self):
        def to_minutes(time_str):
            if not time_str: return 0
            h, m = map(int, time_str.split(':'))
            return h * 60 + m
        
        m_in = to_minutes(self.morn_in)
        m_out = to_minutes(self.morn_out)
        a_in = to_minutes(self.aftie_in)
        a_out = to_minutes(self.aftie_out)
        
        m_total = max(0, m_out - m_in)
        a_total = max(0, a_out - a_in)
        
        self.total_hours = (m_total + a_total) / 60.0

def cleanup_past_dates():
    today = datetime.now().date()
    # Delete past holidays and exclusions
    Holiday.query.filter(Holiday.date < today).delete()
    ExcludedDate.query.filter(ExcludedDate.date < today).delete()
    db.session.commit()

with app.app_context():
    db.create_all()
    cleanup_past_dates()
    # Seed 2026 Philippine Holidays
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
    entry.calculate_hours()
    
    db.session.commit()
    return jsonify({'message': 'Success', 'entry_id': entry.id})

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
    
    if entries:
        avg_per_day = sum(e.total_hours for e in entries) / len(entries)
        if avg_per_day > 0:
            # Iterative projection skipping weekends, holidays, and exclusions
            holidays = {h.date for h in Holiday.query.all()}
            exclusions = {x.date for x in ExcludedDate.query.all()}
            
            non_working_dates = holidays.union(exclusions)
            
            hours_rem = left
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
        'expected_end': expected_end
    })

@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    setting = Settings.get_settings_obj()
    
    if request.method == 'POST':
        data = request.json
        setting.target_hours = float(data.get('target_hours', setting.target_hours))
        setting.include_saturday = bool(data.get('include_saturday', False))
        setting.include_sunday = bool(data.get('include_sunday', False))
        db.session.commit()
    
    return jsonify({
        'target_hours': setting.target_hours,
        'include_saturday': setting.include_saturday,
        'include_sunday': setting.include_sunday
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

@app.route('/api/chart')
def get_chart():
    chart_type = request.args.get('type', 'heatmap')
    # Use 60 days for heatmap, or current month for bar
    limit_days = 60 if chart_type == 'heatmap' else 31
    start_date = (datetime.now() - timedelta(days=limit_days)).date()
    
    entries = OJTEntry.query.filter(OJTEntry.date >= start_date).order_by(OJTEntry.date).all()
    
    if not entries:
        return jsonify({'chart': None})

    # Theme-aware chart
    is_dark = request.args.get('theme', 'dark') in ['dark', 'amoled']
    plt.style.use('dark_background' if is_dark else 'default')
    
    if chart_type == 'bar':
        data = {
            'Date': [e.date.strftime('%m-%d') for e in entries],
            'Hours': [e.total_hours for e in entries]
        }
        df = pd.DataFrame(data)
        plt.figure(figsize=(10, 4))
        sns.set_theme(style="whitegrid" if not is_dark else "darkgrid")
        plot = sns.barplot(x='Date', y='Hours', data=df, color='#cc0000') # Scarlet
        plot.set_title('OJT Progress (Bar)', fontsize=14, pad=20)
    else:
        # Heatmap Logic (Github Style: Weeks vs Days)
        # We'll map last 8 weeks
        import numpy as np
        weeks = 8
        grid = np.zeros((7, weeks))
        today = datetime.now().date()
        # Find start of the window (8 weeks ago, starting on a Sunday)
        start_of_window = today - timedelta(days=today.weekday() + (7 * (weeks-1)))
        
        entry_map = {e.date: e.total_hours for e in entries}
        
        for w in range(weeks):
            for d in range(7):
                target_date = start_of_window + timedelta(weeks=w, days=d)
                if target_date in entry_map:
                    grid[d, w] = entry_map[target_date]
                elif target_date > today:
                    grid[d, w] = -1 # Future dates

        plt.figure(figsize=(10, 3))
        # Custom Scarlet Gradient
        cmap = sns.dark_palette("#cc0000", as_cmap=True) if is_dark else sns.light_palette("#cc0000", as_cmap=True)
        
        # Mask future dates
        mask = grid == -1
        
        plot = sns.heatmap(grid, annot=False, fmt=".1f", cmap=cmap, cbar=True, 
                           mask=mask, linewidths=.5, linecolor='#111' if is_dark else '#eee',
                           yticklabels=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
        plot.set_title('Temporal Archive Intensity (Heatmap)', fontsize=12, pad=15)
        plt.xlabel('Weeks Ago → Today')

    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight', transparent=True)
    img.seek(0)
    
    chart_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return jsonify({'chart': f"data:image/png;base64,{chart_url}"})

@app.route('/api/export')
def export_entries():
    entries = OJTEntry.query.order_by(OJTEntry.date).all()
    data = []
    for e in entries:
        data.append({
            'Date': e.date,
            'Morning In': e.morn_in,
            'Morning Out': e.morn_out,
            'Afternoon In': e.aftie_in,
            'Afternoon Out': e.aftie_out,
            'Total Hours': e.total_hours
        })
    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='OJT Log')
    output.seek(0)
    
    from flask import send_file
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'OJT_Log_{datetime.now().strftime("%Y-%m-%d")}.xlsx'
    )

@app.route('/api/export/multi')
def export_multi():
    fmt = request.args.get('format', 'xlsx')
    entries = OJTEntry.query.order_by(OJTEntry.date).all()
    data = []
    for e in entries:
        data.append({
            'Date': e.date,
            'Morning In': e.morn_in,
            'Morning Out': e.morn_out,
            'Afternoon In': e.aftie_in,
            'Afternoon Out': e.aftie_out,
            'Total Hours': e.total_hours
        })
    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    
    if fmt == 'csv':
        df.to_csv(output, index=False)
        output.seek(0)
        return send_file(output, mimetype='text/csv', as_attachment=True, download_name=f'OJT_Export_{datetime.now().strftime("%Y%m%d")}.csv')
    
    elif fmt == 'txt':
        # Text Summary
        text = f"OJT TRACKER SUMMARY - {datetime.now().strftime('%Y-%m-%d')}\n"
        text += "="*40 + "\n"
        for _, row in df.iterrows():
            text += f"{row['Date']} | {row['Total Hours']}h | (AM: {row['Morning In']}-{row['Morning Out']} | PM: {row['Afternoon In']}-{row['Afternoon Out']})\n"
        output.write(text.encode('utf-8'))
        output.seek(0)
        return send_file(output, mimetype='text/plain', as_attachment=True, download_name=f'OJT_Summary_{datetime.now().strftime("%Y%m%d")}.txt')
    
    else: # Default XLSX
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='OJT Log')
        output.seek(0)
        return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name=f'OJT_Log_{datetime.now().strftime("%Y%m%d")}.xlsx')

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
                        aftie_out=row[4],
                        total_hours=row[5]
                    )
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
                        aftie_out=row.get('Afternoon Out', row.get('aftie_out')),
                        total_hours=float(row.get('Total Hours', row.get('total_hours', 0)))
                    )
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
                        aftie_out=row.get('Afternoon Out', row.get('aftie_out')),
                        total_hours=float(row.get('Total Hours', row.get('total_hours', 0)))
                    )
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
