# 💳 Credit Approval System

A backend-only Django-based system that automates credit/loan approval using a customer's financial and historical loan data. The system checks loan eligibility, calculates credit score, and approves or rejects loans intelligently. All operations are managed via REST APIs, with background tasks handling data ingestion.

---

## 🚀 Features

- 📝 **Customer Registration**: Register new customers with auto-calculated credit limits.
- 📊 **Credit Scoring**: Assigns credit score based on past loan performance and current debt.
- ✅ **Loan Eligibility Check**: Determines loan approval status with interest correction logic.
- 🧾 **Loan Processing**: Processes loan creation with EMI calculation using compound interest.
- 🔍 **Loan Viewing**:
  - View individual loan details with customer info.
  - View all current loans of a customer.
- ⚙️ **Background Tasks**: Automatically ingest historical customer and loan data from Excel files using Celery workers.

---

## 🛠️ Tech Stack

| Tool/Tech             | Purpose                         |
|----------------------|---------------------------------|
| Python, Django        | Backend Framework               |
| Django REST Framework | API Development                 |
| PostgreSQL            | Relational Database             |
| Docker + Docker Compose | Containerization             |
| Celery + Redis        | Background Task Management      |
| Pandas & openpyxl     | Excel Data Parsing              |

---

## 📌 Assumptions

- EMI calculation uses **Compound Interest**:
- **Credit Score Logic** factors:
- Timely EMI repayments
- Number of past loans
- Total loan volume
- Existing debt
- Loans taken in the current year

- **Auto-Rejection Criteria**:
- Credit score < 10
- EMI exceeds 50% of monthly income
- Total debt exceeds approved limit

---

## ⚙️ Background Task Logic (Celery)

- On project startup, Celery triggers ingestion of data from Excel files (`customer_data.xlsx`, `loan_data.xlsx`)
- Files are parsed using `pandas` and `openpyxl`
- Records are inserted into PostgreSQL
- Redis is used as the message broker
- Celery worker runs in a separate Docker container via `docker-compose`

---

## 📬 Submission

✅ Dockerized setup using `docker-compose up`  
✅ All API endpoints tested successfully  
✅ Celery-based background ingestion implemented  
✅ Codebase committed to GitHub

---

## 🤝 Contact

For any queries or collaboration:

- **Name**: Yuvraj Shete  
- **Email**: yuvrajshete612@gmail.com  
- **GitHub**: https://github.com/yuvrajshete05/credit-approval-system.git
