# 🏠 HomeBills

> **A modern, self-hosted home expense tracker featuring interactive dashboards, multi-user roles, and dark mode.**

[![Docker Pulls](https://img.shields.io/docker/pulls/20ervin/homebills)](https://hub.docker.com/r/20ervin/homebills)
[![GitHub Repo](https://img.shields.io/badge/github-Dr20Ervin%2Fhomebills-black?logo=github)](https://github.com/Dr20Ervin/homebills)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-docker-blue)](https://www.docker.com/)

**HomeBills** is a lightweight, secure, and containerized application designed to help you track household expenses effortlessly. Whether you want to monitor your electricity usage, track rent payments, or visualize your monthly spending habits, HomeBills provides a clean and intuitive interface to get the job done.

---

## ✨ Features

* **📊 Interactive Dashboard:** Visualize spending trends with dynamic bar and pie charts.
* **🌙 Dark Mode Support:** Seamlessly switch between Light and Dark themes.
* **🔐 Role-Based Access:**
  * **Admin:** Full control over settings, users, and categories.
  * **Editor:** Can add and edit bill records.
  * **Viewer:** Read-only access to dashboards.
* **⚡ Smart Calculator:** Auto-calculates total costs based on unit usage (e.g., `kWh price * usage`).
* **🚀 Setup Wizard:** A user-friendly setup screen to create your Admin account and customize categories on the first run.
* **💾 Database Agnostic:** Supports both **SQLite** (default) and **PostgreSQL** for scalable deployments.
* **🐳 Docker Ready:** Easy deployment with a single `docker-compose.yml` file.

---

## 📸 Screenshots

| **Dashboard (Dark Mode)** | **Expense Records** |
|:---:|:---:|
| ![Dashboard](https://i.imgur.com/zmpL3Ft.png) <br> *Monitor your spending trends at a glance.* | ![Records](https://i.imgur.com/lnnDWkB.png) <br> *View and manage monthly bills.* |

| **Settings & Users** | **Setup Wizard** |
|:---:|:---:|
| ![Settings](https://i.imgur.com/bU2Nodf.png) <br> *Manage users, roles, and categories.* | ![Setup](https://i.imgur.com/h0q7mxz.png) <br> *Easy initial configuration.* |

---

## 🚀 Quick Start

The easiest way to run **HomeBills** is using Docker Compose.

### 1. Create a `docker-compose.yml` file
Copy the following content into a file named `docker-compose.yml`. You can configure your security key and settings directly in the `environment` section.

```yaml
version: '3.8'

services:
  web:
    image: 20ervin/homebills:latest
    container_name: homebills_app
    ports:
      - "5020:5020"
    volumes:
      - ./config_data:/config
    environment:
      - SECRET_KEY=change-me-to-something-secure-and-random
      - DATABASE=SQLite
    restart: unless-stopped

```

### 2. Run the Container

Start the application:

```bash
docker-compose up -d

```

### 3. First Run Setup

1. Open your browser and navigate to `http://localhost:5020`.
2. You will be greeted by the **Setup Wizard**.
3. Create your **Admin** account and set up your initial **Expense Categories**.
4. Log in and start tracking!

---

## 🐘 Using PostgreSQL (Optional)

For a more robust setup, you can connect HomeBills to a PostgreSQL database by simply updating your `docker-compose.yml` to include the database service and the correct environment variables.

### Update `docker-compose.yml`

```yaml
version: '3.8'

services:
  web:
    image: 20ervin/homebills:latest
    container_name: homebills_app
    ports:
      - "5020:5020"
    volumes:
      - ./config_data:/config
    depends_on:
      - db
    environment:
      - SECRET_KEY=change-me-to-something-secure
      - DATABASE=psql
      - PSQL_USER=hb_user
      - PSQL_PASSWORD=secure_password
      - PSQL_HOST=db
      - PSQL_DB=homebills_db
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    container_name: homebills_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: hb_user
      POSTGRES_PASSWORD: secure_password
      POSTGRES_DB: homebills_db
    restart: unless-stopped

volumes:
  postgres_data:

```
