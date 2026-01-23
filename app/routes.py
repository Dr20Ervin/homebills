import json
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import func, extract
from .models import db, User, Category, BillEntry, AppSetting

main = Blueprint('main', __name__)

# --- GATEKEEPER: FORCE SETUP IF NO ADMIN ---
@main.before_request
def check_setup():
    if request.endpoint and 'static' in request.endpoint:
        return

    if request.endpoint == 'main.setup':
        return

    admin_exists = User.query.filter_by(role='Admin').first()
    
    if not admin_exists:
        return redirect(url_for('main.setup'))

@main.route('/setup', methods=['GET', 'POST'])
def setup():

    if User.query.filter_by(role='Admin').first():
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        username = request.form.get('admin_user')
        password = request.form.get('admin_pass')
        
        if not username or not password:
            flash("Admin username and password are required.")
            return redirect(url_for('main.setup'))

        admin = User(username=username, role='Admin')
        admin.set_password(password)
        db.session.add(admin)

        cat_names = request.form.getlist('cat_name[]')
        cat_units = request.form.getlist('cat_unit[]')
        cat_costs = request.form.getlist('cat_cost[]')
        cat_icons = request.form.getlist('cat_icon[]')
        cat_colors = request.form.getlist('cat_color[]')

        for i in range(len(cat_names)):
            if cat_names[i].strip(): # Only add if name exists
                new_cat = Category(
                    name=cat_names[i],
                    unit=cat_units[i],
                    default_cost=float(cat_costs[i] or 0),
                    icon=cat_icons[i],
                    color=cat_colors[i]
                )
                db.session.add(new_cat)

        # 3. Default Settings
        db.session.add(AppSetting(key='currency', value='$'))
        
        db.session.commit()
        flash("Setup Complete!")
        return redirect(url_for('main.login'))

    return render_template('setup.html')

# --- HELPERS ---
def get_currency():
    setting = AppSetting.query.get('currency')
    return setting.value if setting else "$"

def get_pivoted_data():
    bills = BillEntry.query.order_by(BillEntry.date.desc()).all()
    grouped = {}
    for bill in bills:
        month_key = bill.date.strftime('%Y-%m')
        if month_key not in grouped:
            grouped[month_key] = {'date_obj': bill.date, 'total': 0}
        
        cat_name = bill.category.name if bill.category else "Deleted"
        grouped[month_key][f"{cat_name}_cost"] = bill.cost
        grouped[month_key][f"{cat_name}_unit"] = bill.usage
        grouped[month_key]['total'] += bill.cost
    return sorted(grouped.values(), key=lambda x: x['date_obj'], reverse=True)

# --- AUTH (SECURE) ---
@main.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and user.check_password(request.form.get('password')):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        flash('Invalid Login')
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/toggle-theme', methods=['POST'])
@login_required
def toggle_theme():
    current_user.theme = 'dark' if current_user.theme == 'light' else 'light'
    db.session.commit()
    return jsonify({'status': 'success', 'new_theme': current_user.theme})

# --- DASHBOARD ---
@main.route('/dashboard')
@login_required
def dashboard():
    categories = Category.query.filter_by(is_active=True).all()
    pivoted_data = get_pivoted_data()
    currency = get_currency()

    chart_labels = [row['date_obj'].strftime('%Y-%m') for row in pivoted_data[:12]][::-1]
    datasets = []
    for cat in categories:
        data_points = []
        for row in pivoted_data[:12]:
            data_points.append(row.get(f"{cat.name}_cost", 0))
        datasets.append({'label': cat.name, 'data': data_points[::-1], 'backgroundColor': cat.color or '#4e73df'})

    pie_labels = []
    pie_data = []
    pie_colors = []
    pie_breakdown = []
    
    if pivoted_data:
        latest_month = pivoted_data[0]
        for cat in categories:
            cost = latest_month.get(f"{cat.name}_cost", 0)
            if cost > 0:
                pie_labels.append(cat.name)
                pie_data.append(cost)
                pie_colors.append(cat.color or '#ccc')
                pie_breakdown.append({
                    'name': cat.name,
                    'cost': cost,
                    'color': cat.color or '#ccc',
                    'unit_val': latest_month.get(f"{cat.name}_unit", 0),
                    'unit_label': cat.unit
                })

    return render_template('dashboard.html', 
                         user=current_user,
                         categories=categories,
                         rows=pivoted_data[:6],
                         currency=currency,
                         chart_labels=json.dumps(chart_labels),
                         chart_datasets=json.dumps(datasets),
                         pie_labels=json.dumps(pie_labels),
                         pie_data=json.dumps(pie_data),
                         pie_colors=json.dumps(pie_colors),
                         pie_breakdown=pie_breakdown)

