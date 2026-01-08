# Data Engineering Portfolio

[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://www.postgresql.org/)
[![Python](https://img.shields.io/badge/Python-3.9+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Private-red.svg)]()
[![Code Style](https://img.shields.io/badge/code%20style-documented-brightgreen.svg)]()

Migration, standardization and consolidation of operational and administrative data  
**PostgreSQL • BigQuery • ETL • Python • RDBMS**

---

This repository contains the architecture, scripts and pipelines used in creating
a Data Warehouse for Financial Controllership. The goal is to integrate operational
data sources (BigQuery) and administrative sources (manual registrations), consolidating
everything into a standardized and reliable PostgreSQL environment to support financial
processes and incentive analysis.

---

## 📂 Projects

### [Financial ETL Framework](./financial-etl-framework/)

Complete ETL framework for financial Data Warehouse with modern architecture:
- 🏗️ **Medallion Architecture**: Raw → Staging → Mart layers
- 🔄 **Automated Pipelines**: Daily data ingestion and transformation
- 🧪 **Tested & Documented**: 95%+ test coverage with comprehensive docs
- 🐳 **Containerized**: Docker support with CI/CD pipelines
- 📊 **BigQuery Integration**: Operational data extraction

[➡️ View detailed documentation](./financial-etl-framework/README.md)

---

## 🎯 Project Objectives

- Centralize operational and administrative data in a single PostgreSQL server
- Ensure integrity, versioning and traceability in the data flow
- Automate daily ingestions from BigQuery and manual registrations
- Apply business rules (e.g.: BYD bonuses, billing status)
- Create structured layers (RAW → STG → MART) to simplify controllership consumption
- Support reports, monthly closings and internal KPIs

---

## 🏗️ Data Architecture

```text
BigQuery (daily billing)
        │
        ▼
RAW_BQ (raw mirror tables)
        │
        ├── Manual Registration (AppSheet / Sheets)
        ▼
RAW_REGISTRATION
        │
        ▼
STG (standardization, cleaning, normalization)
        │
        ▼
MART_CONTROLLING
        │
        ▼
Dashboards, reports and financial controls
```

---

## 📁 Repository Structure

```
.
├── financial-etl-framework/    # Main ETL project
│   ├── src/                    # Source code
│   ├── tests/                  # Automated tests
│   ├── schemas/                # SQL schemas
│   ├── .github/                # CI/CD pipelines
│   └── README.md               # Detailed documentation
├── controlling_postgreSQL/     # Legacy scripts
├── Datasets/                   # Sample data
└── README.md                   # This file
```

---

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/GSMuller/financial-etl-framework.git
   cd financial-etl-framework
   ```

2. **Install requirements** (Python 3.9+)
   ```bash
   cd financial-etl-framework
   pip install -e ".[dev]"
   ```

3. **Configure database access**
   - Copy `.env.example` to `.env`
   - Fill in your PostgreSQL credentials

4. **Run tests**
   ```bash
   pytest
   ```

For detailed instructions, see [financial-etl-framework/README.md](./financial-etl-framework/README.md)

---

## 🛠️ Technologies

- **Database**: PostgreSQL 13+, BigQuery
- **Language**: Python 3.9+
- **ETL**: pandas, psycopg2, sqlalchemy
- **Testing**: pytest, pytest-cov
- **DevOps**: Docker, GitHub Actions
- **Analytics**: Jupyter, matplotlib, seaborn

---

## 📊 Skills Demonstrated

### Data Engineering
- ✅ ETL pipeline design and implementation
- ✅ Data warehouse architecture (Medallion/Lakehouse)
- ✅ Data modeling and schema design
- ✅ SQL optimization and query tuning
- ✅ Data quality and validation

### Software Engineering
- ✅ Clean code and SOLID principles
- ✅ Test-driven development (TDD)
- ✅ CI/CD pipeline automation
- ✅ Containerization with Docker
- ✅ Version control with Git

### Database Management
- ✅ PostgreSQL administration
- ✅ Trigger and stored procedure development
- ✅ Performance optimization
- ✅ Backup and recovery strategies
- ✅ Database security best practices

---

## 🤝 Contributing

1. Fork the project
2. Create a feature branch: `git checkout -b feature/feature-name`
3. Commit your changes: `git commit -m 'feat: new feature'`
4. Push to your fork: `git push origin feature/feature-name`
5. Open a Pull Request

---

## 👤 Author

**Giovanni Muller**  
Data Engineer | ETL Specialist | Database Developer

- GitHub: [@GSMuller](https://github.com/GSMuller)
- LinkedIn: [Giovanni Muller](https://www.linkedin.com/in/giovanni-muller)

---

## 📄 License

This project is private and for internal use.

---

**⭐ If you find this work interesting, please consider giving it a star!**
