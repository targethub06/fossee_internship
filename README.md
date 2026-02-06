# ChemVis - Equipment Parameter Visualizer

A comprehensive application for managing, analyzing, and visualizing chemical equipment parameters. ChemVis provides real-time data analytics with both web and desktop interfaces, featuring CSV data import, statistical analysis, and PDF report generation.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Starting the Backend](#starting-the-backend)
  - [Web Interface](#web-interface)
  - [Desktop Application](#desktop-application)
- [API Endpoints](#api-endpoints)
- [Database Models](#database-models)
- [CSV Data Format](#csv-data-format)

## Features

- **CSV Data Upload**: Upload equipment parameter data from CSV files
- **Data Validation**: Automatic validation of required data fields
- **Statistical Analysis**: Calculate and display summary statistics (mean flowrate, pressure, temperature)
- **Type Distribution**: Analyze equipment type distribution
- **PDF Report Generation**: Generate professional equipment summary reports
- **Upload History**: Track and manage up to 5 recent uploads
- **Dual Interface**: 
  - Web-based interface with modern UI
  - Desktop application using PyQt5
- **Authentication**: Secure login system for data protection
- **Data Visualization**: Charts and distribution graphs

## Project Structure

```
Foseee internship/
├── manage.py                          # Django management script
├── requirements.txt                   # Python dependencies
├── db.sqlite3                         # SQLite database
├── equipment_parameters.csv           # Sample equipment data
├── sample_equipment_data.csv          # Additional sample data
├── api/                               # Django API application
│   ├── models.py                     # Data models (EquipmentDataset, Equipment)
│   ├── views.py                      # API views and business logic
│   ├── serializers.py                # DRF serializers
│   ├── urls.py                       # API URL routes
│   ├── admin.py                      # Django admin configuration
│   └── migrations/                   # Database migrations
├── backend/                           # Django project configuration
│   ├── settings.py                   # Django settings
│   ├── urls.py                       # Main URL configuration
│   ├── wsgi.py                       # WSGI configuration
│   └── asgi.py                       # ASGI configuration
├── web/                               # Web frontend
│   ├── index.html                    # Main HTML interface
│   ├── app.js                        # Frontend JavaScript
│   └── style.css                     # Styling
└── desktop/                           # Desktop application
    └── main.py                       # PyQt5 desktop application
```

## Technology Stack

### Backend
- **Framework**: Django 3.x+ with Django REST Framework
- **Database**: SQLite
- **Data Processing**: Pandas
- **PDF Generation**: ReportLab
- **CORS**: django-cors-headers
- **HTTP**: Requests

### Frontend - Web
- **HTML5**, **CSS3**, **JavaScript**
- **Chart Library**: Chart.js
- **Authentication**: Token-based

### Frontend - Desktop
- **Framework**: PyQt5
- **Visualization**: Matplotlib
- **API Communication**: Requests

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone or download the project**
   ```bash
   cd "d:\Foseee internship"
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser** (for admin access)
   ```bash
   python manage.py createsuperuser
   ```

## Configuration

### Django Settings
Edit `backend/settings.py` to configure:
- Database connection
- CORS allowed origins
- Secret key
- Allowed hosts

### API Configuration
The API is configured to:
- Require authentication for all endpoints
- Automatically manage upload history (keeps 5 most recent uploads)
- Validate CSV structure before data insertion

## Usage

### Starting the Backend

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api`

### Web Interface

1. Open a web browser and navigate to `http://127.0.0.1:8000/` (or wherever the web files are served)
2. Login with your credentials
3. Upload a CSV file containing equipment data
4. View upload history and download PDF reports
5. Analyze equipment statistics and distributions

### Desktop Application

1. Ensure the Django backend is running
2. Run the desktop application:
   ```bash
   python desktop/main.py
   ```
3. Login with your credentials
4. Upload CSV files and view interactive visualizations
5. Analyze equipment type distribution in real-time

## API Endpoints

All endpoints require authentication. Base URL: `http://127.0.0.1:8000/api`

### Upload CSV Data
- **URL**: `/upload-csv/`
- **Method**: `POST`
- **Authentication**: Required
- **Parameters**:
  - `file`: CSV file upload
- **Response**: 201 Created with dataset details

### Get Upload History
- **URL**: `/history/`
- **Method**: `GET`
- **Authentication**: Required
- **Response**: List of last 5 uploaded datasets

### Generate PDF Report
- **URL**: `/reports/<dataset_id>/`
- **Method**: `GET`
- **Authentication**: Required
- **Response**: PDF file download

## Database Models

### EquipmentDataset
Represents a single CSV upload session
- `filename`: Name of the uploaded file
- `upload_date`: Timestamp of upload
- `summary_stats`: JSON field containing aggregated statistics

### Equipment
Individual equipment entries
- `dataset`: Foreign key to EquipmentDataset
- `name`: Equipment name
- `equipment_type`: Type of equipment
- `flowrate`: Flow rate measurement
- `pressure`: Pressure measurement
- `temperature`: Temperature measurement

## CSV Data Format

CSV files must contain the following columns:

| Column Name | Data Type | Description |
|------------|-----------|-------------|
| Equipment Name | String | Name of the equipment |
| Type | String | Equipment type/category |
| Flowrate | Float | Flow rate value |
| Pressure | Float | Pressure value |
| Temperature | Float | Temperature value |

### Example CSV
```csv
Equipment Name,Type,Flowrate,Pressure,Temperature
Pump A,Centrifugal,150.5,20.3,65.2
Compressor B,Rotary,200.0,15.8,72.1
Valve C,Gate,50.2,25.5,68.0
```

## Features in Detail

### Data Validation
- Validates all required columns are present
- Type-checks numeric fields
- Provides clear error messages

### Statistical Analysis
Automatically calculates:
- Total equipment count
- Average flowrate
- Average pressure
- Average temperature
- Equipment type distribution

### Upload Management
- Automatically maintains 5 most recent uploads
- Older uploads are deleted to save storage
- Full history available in the UI

### Report Generation
PDF reports include:
- Equipment dataset information
- Upload date and time
- Summary statistics
- Equipment type distribution

## License

This project is part of the Foseee internship program.

## Support

For issues or questions, please contact the development team.
