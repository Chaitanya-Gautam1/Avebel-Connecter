import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import psycopg2
from psycopg2.extras import RealDictCursor
import csv
import json

class PostgreSQLGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Avebel Connecter")
        self.root.geometry("1200x800")
        
        self.connection = None
        self.current_table = None
        self.table_columns = []
        self.current_table_data = []
        self.setup_gui()
        
    def setup_gui(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Connection tab
        self.setup_connection_tab()
        
        # Browser tab
        self.setup_browser_tab()
        
        # Query tab
        self.setup_query_tab()
        
        # Schema tab
        self.setup_schema_tab()
        
        # Database Management tab
        self.setup_database_tab()
        
        # Table Management tab
        self.setup_table_tab()
        
    def setup_connection_tab(self):
        # Connection Frame
        conn_frame = ttk.Frame(self.notebook)
        self.notebook.add(conn_frame, text="🔗 Connection")
        
        tk.Label(conn_frame, text="PostgreSQL Connection URL:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)
        
        self.url_entry = tk.Entry(conn_frame, width=100, font=("Courier", 10))
        self.url_entry.insert(0, "postgres://username:password@host:port/database")
        self.url_entry.pack(padx=10, pady=5)
        
        # Connection buttons
        btn_frame = tk.Frame(conn_frame)
        btn_frame.pack(pady=10)
        
        self.connect_btn = tk.Button(btn_frame, text="🔌 Connect", command=self.connect_db, 
                                   bg="green", fg="white", font=("Arial", 10, "bold"))
        self.connect_btn.pack(side=tk.LEFT, padx=5)
        
        self.disconnect_btn = tk.Button(btn_frame, text="❌ Disconnect", command=self.disconnect_db, 
                                      bg="red", fg="white", font=("Arial", 10, "bold"))
        self.disconnect_btn.pack(side=tk.LEFT, padx=5)
        
        # Connection status
        self.status_label = tk.Label(conn_frame, text="Status: Not Connected", 
                                   fg="red", font=("Arial", 10, "bold"))
        self.status_label.pack(pady=5)
        
        # Connection info display
        self.info_text = scrolledtext.ScrolledText(conn_frame, height=15, width=100)
        self.info_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
    def setup_browser_tab(self):
        # Database Browser Frame
        browser_frame = ttk.Frame(self.notebook)
        self.notebook.add(browser_frame, text="🗂️ Browser")
        
        # Left panel - Tree view
        left_frame = tk.Frame(browser_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 5), pady=10)
        
        tk.Label(left_frame, text="Database Objects:", font=("Arial", 12, "bold")).pack(anchor="w")
        
        # Treeview for database objects
        self.tree = ttk.Treeview(left_frame)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.column("#0", width=250, minwidth=200)
        self.tree.bind("<Double-1>", self.on_tree_select)
        
        refresh_btn = tk.Button(left_frame, text="🔄 Refresh", command=self.refresh_browser)
        refresh_btn.pack(pady=5)
        
        # Right panel - Table data
        right_frame = tk.Frame(browser_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=10)
        
        tk.Label(right_frame, text="Table Data:", font=("Arial", 12, "bold")).pack(anchor="w")
        
        # Table display with scrollbars
        table_frame = tk.Frame(right_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        self.table_display = ttk.Treeview(table_frame)
        
        # Scrollbars for table
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.table_display.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.table_display.xview)
        
        self.table_display.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.table_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Export button
        export_btn = tk.Button(right_frame, text="📊 Export to CSV", command=self.export_data)
        export_btn.pack(pady=5)
        
    def setup_query_tab(self):
        # Query Frame
        query_frame = ttk.Frame(self.notebook)
        self.notebook.add(query_frame, text="🔍 Query")
        
        tk.Label(query_frame, text="SQL Query:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)
        
        # Query input
        self.query_text = scrolledtext.ScrolledText(query_frame, height=10, width=100, font=("Courier", 10))
        self.query_text.pack(padx=10, pady=5, fill=tk.X)
        
        # Query buttons
        query_btn_frame = tk.Frame(query_frame)
        query_btn_frame.pack(pady=5)
        
        execute_btn = tk.Button(query_btn_frame, text="▶️ Execute Query", command=self.execute_query,
                              bg="blue", fg="white", font=("Arial", 10, "bold"))
        execute_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(query_btn_frame, text="🗑️ Clear", command=lambda: self.query_text.delete("1.0", tk.END))
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Results
        tk.Label(query_frame, text="Results:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
        
        self.results_text = scrolledtext.ScrolledText(query_frame, height=20, width=100, font=("Courier", 9))
        self.results_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
    def setup_schema_tab(self):
        # Schema Frame
        schema_frame = ttk.Frame(self.notebook)
        self.notebook.add(schema_frame, text="🏗️ Schema")
        
        tk.Label(schema_frame, text="SQL Schema/DDL Commands:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)
        
        self.schema_text = scrolledtext.ScrolledText(schema_frame, height=20, width=100, font=("Courier", 10))
        self.schema_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # Schema buttons
        schema_btn_frame = tk.Frame(schema_frame)
        schema_btn_frame.pack(pady=10)
        
        run_schema_btn = tk.Button(schema_btn_frame, text="🚀 Run Schema", command=self.run_schema,
                                 bg="green", fg="white", font=("Arial", 10, "bold"))
        run_schema_btn.pack(side=tk.LEFT, padx=5)
        
        load_file_btn = tk.Button(schema_btn_frame, text="📁 Load SQL File", command=self.load_sql_file)
        load_file_btn.pack(side=tk.LEFT, padx=5)
        
        save_file_btn = tk.Button(schema_btn_frame, text="💾 Save SQL File", command=self.save_sql_file)
        save_file_btn.pack(side=tk.LEFT, padx=5)
        
    def setup_database_tab(self):
        # Database Management Frame
        db_frame = ttk.Frame(self.notebook)
        self.notebook.add(db_frame, text="🗄️ Databases")
        
        # Database operations
        tk.Label(db_frame, text="Database Management:", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=10)
        
        # Create database section
        create_db_frame = tk.LabelFrame(db_frame, text="Create Database", font=("Arial", 12, "bold"))
        create_db_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(create_db_frame, text="Database Name:").pack(anchor="w", padx=10, pady=5)
        self.new_db_entry = tk.Entry(create_db_frame, width=40, font=("Arial", 10))
        self.new_db_entry.pack(padx=10, pady=5)
        
        create_db_btn = tk.Button(create_db_frame, text="➕ Create Database", command=self.create_database,
                                bg="green", fg="white", font=("Arial", 10, "bold"))
        create_db_btn.pack(padx=10, pady=5)
        
        # List databases section
        list_db_frame = tk.LabelFrame(db_frame, text="Existing Databases", font=("Arial", 12, "bold"))
        list_db_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Database listbox with scrollbar
        db_list_frame = tk.Frame(list_db_frame)
        db_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.db_listbox = tk.Listbox(db_list_frame, font=("Arial", 10))
        db_scrollbar = tk.Scrollbar(db_list_frame, orient=tk.VERTICAL, command=self.db_listbox.yview)
        self.db_listbox.configure(yscrollcommand=db_scrollbar.set)
        
        self.db_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        db_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Database action buttons
        db_btn_frame = tk.Frame(list_db_frame)
        db_btn_frame.pack(pady=10)
        
        refresh_db_btn = tk.Button(db_btn_frame, text="🔄 Refresh", command=self.refresh_databases)
        refresh_db_btn.pack(side=tk.LEFT, padx=5)
        
        drop_db_btn = tk.Button(db_btn_frame, text="🗑️ Drop Database", command=self.drop_database,
                              bg="red", fg="white", font=("Arial", 10, "bold"))
        drop_db_btn.pack(side=tk.LEFT, padx=5)
        
    def setup_table_tab(self):
        # Table Management Frame
        table_frame = ttk.Frame(self.notebook)
        self.notebook.add(table_frame, text="📋 Tables")
        
        # Create main sections
        left_table_frame = tk.Frame(table_frame)
        left_table_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 5), pady=10)
        
        right_table_frame = tk.Frame(table_frame)
        right_table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=10)
        
        # Left side - Table creation and management
        tk.Label(left_table_frame, text="Table Management:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))
        
        # Create table section
        create_table_frame = tk.LabelFrame(left_table_frame, text="Create Table", font=("Arial", 10, "bold"))
        create_table_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(create_table_frame, text="Table Name:").pack(anchor="w", padx=5, pady=2)
        self.table_name_entry = tk.Entry(create_table_frame, width=25)
        self.table_name_entry.pack(padx=5, pady=2)
        
        tk.Label(create_table_frame, text="Columns (name:type):").pack(anchor="w", padx=5, pady=2)
        self.columns_text = scrolledtext.ScrolledText(create_table_frame, height=8, width=30, font=("Courier", 9))
        self.columns_text.pack(padx=5, pady=2)
        self.columns_text.insert(tk.END, "id SERIAL PRIMARY KEY,\nname VARCHAR(100),\nemail VARCHAR(255)")
        
        create_table_btn = tk.Button(create_table_frame, text="➕ Create Table", command=self.create_table,
                                   bg="green", fg="white", font=("Arial", 9, "bold"))
        create_table_btn.pack(pady=5)
        
        # Table operations section
        ops_frame = tk.LabelFrame(left_table_frame, text="Table Operations", font=("Arial", 10, "bold"))
        ops_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(ops_frame, text="Select Table:").pack(anchor="w", padx=5, pady=2)
        self.table_combo = ttk.Combobox(ops_frame, width=22, state="readonly")
        self.table_combo.pack(padx=5, pady=2)
        
        table_ops_btn_frame = tk.Frame(ops_frame)
        table_ops_btn_frame.pack(pady=5)
        
        view_table_btn = tk.Button(table_ops_btn_frame, text="👁️ View", command=self.view_selected_table,
                                 bg="blue", fg="white", font=("Arial", 8))
        view_table_btn.pack(side=tk.TOP, pady=2, fill=tk.X)
        
        drop_table_btn = tk.Button(table_ops_btn_frame, text="🗑️ Drop", command=self.drop_table,
                                 bg="red", fg="white", font=("Arial", 8))
        drop_table_btn.pack(side=tk.TOP, pady=2, fill=tk.X)
        
        refresh_tables_btn = tk.Button(table_ops_btn_frame, text="🔄 Refresh", command=self.refresh_table_list)
        refresh_tables_btn.pack(side=tk.TOP, pady=2, fill=tk.X)
        
        # Right side - Table data and editing
        tk.Label(right_table_frame, text="Table Data Editor:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))
        
        # Current table label
        self.current_table_label = tk.Label(right_table_frame, text="No table selected", 
                                          font=("Arial", 10, "italic"), fg="gray")
        self.current_table_label.pack(anchor="w")
        
        # Data display frame
        data_frame = tk.Frame(right_table_frame)
        data_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Table data display
        self.data_tree = ttk.Treeview(data_frame)
        data_v_scroll = ttk.Scrollbar(data_frame, orient=tk.VERTICAL, command=self.data_tree.yview)
        data_h_scroll = ttk.Scrollbar(data_frame, orient=tk.HORIZONTAL, command=self.data_tree.xview)
        
        self.data_tree.configure(yscrollcommand=data_v_scroll.set, xscrollcommand=data_h_scroll.set)
        
        self.data_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        data_v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        data_h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Data operation buttons
        data_btn_frame = tk.Frame(right_table_frame)
        data_btn_frame.pack(pady=5)
        
        add_row_btn = tk.Button(data_btn_frame, text="➕ Add Row", command=self.show_add_row_dialog,
                              bg="green", fg="white", font=("Arial", 9, "bold"))
        add_row_btn.pack(side=tk.LEFT, padx=2)
        
        edit_row_btn = tk.Button(data_btn_frame, text="✏️ Edit Row", command=self.show_edit_row_dialog,
                               bg="orange", fg="white", font=("Arial", 9, "bold"))
        edit_row_btn.pack(side=tk.LEFT, padx=2)
        
        delete_row_btn = tk.Button(data_btn_frame, text="🗑️ Delete Row", command=self.delete_row,
                                 bg="red", fg="white", font=("Arial", 9, "bold"))
        delete_row_btn.pack(side=tk.LEFT, padx=2)
        
        refresh_data_btn = tk.Button(data_btn_frame, text="🔄 Refresh Data", command=self.refresh_table_data)
        refresh_data_btn.pack(side=tk.LEFT, padx=2)
        
    # Connection Methods
    def connect_db(self):
        db_url = self.url_entry.get().strip()
        if not db_url:
            messagebox.showwarning("Input Error", "Please provide database URL.")
            return
            
        try:
            self.connection = psycopg2.connect(db_url)
            self.status_label.config(text="Status: Connected ✅", fg="green")
            self.connect_btn.config(state="disabled")
            self.disconnect_btn.config(state="normal")
            
            # Show connection info
            self.show_connection_info()
            self.refresh_browser()
            self.refresh_databases()
            self.refresh_table_list()
            
            messagebox.showinfo("Success", "Connected to database successfully!")
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"❌ {str(e)}")
            
    def disconnect_db(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            
        self.status_label.config(text="Status: Not Connected ❌", fg="red")
        self.connect_btn.config(state="normal")
        self.disconnect_btn.config(state="disabled")
        
        # Clear displays
        self.info_text.delete("1.0", tk.END)
        self.tree.delete(*self.tree.get_children())
        self.table_display.delete(*self.table_display.get_children())
        self.db_listbox.delete(0, tk.END)
        self.table_combo['values'] = ()
        self.data_tree.delete(*self.data_tree.get_children())
        
    def show_connection_info(self):
        if not self.connection:
            return
            
        try:
            with self.connection.cursor() as cur:
                # Get database info
                cur.execute("SELECT version();")
                version = cur.fetchone()[0]
                
                cur.execute("SELECT current_database();")
                db_name = cur.fetchone()[0]
                
                cur.execute("SELECT current_user;")
                user = cur.fetchone()[0]
                
                cur.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';")
                table_count = cur.fetchone()[0]
                
                info = f"""Database Information:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Database: {db_name}
User: {user}
Tables in 'public' schema: {table_count}

PostgreSQL Version:
{version}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
                
                self.info_text.delete("1.0", tk.END)
                self.info_text.insert(tk.END, info)
                
        except Exception as e:
            self.info_text.delete("1.0", tk.END)
            self.info_text.insert(tk.END, f"Error getting database info: {e}")
            
    # Browser Methods
    def refresh_browser(self):
        if not self.connection:
            messagebox.showwarning("Not Connected", "Please connect to database first.")
            return
            
        try:
            self.tree.delete(*self.tree.get_children())
            
            with self.connection.cursor() as cur:
                # Get schemas
                cur.execute("""
                    SELECT schema_name 
                    FROM information_schema.schemata 
                    WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                    ORDER BY schema_name;
                """)
                schemas = cur.fetchall()
                
                for schema in schemas:
                    schema_name = schema[0]
                    schema_node = self.tree.insert("", "end", text=f"📁 {schema_name}", values=("schema", schema_name))
                    
                    # Get tables in schema
                    cur.execute("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = %s 
                        ORDER BY table_name;
                    """, (schema_name,))
                    tables = cur.fetchall()
                    
                    for table in tables:
                        table_name = table[0]
                        self.tree.insert(schema_node, "end", text=f"📋 {table_name}", 
                                       values=("table", schema_name, table_name))
                        
        except Exception as e:
            messagebox.showerror("Browser Error", f"❌ {str(e)}")
            
    def on_tree_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
            
        item = self.tree.item(selection[0])
        values = item['values']
        
        if len(values) >= 3 and values[0] == "table":
            schema_name = values[1]
            table_name = values[2]
            self.show_table_data(schema_name, table_name)
            
    def show_table_data(self, schema_name, table_name):
        if not self.connection:
            return
            
        try:
            # Clear previous data
            self.table_display.delete(*self.table_display.get_children())
            
            with self.connection.cursor(cursor_factory=RealDictCursor) as cur:
                # Get table data (limit to first 1000 rows)
                cur.execute(f"SELECT * FROM {schema_name}.{table_name} LIMIT 1000;")
                rows = cur.fetchall()
                
                if not rows:
                    # Show table structure even if empty
                    cur.execute(f"""
                        SELECT column_name, data_type, is_nullable, column_default
                        FROM information_schema.columns 
                        WHERE table_schema = %s AND table_name = %s 
                        ORDER BY ordinal_position;
                    """, (schema_name, table_name))
                    
                    columns_info = cur.fetchall()
                    if columns_info:
                        # Show empty table with column headers
                        columns = [col[0] for col in columns_info]
                        self.table_display["columns"] = columns
                        self.table_display["show"] = "headings"
                        
                        for i, col_info in enumerate(columns_info):
                            col_name, data_type, nullable, default = col_info
                            header_text = f"{col_name}\n({data_type})"
                            self.table_display.heading(columns[i], text=header_text)
                            self.table_display.column(columns[i], width=120)
                        
                        messagebox.showinfo("Empty Table", f"Table {table_name} is empty but structure is shown.")
                        return
                    else:
                        messagebox.showinfo("No Data", f"Table {table_name} is empty.")
                        return
                
                # Set up columns
                columns = list(rows[0].keys())
                self.table_display["columns"] = columns
                self.table_display["show"] = "headings"
                
                # Configure column headings
                for col in columns:
                    self.table_display.heading(col, text=col)
                    self.table_display.column(col, width=100)
                
                # Insert data
                self.current_table_data = []
                for row in rows:
                    values = [str(row[col]) if row[col] is not None else "NULL" for col in columns]
                    self.table_display.insert("", "end", values=values)
                    self.current_table_data.append(dict(row))
                    
        except Exception as e:
            messagebox.showerror("Data Error", f"❌ {str(e)}")
            
    # Query Methods
    def execute_query(self):
        if not self.connection:
            messagebox.showwarning("Not Connected", "Please connect to database first.")
            return
            
        query = self.query_text.get("1.0", tk.END).strip()
        if not query:
            messagebox.showwarning("Empty Query", "Please enter a SQL query.")
            return
            
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query)
                
                # Check if it's a SELECT query
                if query.strip().upper().startswith("SELECT"):
                    rows = cur.fetchall()
                    if rows:
                        # Format results
                        columns = list(rows[0].keys())
                        result = f"Results ({len(rows)} rows):\n" + "="*50 + "\n"
                        
                        # Header
                        header = " | ".join(f"{col:15}" for col in columns)
                        result += header + "\n" + "-" * len(header) + "\n"
                        
                        # Data rows
                        for row in rows:
                            row_data = " | ".join(f"{str(row[col]):15}" if row[col] is not None else f"{'NULL':15}" 
                                                for col in columns)
                            result += row_data + "\n"
                    else:
                        result = "Query executed successfully. No rows returned."
                else:
                    # For non-SELECT queries
                    self.connection.commit()
                    result = f"Query executed successfully. {cur.rowcount} rows affected."
                    
                self.results_text.delete("1.0", tk.END)
                self.results_text.insert(tk.END, result)
                
        except Exception as e:
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert(tk.END, f"❌ Error: {str(e)}")
            
    # Schema Methods
    def run_schema(self):
        if not self.connection:
            messagebox.showwarning("Not Connected", "Please connect to database first.")
            return
            
        schema_sql = self.schema_text.get("1.0", tk.END).strip()
        if not schema_sql:
            messagebox.showwarning("Empty Schema", "Please enter SQL schema commands.")
            return
            
        try:
            with self.connection.cursor() as cur:
                cur.execute(schema_sql)
            self.connection.commit()
            messagebox.showinfo("Success", "✅ Schema executed successfully.")
            self.refresh_browser()
            
        except Exception as e:
            messagebox.showerror("Schema Error", f"❌ {str(e)}")
            
    def load_sql_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("SQL files", "*.sql"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    content = f.read()
                self.schema_text.delete("1.0", tk.END)
                self.schema_text.insert(tk.END, content)
                
            except Exception as e:
                messagebox.showerror("Load Error", f"❌ {str(e)}")
                
    def save_sql_file(self):
        content = self.schema_text.get("1.0", tk.END)
        if not content.strip():
            messagebox.showwarning("Empty Content", "No SQL content to save.")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".sql",
            filetypes=[("SQL files", "*.sql"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(content)
                messagebox.showinfo("Save Success", f"SQL saved to {filename}")
                
            except Exception as e:
                messagebox.showerror("Save Error", f"❌ {str(e)}")
                
    # Database Management Methods
    def create_database(self):
        if not self.connection:
            messagebox.showwarning("Not Connected", "Please connect to database first.")
            return
            
        db_name = self.new_db_entry.get().strip()
        if not db_name:
            messagebox.showwarning("Input Error", "Please enter a database name.")
            return
            
        try:
            # Need to use autocommit for CREATE DATABASE
            self.connection.autocommit = True
            with self.connection.cursor() as cur:
                cur.execute(f'CREATE DATABASE "{db_name}";')
            self.connection.autocommit = False
            
            messagebox.showinfo("Success", f"✅ Database '{db_name}' created successfully.")
            self.new_db_entry.delete(0, tk.END)
            self.refresh_databases()
            
        except Exception as e:
            self.connection.autocommit = False
            messagebox.showerror("Database Creation Error", f"❌ {str(e)}")
            
    def refresh_databases(self):
        if not self.connection:
            return
            
        try:
            self.db_listbox.delete(0, tk.END)
            with self.connection.cursor() as cur:
                cur.execute("""
                    SELECT datname FROM pg_database 
                    WHERE datistemplate = false 
                    ORDER BY datname;
                """)
                databases = cur.fetchall()
                
                for db in databases:
                    self.db_listbox.insert(tk.END, db[0])
                    
        except Exception as e:
            messagebox.showerror("Database List Error", f"❌ {str(e)}")
            
    def drop_database(self):
        selection = self.db_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a database to drop.")
            return
            
        db_name = self.db_listbox.get(selection[0])
        
        result = messagebox.askyesno("Confirm Drop", 
                                   f"Are you sure you want to drop database '{db_name}'?\n\nThis action cannot be undone!")
        if not result:
            return
            
        try:
            self.connection.autocommit = True
            with self.connection.cursor() as cur:
                cur.execute(f'DROP DATABASE "{db_name}";')
            self.connection.autocommit = False
            
            messagebox.showinfo("Success", f"✅ Database '{db_name}' dropped successfully.")
            self.refresh_databases()
            
        except Exception as e:
            self.connection.autocommit = False
            messagebox.showerror("Database Drop Error", f"❌ {str(e)}")
            
    # Table Management Methods
    def create_table(self):
        if not self.connection:
            messagebox.showwarning("Not Connected", "Please connect to database first.")
            return
            
        table_name = self.table_name_entry.get().strip()
        columns_text = self.columns_text.get("1.0", tk.END).strip()
        
        if not table_name or not columns_text:
            messagebox.showwarning("Input Error", "Please provide table name and columns.")
            return
            
        try:
            # Build CREATE TABLE statement
            sql = f"CREATE TABLE {table_name} (\n{columns_text}\n);"
            
            with self.connection.cursor() as cur:
                cur.execute(sql)
            self.connection.commit()
            
            messagebox.showinfo("Success", f"✅ Table '{table_name}' created successfully.")
            self.table_name_entry.delete(0, tk.END)
            self.refresh_browser()
            self.refresh_table_list()
            
        except Exception as e:
            messagebox.showerror("Table Creation Error", f"❌ {str(e)}")
            
    def refresh_table_list(self):
        if not self.connection:
            return
            
        try:
            with self.connection.cursor() as cur:
                cur.execute("""
                    SELECT schemaname||'.'||tablename as full_name
                    FROM pg_tables 
                    WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
                    ORDER BY schemaname, tablename;
                """)
                tables = cur.fetchall()
                
                table_list = [table[0] for table in tables]
                self.table_combo['values'] = table_list
                
        except Exception as e:
            messagebox.showerror("Table List Error", f"❌ {str(e)}")
            
    def view_selected_table(self):
        selected_table = self.table_combo.get()
        if not selected_table:
            messagebox.showwarning("No Selection", "Please select a table to view.")
            return
            
        self.current_table = selected_table
        self.current_table_label.config(text=f"Current Table: {selected_table}", fg="black")
        self.refresh_table_data()
        
    def refresh_table_data(self):
        if not self.connection or not self.current_table:
            return
            
        try:
            # Clear previous data
            self.data_tree.delete(*self.data_tree.get_children())
            
            with self.connection.cursor(cursor_factory=RealDictCursor) as cur:
                # First get column information
                schema_table = self.current_table.split('.')
                if len(schema_table) == 2:
                    schema_name, table_name = schema_table
                else:
                    schema_name, table_name = 'public', self.current_table
                    
                cur.execute(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_schema = %s AND table_name = %s 
                    ORDER BY ordinal_position;
                """, (schema_name, table_name))
                
                column_info = cur.fetchall()
                self.table_columns = [col['column_name'] for col in column_info]
                
                # Set up columns
                self.data_tree["columns"] = self.table_columns
                self.data_tree["show"] = "headings"
                
                # Configure column headings
                for col_info in column_info:
                    col_name = col_info['column_name']
                    data_type = col_info['data_type']
                    self.data_tree.heading(col_name, text=f"{col_name}\n({data_type})")
                    self.data_tree.column(col_name, width=120)
                
                # Get table data
                cur.execute(f"SELECT * FROM {self.current_table} ORDER BY 1;")
                rows = cur.fetchall()
                
                # Insert data
                for row in rows:
                    values = [str(row[col]) if row[col] is not None else "NULL" for col in self.table_columns]
                    self.data_tree.insert("", "end", values=values)
                    
                if not rows:
                    messagebox.showinfo("Empty Table", f"Table {self.current_table} is empty but structure is shown.")
                    
        except Exception as e:
            messagebox.showerror("Data Refresh Error", f"❌ {str(e)}")
            
    def drop_table(self):
        selected_table = self.table_combo.get()
        if not selected_table:
            messagebox.showwarning("No Selection", "Please select a table to drop.")
            return
            
        result = messagebox.askyesno("Confirm Drop", 
                                   f"Are you sure you want to drop table '{selected_table}'?\n\nThis action cannot be undone!")
        if not result:
            return
            
        try:
            with self.connection.cursor() as cur:
                cur.execute(f'DROP TABLE {selected_table};')
            self.connection.commit()
            
            messagebox.showinfo("Success", f"✅ Table '{selected_table}' dropped successfully.")
            self.refresh_browser()
            self.refresh_table_list()
            
            if self.current_table == selected_table:
                self.current_table = None
                self.current_table_label.config(text="No table selected", fg="gray")
                self.data_tree.delete(*self.data_tree.get_children())
                
        except Exception as e:
            messagebox.showerror("Table Drop Error", f"❌ {str(e)}")
            
    # Row Management Methods
    def show_add_row_dialog(self):
        if not self.current_table or not self.table_columns:
            messagebox.showwarning("No Table", "Please select a table first.")
            return
            
        self.row_dialog("Add", "Insert")
        
    def show_edit_row_dialog(self):
        selection = self.data_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a row to edit.")
            return
            
        if not self.current_table or not self.table_columns:
            messagebox.showwarning("No Table", "Please select a table first.")
            return
            
        # Get current values
        item = self.data_tree.item(selection[0])
        current_values = item['values']
        
        self.row_dialog("Edit", "Update", current_values, selection[0])
        
    def row_dialog(self, mode, action, current_values=None, tree_item=None):
        dialog = tk.Toplevel(self.root)
        dialog.title(f"{mode} Row - {self.current_table}")
        dialog.geometry("400x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        tk.Label(dialog, text=f"{mode} Row in {self.current_table}", 
                font=("Arial", 12, "bold")).pack(pady=10)
        
        # Create entry fields for each column
        entries = {}
        
        # Scrollable frame for many columns
        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for i, col in enumerate(self.table_columns):
            row_frame = tk.Frame(scrollable_frame)
            row_frame.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(row_frame, text=f"{col}:", width=15, anchor="w").pack(side=tk.LEFT)
            
            entry = tk.Entry(row_frame, width=30)
            entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
            
            if current_values and i < len(current_values):
                value = current_values[i]
                if value != "NULL":
                    entry.insert(0, str(value))
            
            entries[col] = entry
        
        canvas.pack(side="left", fill="both", expand=True, padx=(10, 0))
        scrollbar.pack(side="right", fill="y", padx=(0, 10))
        
        # Buttons
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        def save_row():
            try:
                values = {}
                for col, entry in entries.items():
                    value = entry.get().strip()
                    values[col] = value if value and value.upper() != "NULL" else None
                
                if mode == "Add":
                    # INSERT
                    cols = ', '.join(values.keys())
                    placeholders = ', '.join(['%s'] * len(values))
                    sql = f"INSERT INTO {self.current_table} ({cols}) VALUES ({placeholders})"
                    
                    with self.connection.cursor() as cur:
                        cur.execute(sql, list(values.values()))
                    self.connection.commit()
                    
                    messagebox.showinfo("Success", "✅ Row added successfully.")
                    
                else:  # Edit mode
                    # UPDATE - need to identify the row somehow
                    # For simplicity, we'll update based on all original values
                    if current_values:
                        set_clause = ', '.join([f"{col} = %s" for col in values.keys()])
                        where_conditions = []
                        where_values = []
                        
                        for i, col in enumerate(self.table_columns):
                            if i < len(current_values):
                                if current_values[i] == "NULL":
                                    where_conditions.append(f"{col} IS NULL")
                                else:
                                    where_conditions.append(f"{col} = %s")
                                    where_values.append(current_values[i])
                        
                        where_clause = ' AND '.join(where_conditions)
                        sql = f"UPDATE {self.current_table} SET {set_clause} WHERE {where_clause}"
                        
                        with self.connection.cursor() as cur:
                            cur.execute(sql, list(values.values()) + where_values)
                        self.connection.commit()
                        
                        messagebox.showinfo("Success", "✅ Row updated successfully.")
                
                dialog.destroy()
                self.refresh_table_data()
                
            except Exception as e:
                messagebox.showerror("Save Error", f"❌ {str(e)}")
        
        save_btn = tk.Button(btn_frame, text=f"💾 {action}", command=save_row,
                           bg="green", fg="white", font=("Arial", 10, "bold"))
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(btn_frame, text="❌ Cancel", command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
    def delete_row(self):
        selection = self.data_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a row to delete.")
            return
            
        if not self.current_table or not self.table_columns:
            messagebox.showwarning("No Table", "Please select a table first.")
            return
            
        result = messagebox.askyesno("Confirm Delete", 
                                   "Are you sure you want to delete the selected row?\n\nThis action cannot be undone!")
        if not result:
            return
            
        try:
            # Get current values to build WHERE clause
            item = self.data_tree.item(selection[0])
            current_values = item['values']
            
            where_conditions = []
            where_values = []
            
            for i, col in enumerate(self.table_columns):
                if i < len(current_values):
                    if current_values[i] == "NULL":
                        where_conditions.append(f"{col} IS NULL")
                    else:
                        where_conditions.append(f"{col} = %s")
                        where_values.append(current_values[i])
            
            where_clause = ' AND '.join(where_conditions)
            sql = f"DELETE FROM {self.current_table} WHERE {where_clause}"
            
            with self.connection.cursor() as cur:
                cur.execute(sql, where_values)
            self.connection.commit()
            
            messagebox.showinfo("Success", "✅ Row deleted successfully.")
            self.refresh_table_data()
            
        except Exception as e:
            messagebox.showerror("Delete Error", f"❌ {str(e)}")
            
    # Export Methods
    def export_data(self):
        if not self.current_table_data:
            messagebox.showwarning("No Data", "No table data to export.")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    with open(filename, 'w') as f:
                        json.dump(self.current_table_data, f, indent=2, default=str)
                else:
                    with open(filename, 'w', newline='') as f:
                        if self.current_table_data:
                            writer = csv.DictWriter(f, fieldnames=self.current_table_data[0].keys())
                            writer.writeheader()
                            writer.writerows(self.current_table_data)
                            
                messagebox.showinfo("Export Success", f"Data exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"❌ {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PostgreSQLGUI(root)
    root.mainloop()
