# Create virtual environment
echo Creating virtual environment...
python3 -m venv venv

# Install requirements
echo Installing requirements...
./venv/bin/pip install -r requirements.txt --require-virtualenv