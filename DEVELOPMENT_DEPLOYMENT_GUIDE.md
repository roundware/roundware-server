# Roundware Server Development & Deployment Guide

This guide covers the complete workflow for developing and deploying Roundware Server with Django 4.2 LTS, including local development in containers and production deployment on Digital Ocean.

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Production Server Setup](#production-server-setup)
3. [Testing](#testing)
4. [Deployment Process](#deployment-process)
5. [Troubleshooting](#troubleshooting)

---

## Development Environment Setup

### Prerequisites

- **Docker** and **Docker Compose** installed
- **Visual Studio Code** with the Dev Containers extension
- **Git** configured with your credentials

### Getting Started with Dev Containers

1. **Clone the repository:**
   ```bash
   git clone https://github.com/roundware/roundware-server.git
   cd roundware-server
   ```

2. **Open in VS Code:**
   ```bash
   code .
   ```

3. **Start the dev container:**
   - VS Code will detect the `.devcontainer` configuration
   - Click "Reopen in Container" when prompted
   - Or use Command Palette: `Dev Containers: Reopen in Container`

4. **The dev container will automatically:**
   - Install Python 3.11.13
   - Set up PostgreSQL database
   - Install all dependencies from `requirements/common.txt`
   - Configure Django settings for development

### Development Environment Details

- **Python Version:** 3.11.13
- **Django Version:** 4.2.23 LTS (supported until April 2026)
- **Database:** PostgreSQL (containerized)
- **Settings Module:** `roundware.settings.dev`
- **Virtual Environment:** Pre-configured in container

### Running the Development Server

```bash
# Inside the dev container terminal
cd /code
python roundware/manage.py runserver 0.0.0.0:8000
```

The server will be accessible at `http://localhost:8000`

### Running Tests in Development

```bash
# Run all tests
python run_tests.py

# Run tests with coverage report
python run_tests.py -c

# Run specific test file
python run_tests.py roundware/api2/tests/test_views.py

# Run with pytest directly (alternative)
pytest roundware/api2/tests/ -v
```

**Expected Result:** 270 tests should pass successfully.

### Making Code Changes

1. **Edit code** in VS Code (changes are live-mounted)
2. **Run tests** to ensure changes work
3. **Commit changes:**
   ```bash
   git add .
   git commit -m "Your commit message"
   git push origin develop
   ```

---

## Production Server Setup

### Server Requirements

- **Ubuntu 24.04 LTS** (Noble Numbat)
- **Python 3.11+** (3.11.13 recommended)
- **PostgreSQL 12+**
- **Apache 2.4+** with mod_wsgi
- **Minimum 2GB RAM, 2 CPU cores**

### Initial Server Setup

1. **Update the server:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install Python 3.11:**
   ```bash
   sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
   ```

3. **Clone the repository:**
   ```bash
   cd ~
   git clone https://github.com/roundware/roundware-server.git
   cd roundware-server
   ```

4. **Run the installation script:**
   ```bash
   sudo ./install.sh
   ```

   This script will:
   - Install system dependencies (PostgreSQL, Apache, etc.)
   - Create the `roundware` user
   - Set up the virtual environment at `/var/www/roundware-venv`
   - Configure Apache with mod_wsgi
   - Set up the database
   - Deploy the application code to `/var/www/roundware/source`

### Post-Installation Configuration

1. **Configure production settings:**
   ```bash
   sudo nano /var/www/roundware/settings/roundware_production.py
   ```

   Essential settings to configure:
   ```python
   # Database settings (if different from defaults)
   DATABASES = {
       'default': {
           'ENGINE': 'django.contrib.gis.db.backends.postgis',
           'NAME': 'roundware',
           'USER': 'roundware',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '',
       }
   }

   # Email settings for notifications
   EMAIL_HOST = 'smtp.your-provider.com'
   EMAIL_HOST_USER = 'your-email@domain.com'
   EMAIL_HOST_PASSWORD = 'your-password'
   EMAIL_PORT = 587
   EMAIL_USE_TLS = True

   # Security settings
   SECRET_KEY = 'your-secret-key'
   DEBUG = False
   ALLOWED_HOSTS = ['your-domain.com', 'your-ip-address']
   ```

2. **Test the installation:**
   ```bash
   curl http://localhost/api/2/
   ```

   Should return JSON API response.

### Running Tests on Production Server

```bash
# Navigate to your git repository (NOT the deployed code)
cd ~/roundware-server

# Run tests using the production virtual environment
/var/www/roundware-venv/bin/python run_tests.py

# Run with coverage
/var/www/roundware-venv/bin/python run_tests.py -c
```

**Important:** Always run tests from your git repository directory (`~/roundware-server`), not from the deployed code directory (`/var/www/roundware/source`).

---

## Deployment Process

### Understanding the Deployment Structure

- **Git Repository:** `~/roundware-server` (where you develop and test)
- **Deployed Code:** `/var/www/roundware/source` (what Apache serves)
- **Virtual Environment:** `/var/www/roundware-venv` (Python packages)
- **Production Settings:** `/var/www/roundware/settings/roundware_production.py`

### Deploying Updates

1. **Update your code:**
   ```bash
   cd ~/roundware-server
   git pull origin develop
   ```

2. **Run tests to ensure everything works:**
   ```bash
   /var/www/roundware-venv/bin/python run_tests.py
   ```

3. **Deploy the changes:**
   ```bash
   sudo ./deploy.sh
   ```

   The deploy script will:
   - Copy code from your git repo to `/var/www/roundware/source`
   - Install any new Python dependencies
   - Run database migrations
   - Collect static files
   - Restart Apache
   - Display "Deploy Complete" when finished

### Deploy Script Details

The `deploy.sh` script performs these actions:

1. **Code Deployment:**
   - Syncs code from git repository to web directory
   - Preserves production settings and media files
   - Sets proper ownership and permissions

2. **Dependency Management:**
   - Installs packages from `requirements/common.txt`
   - Uses Python 3.11 and the production virtual environment

3. **Database Operations:**
   - Runs Django migrations automatically
   - No manual database steps required

4. **Web Server:**
   - Collects static files for Apache
   - Restarts Apache to load new code
   - Validates deployment success

### Emergency Rollback

If deployment fails:

1. **Check Apache logs:**
   ```bash
   sudo tail -f /var/log/apache2/error.log
   ```

2. **Check Roundware logs:**
   ```bash
   sudo tail -f /var/log/roundware/
   ```

3. **Restart services:**
   ```bash
   sudo systemctl restart apache2
   sudo systemctl restart postgresql
   ```

---

## Testing

### Test Types

1. **Unit Tests:** Test individual functions and methods
2. **Integration Tests:** Test API endpoints and database interactions
3. **Functional Tests:** Test complete user workflows

### Running Different Test Suites

```bash
# All tests (recommended for deployment verification)
python run_tests.py

# Specific test modules
python run_tests.py roundware/api2/tests/test_views.py
python run_tests.py roundware/api2/tests/test_serializers.py
python run_tests.py roundware/rw/tests/test_models.py

# With coverage report (generates htmlcov/ directory)
python run_tests.py -c

# Verbose output
pytest roundware/api2/tests/ -v
```

### Test Environment Configuration

Tests use the `roundware.settings.testing` configuration:
- Separate test database (automatically created/destroyed)
- Faster test execution with `--nomigrations --reuse-db`
- Memory-based SQLite for speed (when possible)

### Expected Test Results

- **Total Tests:** 270
- **Expected Result:** All tests should pass
- **Warnings:** Some deprecation warnings are expected and not critical
- **Time:** Tests typically complete in 30-60 seconds

---

## Troubleshooting

### Common Development Issues

**Container won't start:**
```bash
# Rebuild the container
docker-compose down
docker-compose build --no-cache
docker-compose up
```

**Database connection errors:**
```bash
# Restart PostgreSQL in container
sudo service postgresql restart
```

**Permission errors in tests:**
```bash
# Fix ownership in container
sudo chown -R vscode:vscode /code
```

### Common Production Issues

**"Deploy Complete" not showing:**
- Check Apache error logs: `sudo tail -f /var/log/apache2/error.log`
- Verify virtual environment: `ls -la /var/www/roundware-venv/bin/`
- Check permissions: `ls -la /var/www/roundware/`

**Import errors after deployment:**
```bash
# Reinstall packages
sudo -u roundware /var/www/roundware-venv/bin/pip install -r ~/roundware-server/requirements/common.txt

# Restart Apache
sudo systemctl restart apache2
```

**Database migration errors:**
```bash
# Run migrations manually
sudo -u roundware /var/www/roundware-venv/bin/python /var/www/roundware/source/roundware/manage.py migrate
```

**Tests fail with "settings not configured":**
- Make sure you're running tests from `~/roundware-server`, not `/var/www/roundware/source`
- Verify `pyproject.toml` has the pytest configuration section

### Virtual Environment Issues

**Recreating the virtual environment:**
```bash
# Remove old environment
sudo rm -rf /var/www/roundware-venv

# Create new environment
sudo python3.11 -m venv /var/www/roundware-venv

# Set ownership
sudo chown -R roundware:roundware /var/www/roundware-venv

# Install packages
sudo -u roundware /var/www/roundware-venv/bin/pip install -r ~/roundware-server/requirements/common.txt

# Deploy again
cd ~/roundware-server
sudo ./deploy.sh
```

### Log Locations

- **Apache Access:** `/var/log/apache2/access.log`
- **Apache Errors:** `/var/log/apache2/error.log`
- **Roundware Logs:** `/var/log/roundware/`
- **Django Debug:** Check `DEBUG = True` in development settings

### Getting Help

1. **Check logs first** (Apache and Roundware)
2. **Run tests** to verify functionality
3. **Compare with working dev container** environment
4. **Check Django 4.2 compatibility** for any custom code

---

## Key Changes from Previous Versions

### Django Upgrade (3.0 → 4.2 LTS)

- **Security:** Fixed 29 vulnerabilities (2 critical, 11 high, 13 moderate, 3 low)
- **Dependencies:** Updated all packages to latest compatible versions
- **Code Changes:** Fixed deprecated imports and functions
- **Testing:** Updated test framework compatibility

### New Deployment Structure

- **Virtual Environment:** Now located at `/var/www/roundware-venv` (outside git)
- **Python Version:** Upgraded to Python 3.11.13
- **Requirements:** Separated into `requirements/common.txt` and `requirements/dev.txt`
- **Testing:** Added pytest configuration in `pyproject.toml`

### Development Environment

- **Containerization:** Full dev container support with VS Code
- **Database:** PostgreSQL in container for development
- **Testing:** Streamlined test execution with proper Django settings
- **Dependencies:** Automatic installation and configuration

This guide ensures consistent development and deployment practices while maintaining production stability with Django 4.2 LTS support through April 2026. 