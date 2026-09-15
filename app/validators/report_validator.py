from datetime import datetime

def validate_registration_data(data):
    errors = []
    if not data.get('name') or len(data['name'].strip()) < 2:
        errors.append("Full Name must be at least 2 characters long.")
    if not data.get('email') or '@' not in data['email']:
        errors.append("A valid email address is required.")
    if not data.get('mobile_number') or len(data['mobile_number'].strip()) < 10:
        errors.append("A valid 10-digit mobile number is required.")
    if not data.get('password') or len(data['password']) < 6:
        errors.append("Password must be at least 6 characters long.")
    role = data.get('role', 'STUDENT')
    if role not in ['STUDENT', 'STAFF', 'ADMIN']:
        errors.append("Invalid user role selected.")
    return errors

def validate_report_data(data, is_lost=True):
    errors = []
    if not data.get('item_name') or len(data['item_name'].strip()) < 2:
        errors.append("Item Name is required.")
    if not data.get('category_id'):
        errors.append("Category selection is required.")
    if not data.get('description') or len(data['description'].strip()) < 5:
        errors.append("Detailed description is required (at least 5 characters).")
    if not data.get('location') or len(data['location'].strip()) < 2:
        errors.append("Location is required.")
    
    date_str = data.get('date')
    if not date_str:
        errors.append("Date is required.")
    else:
        try:
            parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            if parsed_date > datetime.utcnow().date():
                errors.append("Report date cannot be in the future.")
        except ValueError:
            errors.append("Invalid date format. Use YYYY-MM-DD.")
            
    return errors
