# Avebel-Connecter

**Avebel-Connecter** is a modern, lightweight, and feature-rich GUI-based database manager built in Python using Tkinter. It allows you to connect to PostgreSQL databases, browse schemas, manage tables and databases, run queries, and export data — all without touching the command line.

> Future versions may support MySQL and other relational databases.

---

## 🔧 Features

### 🔗 Connect to PostgreSQL
- Easily connect to a PostgreSQL database using a full connection URL (`postgres://...`).
- Shows connection status and live metadata:
  - PostgreSQL version
  - Active database
  - Connected user
  - Table count in `public` schema

![Connection Tab](screenshots/1.png)

---

### 🗂️ Schema & Table Browser
- Tree-view for browsing schemas and their tables.
- Double-click a table to preview up to 1000 rows of data.
- Automatically shows column names and types even if the table is empty.

![Browser Tab](screenshots/2.png)

---

### 🔍 Query Executor
- Write and run raw SQL queries.
- Displays formatted results with row counts.
- Supports all SQL: `SELECT`, `INSERT`, `UPDATE`, `DELETE`, DDL, etc.

![Query Tab](screenshots/3.png)

---

### 🏗️ Schema Editor (DDL)
- Execute multiple DDL commands or schema definitions from a text area.
- Load SQL from file or save your current script.
- Quickly deploy table structures or indexes.

![Schema Tab](screenshots/4.png)

---

### 🗄️ Database Management
- Create new databases on the connected PostgreSQL server.
- List existing user-created databases.
- Drop databases with confirmation.

![Database Tab](screenshots/5.png)

---

### 📋 Table Management
- Create new tables with multi-line column definitions.
- View, edit, or delete existing rows.
- Drop tables safely with visual confirmation.
- Add/edit records through a form-based UI (with null handling).

![Table Tab](screenshots/6.png)

---

### 💾 Data Export
- Export selected table’s data into:
  - `.csv` (comma-separated values)
  - `.json` (structured format)
- Supports exporting large tables and nested records.

---

## 🖥️ How to Use

### Option 1: Run the EXE (Windows)
1. Download `Avebel-Connecter.exe` from the [Releases](#) section (built using PyInstaller).
2. Run it — no Python or installation required.

### Option 2: Run from Source (Python 3.7+)
```bash
pip install -r requirements.txt
python main.py
````

> Requires `psycopg2` and `tkinter` (standard in most Python installations).

---

## 📦 Building Your Own EXE

If you want to customize or rebuild:

### Step 1: Install Requirements

```bash
pip install pyinstaller psycopg2
```

### Step 2: Run Build Command

```bash
pyinstaller --onefile --windowed --icon=avebel.ico --name="Avebel-Connecter" main.py
```

### Step 3: Locate Executable

* Your `.exe` will be inside the `dist/` folder.
* Distribute or pin it to your desktop for easy launch.

---

## 📁 Folder Structure

```
Avebel-Connecter/
├── dist/
│   └── Avebel-Connecter.exe
├── screenshots/
│   ├── 1.png  (Connection Tab)
│   ├── 2.png  (Browser Tab)
│   ├── 3.png  (Query Tab)
│   ├── 4.png  (Schema Tab)
│   ├── 5.png  (Database Tab)
│   ├── 6.png  (Table Tab)
├── icons/
│   └── avebel.ico
├── main.py
└── README.md
```

---

## ⚙️ Requirements

* Python 3.7+
* psycopg2
* tkinter (comes preinstalled on most Python environments)
* PyInstaller (for building `.exe`)

---

## 🔐 Security Note

All credentials are used **only at runtime** and are not stored or logged locally. Avebel-Connecter does not collect any analytics or make outbound requests.


## 🧠 Future Plans

* MySQL support via plugin-based architecture
* Theme customization (light/dark mode)
* Backup/restore database tool
* Table visualizations (graph or ERD)

---

## 📜 License

MIT License — free for personal and commercial use.

---

## 👤 Author

**Avebel**

```
```
