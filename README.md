## Setup Instructions

### Prerequisites
- Python 3.6.8 (IMPORTANT)

### Steps
```bash
git clone <repo-url>
cd Savor

py -3.6 -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
