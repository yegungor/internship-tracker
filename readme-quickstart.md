## Quick Start

### Prerequisites
- Python 3.8 or higher ([Download Python](https://www.python.org/downloads/))
- Git ([Download Git](https://git-scm.com/downloads))

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/yegungor/internship-tracker.git
cd internship-tracker
```

**2. Run the setup script**

Mac/Linux:
```bash
chmod +x setup.sh    # Make it executable (first time only)
./setup.sh
```

Windows:
```bash
setup.bat
```

**3. Start the app**

Mac/Linux:
```bash
./run.sh
```

Windows:
```bash
run.bat
```

**4. Open your browser**
```
http://127.0.0.1:1453
```

---

### Manual Setup (if scripts don't work)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate    # Mac/Linux
venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt

# Run the app
python3 app.py
```
