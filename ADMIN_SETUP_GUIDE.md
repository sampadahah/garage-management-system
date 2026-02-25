# Admin Panel Setup Guide - Garage Management System

## 🎯 What's Been Fixed

The white screen issue after admin login has been resolved. The admin panel now has:

1. ✅ Proper base template with navigation
2. ✅ Dashboard with statistics
3. ✅ Slot calendar with date picker
4. ✅ Add slot functionality
5. ✅ Automatic redirect for admin users after login

## 📁 Files Modified/Created

### Modified Files:
- `adminpanel/views.py` - Added dashboard view and improved slot views
- `adminpanel/urls.py` - Added dashboard route
- `customer/views.py` - Added admin redirect logic in login
- `adminpanel/templates/adminpanel/slot_calendar.html` - Updated template
- `adminpanel/templates/adminpanel/add_slot.html` - Updated template

### New Files:
- `adminpanel/templates/adminpanel/base.html` - New base template for admin panel
- `adminpanel/templates/adminpanel/dashboard.html` - Admin dashboard

## 🚀 Setup Instructions

### 1. Install PostgreSQL Driver (if not already installed)

```bash
pip install psycopg2-binary
```

Or if you're using a virtual environment:

```bash
# Activate your virtual environment first
.venv\Scripts\activate  # On Windows
source .venv/bin/activate  # On Linux/Mac

# Then install
pip install psycopg2-binary
```

### 2. Run Migrations

```bash
cd garage-management-system/GMS
python manage.py makemigrations
python manage.py migrate
```

### 3. Create a Superuser (Admin Account)

```bash
python manage.py createsuperuser
```

Follow the prompts:
- Email: your-email@example.com
- Name: Your Name
- Password: (enter a secure password)

### 4. Run the Development Server

```bash
python manage.py runserver
```

### 5. Access the Application

- **Login Page**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/booking/ (after login as admin)
- **Customer Dashboard**: http://127.0.0.1:8000/customer/dashboard/ (after login as customer)

## 🎨 Admin Panel Features

### Dashboard (`/booking/`)
- View total slots statistics
- See available vs booked slots
- Quick access to calendar and add slot

### Slot Calendar (`/booking/calendar/`)
- Date picker to select any date
- View all slots for selected date
- See slot status (Available/Booked)
- Color-coded status indicators

### Add Slot (`/booking/add-slot/`)
- Create new booking slots
- Set date, start time, and end time
- Mark as booked/available
- Automatic validation

## 🔐 User Roles

The system automatically redirects users based on their role:

- **Admin/Staff Users** → Admin Panel Dashboard (`/booking/`)
- **Regular Customers** → Customer Dashboard (`/customer/dashboard/`)

## 📊 Models Structure

### Slot Model
```python
- date: DateField
- start_time: TimeField
- end_time: TimeField
- is_booked: BooleanField (default=False)
- created_by: ForeignKey to User
- created_at: DateTimeField (auto)
```

## 🎯 How to Use

### As an Admin:

1. **Login** with your admin credentials
2. You'll be redirected to the **Admin Dashboard**
3. Click **"View Calendar"** to see slots by date
4. Click **"Add New Slot"** to create booking slots
5. Use the date picker to view slots for specific dates

### Creating Slots:

1. Go to "Add New Slot"
2. Select a date
3. Enter start time (e.g., 09:00)
4. Enter end time (e.g., 10:00)
5. Optionally mark as booked
6. Click "Create Slot"

## 🐛 Troubleshooting

### White Screen Issue
If you still see a white screen:
1. Clear your browser cache
2. Make sure you're logged in as an admin user (is_staff=True or is_superuser=True)
3. Check the URL - it should be `/booking/` not `/adminpanel/`

### Database Connection Error
If you see database errors:
```bash
pip install psycopg2-binary
```

### Template Not Found
Make sure your INSTALLED_APPS in settings.py includes:
```python
INSTALLED_APPS = [
    ...
    'adminpanel',
    'customer',
    'staff',
]
```

## 🎨 Customization

The admin panel uses a modern gradient design with:
- Purple gradient background
- Clean white cards
- Responsive layout
- Color-coded status indicators

You can customize colors in `adminpanel/templates/adminpanel/base.html`

## 📝 Next Steps

You can extend the admin panel with:
- Edit/Delete slot functionality
- Bulk slot creation
- Booking management
- Customer management
- Reports and analytics

## ✅ Testing Checklist

- [ ] Admin can login and see dashboard
- [ ] Dashboard shows correct statistics
- [ ] Calendar displays slots for selected date
- [ ] Can add new slots successfully
- [ ] Slots appear in calendar after creation
- [ ] Date picker works correctly
- [ ] Navigation between pages works
- [ ] Regular customers don't access admin panel

## 🔗 URL Structure

```
/                           → Login page
/customer/login/            → Customer login
/customer/signup/           → Customer signup
/customer/dashboard/        → Customer dashboard
/booking/                   → Admin dashboard
/booking/calendar/          → Slot calendar
/booking/add-slot/          → Add new slot
```

---

**Note**: This admin panel is separate from Django's built-in admin (`/admin/`). It's a custom interface designed specifically for garage slot management.
