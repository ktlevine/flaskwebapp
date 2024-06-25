from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, send_file
from flask_login import login_required, current_user
from .models import Bike
from datetime import datetime, timezone
from . import db
import json
import pandas as pd
from io import BytesIO

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        bike_number = request.form.get('bike_number')
        bike_type = request.form.get('bike_type')
        bike_location = request.form.get('bike_location')
        needs_maintenance = request.form.get('needs_maintenance') == 'on'

        existing_bike = Bike.query.filter_by(number=bike_number).order_by(Bike.id.desc()).first()
        if existing_bike:
            db.session.delete(existing_bike)
            db.session.commit()

        new_bike = Bike(
            number=bike_number,
            type=bike_type,
            location=bike_location,
            needs_maintenance=needs_maintenance,
            user_id=current_user.id
        )
        try:
            db.session.add(new_bike)
            db.session.commit()
            flash('Bike entry added!', category='success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding bike entry: {str(e)}', category='error')
        return redirect(url_for('views.home'))

    bikes = Bike.query.filter_by(user_id=current_user.id).all()  # Fetch only the current user's bikes
    return render_template("home.html", user=current_user, bikes=bikes)

@views.route('/inventory')
@login_required
def inventory():
    bikes = Bike.query.filter_by().all()  # Fetch only the current user's bikes
    current_date = datetime.now(timezone.utc).date()
    return render_template("inventory.html", user=current_user, bikes=bikes)

@views.route('/info')
@login_required
def info():
    bikes = Bike.query.filter_by(Bike.out_of_commission == False).all()
    current_date = datetime.now(timezone.utc).date()
    
    location_summary = {}
    for bike in bikes:
        location = bike.location
        if location not in location_summary:
            location_summary[location] = {'total': 0, 'types': {}, 'entered_today': 0, 'not_entered_today': 0}
        
        location_summary[location]['total'] += 1
        bike_type = bike.type
        if bike_type not in location_summary[location]['types']:
            location_summary[location]['types'][bike_type] = 0
        location_summary[location]['types'][bike_type] += 1

        if bike.date_entered.date() == current_date:
            location_summary[location]['entered_today'] += 1
        else:
            location_summary[location]['not_entered_today'] += 1
    
    return render_template("info.html", location_summary=location_summary)

@views.route('/delete-bike', methods=['POST'])
@login_required
def delete_bike():
    bike_data = json.loads(request.data)
    bike_id = bike_data.get('bikeId')
    bike = Bike.query.get(bike_id)
    if bike:
        try:
            db.session.delete(bike)
            db.session.commit()
            return jsonify({}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Error deleting bike: {str(e)}'}), 500
    return jsonify({'error': 'Bike not found or not authorized'}), 404

@views.route('/mark-out-of-commission', methods=['POST'])
@login_required
def mark_out_of_commission():
    bike_data = json.loads(request.data)
    bike_id = bike_data.get('bikeId')
    bike = Bike.query.get(bike_id)
    if bike:
        try:
            bike.out_of_commission = True
            db.session.commit()
            return jsonify({}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Error updating bike: {str(e)}'}), 500
    return jsonify({'error': 'Bike not found or not authorized'}), 404

@views.route('/export')
@login_required
def export():
    # Fetch the data from the database
    bikes = Bike.query.filter_by(user_id=current_user.id).all()

    # Prepare the data for export
    data = []
    for bike in bikes:
        data.append({
            'Number': bike.number,
            'Type': bike.type,
            'Location': bike.location,
            'Needs Maintenance': 'Yes' if bike.needs_maintenance else 'No',
            'Out of Commission': 'Yes' if bike.out_of_commission else 'No'
        })

    # Create a DataFrame
    df = pd.DataFrame(data)

    # Convert DataFrame to an Excel file
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Bikes')

    output.seek(0)

    # Send the file as a response
    return send_file(output, download_name="bikes.xlsx", as_attachment=True)
