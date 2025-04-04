# 📄 Invoice Parser with Gemini AI

![App Screenshot](screenshot.png) <!-- Add your screenshot here -->

## 🚀 Features
- **AI-Powered Parsing**: Uses Gemini to extract structured data from invoice images
- **Multi-Format Support**: Works with JPG, JPEG, and PNG files
- **Organized Views**:
  - 📋 Invoices tab - Main invoice details
  - 🛒 Items tab - All line items with quantities and prices
  - 👤 Customers tab - Extracted customer information

## ⚙️ Setup
1. **Setup Virtual Environment**:
```bash
python -m venv venv
```

2. **Activate**:
```
venv/scripts/activate
```

3. **Install dependencies**
```
pip install -r requirements.txt
```

3. **Configuration**
Create .env file:
```
GEMINI_API_KEY=your_api_key_here
```

## Running the app
```
streamlit run main.py
```

## 🖥️ Usage
Upload one or more invoice images
Click "Parse Invoices" button
Switch between tabs to view different data sections

## 📁 Project Structure
```
invoice-parser/
├── app.py            # Main application code
├── .env              # Environment variables
├── requirements.txt  # Dependencies
└── README.md         # This file
```
