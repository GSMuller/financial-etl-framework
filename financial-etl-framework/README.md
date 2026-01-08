# Financial ETL Framework

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-336791.svg)](https://www.postgresql.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: Private](https://img.shields.io/badge/License-Private-red.svg)]()

> Robust ETL framework for financial Data Warehouse with PostgreSQL, focused on controllership and operational data analysis.

---

## 📋 Table of Contents

- [About The Project](#-about-the-project)
- [Architecture](#-architecture)
- [Features](#-features)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Testing](#-testing)
- [Contributing](#-contributing)

---

## 🎯 About The Project

The **Financial ETL Framework** is a complete solution for consolidating financial and operational data into a PostgreSQL Data Warehouse. Designed to support controllership processes, the framework integrates data from multiple sources (BigQuery, spreadsheets, internal systems) applying transformations, validations, and business rules.

### Problem Solved

Centralize and standardize fragmented financial data across different systems, ensuring:
- ✅ Data integrity and traceability
- ✅ Automated daily ingestions
- ✅ Consistent business rule application
- ✅ Support for management reports and analysis

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      DATA SOURCES                            │
├─────────────────┬──────────────────┬────────────────────────┤
│   BigQuery      │  AppSheet/       │   Internal             │
│  (Operational)  │  Google Sheets   │   Systems              │
└────────┬────────┴────────┬─────────┴───────────┬────────────┘
         │                 │                     │
         ▼                 ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    RAW LAYER (Bronze)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  raw_bq      │  │raw_cadastro  │  │  raw_manual  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────────┬────────────────────────────────┘
                             │ ETL Pipeline
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                   STAGING LAYER (Silver)                     │
│        Cleaning • Normalization • Standardization            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  stg_billing   │  stg_registration  │  stg_bonus    │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────┘
                             │ Business Rules
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                   MART LAYER (Gold)                          │
│         Analytical Views • Aggregations • KPIs               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  mart_controlling  │  mart_incentives  │  metrics    │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  BI Dashboards  │
                    │    Reports      │
                    └─────────────────┘
```

### Data Pipeline

1. **Extraction**: Data collection from BigQuery, spreadsheets, and systems
2. **Loading (Raw)**: Raw storage without transformations
3. **Staging**: Cleaning, validation, and normalization
4. **Transformation**: Business rules application (triggers, functions)
5. **Mart**: Analytical layer optimized for consumption

---

## ✨ Features

### Core Features
- 🔄 **Automated ETL**: Complete Extract-Transform-Load pipeline
- 🗃️ **Layered Architecture**: Raw → Staging → Mart (Medallion)
- 🔐 **Security**: Credentials via environment variables (.env)
- 📊 **BigQuery Integration**: Daily operational data ingestion
- 🧪 **Automated Testing**: Coverage with pytest
- 📝 **Complete Logging**: Tracking of all operations

### Specific Functionalities
- 💰 Automatic BYD bonus calculation
- 🔄 Trigger system for data propagation
- 📈 Materialized views for performance
- 🎯 Referential integrity validation
- 📅 Data versioning control

---

## 🚀 Installation

### Prerequisites

- Python 3.9 or higher
- PostgreSQL 13 or higher
- Git

### Steps

1. **Clone the repository**
```bash
git clone https://github.com/GSMuller/financial-etl-framework.git
cd financial-etl-framework
```

2. **Create a virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
# Basic installation
pip install -e .

# With development tools
pip install -e ".[dev]"

# With notebook support
pip install -e ".[notebooks]"

# Complete installation
pip install -e ".[dev,notebooks,excel]"
```

4. **Configure environment variables**

Create a `.env` file in the project root:
```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=financial_dw
DB_USER=your_username
DB_PASSWORD=your_password

# BigQuery (optional)
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
BQ_PROJECT_ID=your-project
BQ_DATASET=your_dataset
```

5. **Run database migrations**
```bash
# Create schemas
psql -h localhost -U your_user -d financial_dw -f schemas/byd/tables/create/create_all.sql

# Create triggers
psql -h localhost -U your_user -d financial_dw -f schemas/byd/triggers/install_triggers.sql
```

---

## 💻 Usage

### Basic Example

```python
from financial_etl import get_connection, db_connection

# Using context manager (recommended)
with db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mart_controlling.bonus_summary")
    results = cursor.fetchall()
    
    for row in results:
        print(row)
```

### Run Complete ETL

```python
from financial_etl.pipelines import run_daily_etl

# Execute the complete pipeline
result = run_daily_etl(date='2026-01-08')
print(f"Pipeline executed: {result['status']}")
print(f"Records processed: {result['records_processed']}")
```

### Transaction Rollback

```bash
python src/financial_etl/rollback.py
```

### Run Tests

```bash
# All tests
pytest

# With coverage report
pytest --cov=financial_etl --cov-report=html

# Specific test
pytest tests/test_conn.py -v
```

---

## 📁 Project Structure

```
financial-etl-framework/
├── src/
│   └── financial_etl/          # Main source code
│       ├── __init__.py
│       ├── config.py           # Configuration and logging
│       ├── conn.py             # Connection management
│       └── rollback.py         # Rollback utility
├── tests/                      # Automated tests
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_conn.py
│   └── test_rollback.py
├── schemas/                    # SQL schemas
│   ├── byd/
│   │   ├── tables/
│   │   │   ├── create/        # Creation scripts
│   │   │   ├── alter/         # Schema alterations
│   │   │   ├── insert/        # Insertion scripts
│   │   │   └── view&conults/  # Views and queries
│   │   └── triggers/          # Triggers and PL/pgSQL functions
│   └── nd/
├── Datasets/                   # Sample data (not versioned)
├── controlling_postgreSQL/     # Legacy scripts
├── docs/                       # Additional documentation
├── .github/
│   └── workflows/              # CI/CD GitHub Actions
├── .gitignore
├── pyproject.toml              # Project configuration
├── requirements.txt            # Dependencies (legacy)
├── pytest.ini                  # Pytest configuration
├── Dockerfile                  # Docker container
├── .env.example                # Environment variables template
├── CHANGELOG.md                # Change history
└── README.md                   # This file
```

---

## 🧪 Testing

The project uses **pytest** with code coverage:

```bash
# Run all tests
pytest

# With verbose output
pytest -v

# Generate HTML coverage report
pytest --cov=financial_etl --cov-report=html

# Open report in browser
# File will be at htmlcov/index.html
```

### Current Coverage

- `config.py`: 95%
- `conn.py`: 98%
- `rollback.py`: 92%

---

## 🐳 Docker

### Build Image

```bash
docker build -t financial-etl-framework .
```

### Run Container

```bash
docker run -d \
  --name financial-etl \
  -e DB_HOST=host.docker.internal \
  -e DB_NAME=financial_dw \
  -e DB_USER=username \
  -e DB_PASSWORD=password \
  financial-etl-framework
```

---

## 📊 Project Metrics

- **Language**: Python 58.1%
- **SQL**: 5.7%
- **Jupyter Notebooks**: 36.2%
- **Test Coverage**: ~95%
- **Lines of Code**: ~5,000+

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style

The project uses:
- **black** for code formatting
- **isort** for import organization
- **flake8** for linting
- **mypy** for type checking

```bash
# Format code
black src/ tests/

# Organize imports
isort src/ tests/

# Quality check
flake8 src/ tests/
```

---

## 📄 License

Private project - All rights reserved.

---

## 👤 Author

**Giovanni Muller**

- GitHub: [@GSMuller](https://github.com/GSMuller)
- LinkedIn: [Giovanni Muller](https://www.linkedin.com/in/giovanni-muller)

---

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete version history.

---

## 🙏 Acknowledgments

- Servopa Controllership Team
- PostgreSQL Community
- Open-source contributors

---

**⭐ If this project was helpful, please consider giving it a star!**
