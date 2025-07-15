# Selenium Pytest Automation Framework

## 🚀 Overview

This project is a robust, extensible, and data-driven test automation framework built with **Selenium WebDriver**, **Pytest**, **Allure** (for detailed reporting), and **MySQL** for data-backed test execution. The framework supports:

- UI automation testing
- Data-driven testing (Excel & MySQL)
- Custom logging and failure debugging
- Allure report integration (with optional Docker support)
- `.env`-based environment configuration

---

## 📚 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
  - [Drivers](#drivers)
  - [Docker Setup (Optional)](#docker-setup-optional)
- [Configuration](#configuration)
- [Running Tests](#running-tests)
  - [Basic Run](#basic-run)
  - [With Markers](#with-markers)
  - [Browser Selection](#browser-selection)
  - [Allure Reporting](#allure-reporting)
  - [Allure CLI Installation](#allure-cli-installation)
- [Data-Driven Testing](#data-driven-testing)
  - [Using Excel](#using-excel)
  - [Using MySQL](#using-mysql)
- [Utilities](#utilities)
- [Logging](#logging)
- [Screenshots & Attachments](#screenshots--attachments)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [References](#references)

---

## ✅ Features

- Selenium WebDriver (UI automation)
- Pytest for structured test execution
- Data-driven testing with Excel and MySQL
- Allure report generation and attachment integration
- Dockerized DB testing (optional)
- Loguru-powered logging (with file + console support)
- Pytest fixtures in `conftest.py`
- Screenshot capture on failure
- Cross-browser testing (Chrome, Edge, Firefox)
- Modular configuration via `.env` and `config.yaml`

---

## 🧭 Project Structure

```
selenium_pytest/
│
├── .env                # Environment config
├── init.sql            # SQL script to setup DB schema
├── requirements.txt    # Python packages
├── pytest.ini          # Pytest options
│
├── config/
│   └── config.yaml     # Test configuration
│
├── data/
│   ├── excel_data.xlsx # Excel test cases
│   └── upload_files/   # Test file uploads
│
├── drivers/            # WebDrivers (Chrome/Edge)
│
├── pages/              # Page Object classes
│
├── tests/              # All test scripts
│   ├── test_*.py
│   └── data_driven_test/
│       ├── test_excel_data.py
│       └── test_sql_database.py
│
├── utils/              # Custom helpers
│   ├── browser_manager.py
│   ├── excel_reader.py
│   ├── logger.py
│   └── wait_helper.py
│
└── conftest.py         # Shared fixtures
```

---

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.10+
- Google Chrome / Edge browser
- MySQL server (local or remote)
- Allure CLI (see [Allure CLI Installation](#allure-cli-installation))

### Installation

```bash
git clone https://github.com/yourusername/selenium_pytest.git
cd selenium_pytest
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Environment Variables

Copy the sample and update with DB credentials:

```bash
cp .env.example .env
```

```dotenv
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_USER=root
DATABASE_PASSWORD=root
DATABASE_NAME=test_data
```

### Drivers

Download drivers:

- [ChromeDriver](https://chromedriver.chromium.org/downloads)
- [EdgeDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)

Place them in the `/drivers/` directory.

### Docker Setup (Optional)

To spin up a MySQL instance using Docker:

```bash
docker run --name test-mysql -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=test_data -p 3306:3306 -d mysql:latest
```

Run the `init.sql` script to create necessary tables:

```bash
mysql -h 127.0.0.1 -u root -p test_data < init.sql
```

---

## ⚙️ Configuration

Edit `config/config.yaml`:

```yaml
browser: chrome
headless: false
timeouts:
  implicit: 5
  explicit: 10
download_directory: downloads/
database:
  host: ${DATABASE_HOST}
  user: ${DATABASE_USER}
  password: ${DATABASE_PASSWORD}
  name: ${DATABASE_NAME}
```

---

## 🧪 Running Tests

### Basic Run

```bash
pytest
```

### With Markers

```bash
pytest -m smoke
pytest -m data_driven
```

### Browser Selection

```bash
pytest --browser=chrome
pytest --browser=firefox
```

### Allure Reporting

Generate results:

```bash
pytest --alluredir=allure-results
```

Serve report:

```bash
allure serve allure-results
```

Export to HTML:

```bash
allure generate allure-results --clean -o allure-report
```

### Allure CLI Installation

Install CLI:

```bash
brew install allure      # macOS
choco install allure     # Windows
scoop install allure
```

Or download from [Allure official site](https://docs.qameta.io/allure/#_installing_a_commandline).

---

## 📊 Data-Driven Testing

### Using Excel

- Format your Excel file: `Principal | RateOfInterest | Period | ...`
- Example file: `data/excel_data.xlsx`
- Test script: `test_excel_data.py`

### Using MySQL

- Setup DB using `init.sql`
- Insert rows into `fixed_deposits`
- Test script: `test_sql_database.py`
- Use:

```bash
pytest --init-db    # optional helper to initialize DB
```

---

## 🧩 Utilities

- `browser_manager.py`: Driver launch config
- `wait_helper.py`: Explicit wait wrapper
- `logger.py`: Console + file logger using Loguru
- `excel_reader.py`: Excel I/O via `openpyxl`
- `paths.py`: Centralized path resolution

---

## 📂 Logging

- Saved in `/logs/` folder
- Configured via `logger.py`
- Automatically attached to Allure reports

---

## 📸 Screenshots & Attachments

- Captured on test failure
- Also saves HTML source
- Auto-attached to Allure reports
- Manual screenshots: `driver.save_screenshot("image.png")`

---

## 🛠️ Troubleshooting

| Issue              | Solution                                         |
| ------------------ | ------------------------------------------------ |
| Driver not found   | Ensure it's in `drivers/` and matches browser    |
| Excel read error   | Validate sheet and headers                       |
| DB not connecting  | Check `.env` and DB availability                 |
| Allure not working | Ensure CLI is installed and `--alluredir` is set |

---

## 🤝 Contributing

1. Fork the repository
2. Create a new branch
3. Follow PEP8 and modular structure
4. Add your tests to `/tests/`
5. Submit a PR

---

## 📜 License

This project is licensed under the **MIT License**.

---

## 📚 References

- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [Pytest Docs](https://docs.pytest.org/en/latest/)
- [Allure Docs](https://docs.qameta.io/allure/)
- [Loguru](https://loguru.readthedocs.io/en/stable/)
- [MySQL Connector/Python](https://dev.mysql.com/doc/connector-python/en/)

---

## 📬 Contact

For support, open an issue or contact the maintainer via GitHub Discussions.

---

**Happy Testing! 🧪⚙️**
