import os
from flask import Flask, render_template, request, jsonify
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

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(DATA_DIR, 'ojt_tracker.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_hours = db.Column(db.Float, default=486.0)

    @classmethod
    def get_target(cls):
        setting = cls.query.first()
        if not setting:
            setting = cls(target_hours=486.0)
            db.session.add(setting)
            db.session.commit()
        return setting.target_hours

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
    return render_template('index.html')

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
    target_hours = Settings.get_target()
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
                if curr_date.weekday() >= 5:
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
    setting = Settings.query.first()
    if not setting:
        setting = Settings(target_hours=486.0)
        db.session.add(setting)
        db.session.commit()
    
    if request.method == 'POST':
        data = request.json
        setting.target_hours = float(data.get('target_hours', 486.0))
        db.session.commit()
    
    return jsonify({'target_hours': setting.target_hours})

    return jsonify({'target_hours': setting.target_hours})

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
    # Only show last 30 days or current month
    now = datetime.now()
    month_start = now.replace(day=1).date()
    entries = OJTEntry.query.filter(OJTEntry.date >= month_start).order_by(OJTEntry.date).all()
    
    if not entries:
        return jsonify({'chart': None})

    data = {
        'Date': [e.date.strftime('%m-%d') for e in entries],
        'Hours': [e.total_hours for e in entries]
    }
    df = pd.DataFrame(data)
    
    # Theme-aware chart (simple logic)
    is_dark = request.args.get('theme', 'dark') == 'dark'
    plt.style.use('dark_background' if is_dark else 'default')
    
    plt.figure(figsize=(10, 4))
    sns.set_theme(style="whitegrid" if not is_dark else "darkgrid")
    
    plot = sns.barplot(x='Date', y='Hours', data=df, color='#cc0000') # Scarlet
    plot.set_title('Monthly OJT Progress', fontsize=14, pad=20)
    
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

if __name__ == '__main__':
    app.run(port=8080, debug=True)