# --- RECORDS ---
@main.route('/records')
@login_required
def records():
    year_filter = request.args.get('year')
    query = BillEntry.query
    if year_filter and year_filter != 'All Time':
        query = query.filter(extract('year', BillEntry.date) == int(year_filter))
    
    bills = query.order_by(BillEntry.date.desc()).all()
    categories = Category.query.filter_by(is_active=True).all()
    return render_template('view_records.html', user=current_user, bills=bills, categories=categories, selected_year=year_filter)

# --- SETTINGS ---
@main.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if current_user.role != 'Admin': return redirect(url_for('main.dashboard'))
    if request.method == 'POST' and 'currency' in request.form:
        setting = AppSetting.query.get('currency')
        if not setting: 
            setting = AppSetting(key='currency')
            db.session.add(setting)
        setting.value = request.form.get('currency')
        db.session.commit()
    return render_template('settings.html', user=current_user, users=User.query.all(), categories=Category.query.all(), currency=get_currency())

# --- CATEGORY ACTIONS ---
@main.route('/category/add', methods=['POST'])
@login_required
def add_category():
    if current_user.role != 'Admin': return redirect(url_for('main.settings'))
    db.session.add(Category(name=request.form.get('name'), unit=request.form.get('unit'), icon=request.form.get('icon'), color=request.form.get('color'), default_cost=float(request.form.get('default_cost') or 0)))
    db.session.commit()
    return redirect(url_for('main.settings'))

@main.route('/category/edit/<int:id>', methods=['POST'])
@login_required
def edit_category(id):
    if current_user.role != 'Admin': return redirect(url_for('main.settings'))
    cat = Category.query.get(id)
    if cat:
        cat.name = request.form.get('name')
        cat.unit = request.form.get('unit')
        cat.icon = request.form.get('icon')
        cat.color = request.form.get('color')
        cat.default_cost = float(request.form.get('default_cost') or 0)
        db.session.commit()
    return redirect(url_for('main.settings'))

@main.route('/category/delete/<int:id>')
@login_required
def delete_category(id):
    if current_user.role != 'Admin': return redirect(url_for('main.settings'))
    cat = Category.query.get(id)
    if cat:
        db.session.delete(cat)
        db.session.commit()
    return redirect(url_for('main.settings'))

@main.route('/user/add', methods=['POST'])
@login_required
def add_user():
    if current_user.role != 'Admin': return redirect(url_for('main.settings'))
    if not User.query.filter_by(username=request.form.get('username')).first():
        new_user = User(username=request.form.get('username'), role=request.form.get('role'))
        new_user.set_password(request.form.get('password'))
        db.session.add(new_user)
        db.session.commit()
    return redirect(url_for('main.settings'))

@main.route('/user/edit/<int:id>', methods=['POST'])
@login_required
def edit_user(id):
    if current_user.role != 'Admin': return redirect(url_for('main.settings'))
    user = User.query.get(id)
    if user:
        user.username = request.form.get('username')
        user.role = request.form.get('role')
        db.session.commit()
    return redirect(url_for('main.settings'))

@main.route('/user/password/<int:id>', methods=['POST'])
@login_required
def change_password(id):
    if current_user.role != 'Admin': return redirect(url_for('main.settings'))
    user = User.query.get(id)
    if user:
        user.set_password(request.form.get('new_password'))
        db.session.commit()
    return redirect(url_for('main.settings'))

@main.route('/add', methods=['POST'])
@login_required
def add_entry():
    if current_user.role == 'Viewer': return redirect(url_for('main.dashboard'))
    db.session.add(BillEntry(category_id=request.form.get('category'), cost=float(request.form.get('amount')), usage=float(request.form.get('usage') or 0), date=datetime.strptime(request.form.get('date'), '%Y-%m-%d')))
    db.session.commit()
    return redirect(url_for('main.dashboard'))

@main.route('/record/edit/<int:id>', methods=['POST'])
@login_required
def edit_entry(id):
    if current_user.role == 'Viewer': return redirect(url_for('main.records'))
    bill = BillEntry.query.get(id)
    if bill:
        bill.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d')
        bill.category_id = request.form.get('category')
        bill.cost = float(request.form.get('amount'))
        bill.usage = float(request.form.get('usage') or 0)
        db.session.commit()
    return redirect(url_for('main.records'))

@main.route('/record/delete/<int:id>')
@login_required
def delete_entry(id):
    if current_user.role == 'Viewer': return redirect(url_for('main.records'))
    bill = BillEntry.query.get(id)
    if bill:
        db.session.delete(bill)
        db.session.commit()
    return redirect(url_for('main.records'))