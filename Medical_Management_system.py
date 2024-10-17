from asyncio import sleep
import streamlit as st
import mysql.connector as sqlct
import pandas as pd
import datetime
from streamlit_option_menu import option_menu
import streamlit as st
import sqlite3
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

class LoginSystem:
    def __init__(self):
        self.mycn = None
        self.mycur = None
        self.cust = None
        self.role=None
        self.count=0
        
    def create_table(self):
        self.mycur.execute("SHOW TABLES LIKE 'medicineslist'")
        result = self.mycur.fetchone()
        if result is None:
            cmd1 = """
            CREATE TABLE medicineslist (
            ProductCode INT PRIMARY KEY,
            name CHAR(50) NOT NULL,
            Packing CHAR(50),
            Expirydate DATE,
            Company CHAR(50),
            Batch CHAR(10),
            Quantity INT,
            Rate FLOAT
            )"""
            self.mycur.execute(cmd1)
            self.mycur.execute(f"CREATE TABLE IF NOT EXISTS {self.dupli} (ProductCode INT, MedicineName VARCHAR(50), Quantity INT, CostPerPiece DECIMAL(10, 2), TotalCost DECIMAL(10, 2), FOREIGN KEY (ProductCode) REFERENCES medicineslist(ProductCode))")
            print("\tThank you for choosing to shop with Apollo Medical Store.")
        self.mycn.commit()




    def createdb(self):
        self.mycn = sqlct.connect(host="sql12.freesqldatabase.com", user="sql12738529", password="A5zw3LV1Qe", database="sql12738529")
        self.mycur = self.mycn.cursor()
        self.mycur.execute("SHOW TABLES LIKE 'users'")
        result = self.mycur.fetchone()
        if result is None:
            self.mycur.execute("CREATE TABLE IF NOT EXISTS users (username VARCHAR(255), name VARCHAR(255), phonenumber VARCHAR(255), password VARCHAR(255))")
        self.mycur.execute("SHOW TABLES LIKE 'admins'")
        result = self.mycur.fetchone()
        if result is None:
            self.mycur.execute("CREATE TABLE IF NOT EXISTS admins (username VARCHAR(255), name VARCHAR(255), phonenumber VARCHAR(255), password VARCHAR(255))")
        self.mycur.execute("SHOW TABLES LIKE 'medicineslist'")
        result = self.mycur.fetchone()
        if result is None:
            cmd1 = "CREATE TABLE medicineslist (ProductCode INT PRIMARY KEY, name CHAR(50) NOT NULL, Packing CHAR(50), Expirydate DATE, " \
                   "Company CHAR(50), Batch CHAR(10), Quantity INT, Rate FLOAT(10,2))"
            self.mycur.execute(cmd1)
            cust1 = "CREATE TABLE IF NOT EXISTS customertable (BillNumber INT, Customername VARCHAR(50), Doctorname VARCHAR(50), Productcode INT, " \
                    "Quantity INT, FOREIGN KEY (ProductCode) REFERENCES medicineslist(ProductCode))"
            self.mycur.execute(cust1)
            print("\tThank you for choosing to shop with Apollo Medical Store.")
        self.mycn.commit()

    def authenticate(self, username, password, role):
        if role == "admin" :
            self.mycur.execute("SELECT * FROM admins WHERE username = %s AND password = %s", (username, password))
            result = self.mycur.fetchone()
            if result is not None:
                return result[0]  
            else:
                return False
        elif role == "Customer":
            self.mycur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            result = self.mycur.fetchone()
            if result is not None:
                return result[0]
            else:
                return False
        else:
            return False

    def login(self):
        st.title("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Select Role", ["admin", "Customer"])
        login_button = st.button("Login")
        if login_button:
            authentication=self.authenticate(username, password, role)
            if authentication != False:
                st.success(f"Welcome, {authentication}!")
                st.balloons()
                st.empty()
                self.cust = authentication
                self.role = role
                if role=="admin":
                    st.session_state.user_id = 1
                    with open('customer.txt', 'w') as f:
                        f.write(f"{authentication}\n")
                        f.write(f'{st.session_state.user_id}')
                else:
                    st.session_state.user_id = 2
                    with open('customer.txt', 'w') as f:
                        f.write(f"{authentication}\n")
                        f.write(f'{st.session_state.user_id}')
            else:
                st.error("Invalid credentials. Please try again.")
                return None

    def sign_up(self):
        st.title("Sign Up")
        name = st.text_input("Name")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        retype_password = st.text_input("Retype Password", type="password")
        phone_number = st.text_input("Phone Number")
        role = st.selectbox("Select Role", ["admin", "Customer"])
        if role == "admin":
            admin_pass=st.text_input("Admin Password", type="password")
        sign_up_button = st.button("Sign Up")
        if sign_up_button:
            if len(username) < 6:
                st.error("Username must be at least 6 characters long. Please try again.")
            elif self.user_name_validation(username) == False:
                st.error("Username cannot contain special characters or spaces. Please try again.")
            elif password != retype_password:
                st.error("Passwords do not match. Please try again.")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters long. Please try again.")
            elif self.authenticate(username, password, role):
                st.error(f"User {username} already exists. Please try again.")
            elif len(phone_number) != 10:
                st.error("Phone number must be 10 digits long. Please try again.")
            else:
                if role=="admin" and admin_pass=="123456":
                    self.mycur.execute("INSERT INTO admins (username, name, phonenumber, password) VALUES (%s, %s, %s, %s)", (username, name, phone_number, password))
                    st.success(f"User {username} created successfully. Please login to continue.")
                elif role=="Customer":
                    self.mycur.execute("INSERT INTO users (username, name, phonenumber, password) VALUES (%s, %s, %s, %s)", (username, name, phone_number, password))
                    st.success(f"User {username} created successfully. Please login to continue.")
                elif role=="admin" and admin_pass!="123456":
                    st.error("Invalid admin password. Please try again.")
                self.mycn.commit()

    def display_tables(self):
        st.title("User Table")
        self.mycur.execute("SELECT * FROM users")
        users_data = self.mycur.fetchall()
        users_df = pd.DataFrame(users_data, columns=["Username", "Name", "Phone Number", "Password"])
        st.dataframe(users_df)
        st.title("Admin Table")
        self.mycur.execute("SELECT * FROM admins")
        admins_data = self.mycur.fetchall()
        admins_df = pd.DataFrame(admins_data, columns=["Username", "Name", "Phone Number", "Password"])
        st.dataframe(admins_df)

    def user_name_validation(self, input_string):
        # special_chars = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
        if ' ' in input_string:
            return False
        # for char in input_string:
        #     if char in special_chars:
        #         return False
        return True

    def add_medicine(self):
        st.header(f"Hello , {self.cust} !")
        st.header("Add Medicine")
        ProductCode = st.number_input("Enter the product code:", step=1, value=0)
        name = st.text_input("Enter name of the medicine:")
        Packing = st.text_input("Enter delivery details:")
        ExpiryDate = st.date_input("Enter expiry date of medicine:")
        Company = st.text_input("Enter name of the company:")
        Batch = st.number_input("Enter batch name of medicine:", step=1, value=0)
        Quantity = st.number_input("Enter quantity for your medicine:", step=1, value=0)
        Rate = st.number_input("Enter rate of your medicine:", value=0.0)
        if st.button("Add Medicine"):
            if self.check_duplicate_product_code(ProductCode):
                st.warning("Product code already exists.")
                return
            elif self.check_duplicate_product_name(name):
                st.warning("Medicine name already exists.")
                return
            ExpiryDate_str = ExpiryDate.strftime("%Y-%m-%d")
            rate_value = float(Rate)
            cmd5 = "INSERT INTO medicineslist VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            data = (ProductCode, name.lower(), Packing.lower(), ExpiryDate_str, Company.lower(), Batch, Quantity, rate_value)
            self.mycur.execute(cmd5, data)
            self.mycn.commit()
            st.success("Record has been added successfully.")

    def check_duplicate_product_name(self, product_name):
        cmd_check_duplicate = f"SELECT COUNT(*) FROM medicineslist WHERE name='{product_name.lower()}'"
        self.mycur.execute(cmd_check_duplicate)
        result = self.mycur.fetchone()
        if result[0] > 0:
            return True
        else:
            return False

    def check_duplicate_product_code(self, product_code):
        cmd_check_duplicate = f"SELECT COUNT(*) FROM medicineslist WHERE ProductCode={product_code}"
        self.mycur.execute(cmd_check_duplicate)
        result = self.mycur.fetchone()
        if result[0] > 0:
            return True
        else:
            return False
    
    def display_medicine(self):
        cmd2 = "SELECT * FROM medicineslist"
        self.mycur.execute(cmd2)
        r2 = self.mycur.fetchall()
        columns = ["Product Code", "Medicine Name", "Packing Details", "Expiry Date", "Company Name", "Batch", "Quantity", "Rate"]
        df = pd.DataFrame(r2, columns=columns)
        st.title("Display Medicines")
        st.table(df)
    
    def get_medicine_names(self):
        cmd_get_names = "SELECT DISTINCT name FROM medicineslist"
        self.mycur.execute(cmd_get_names)
        names = self.mycur.fetchall()
        return [name[0] for name in names]

    def search_medicine(self):
        st.header("Search Medicines")
        medicine_names = self.get_medicine_names()
        selected_med_name = st.selectbox("Select Medicine Name:", medicine_names, index=0, key="selected_med_name")
        if st.button("Search"):
            cmd4 = f"SELECT * FROM medicineslist WHERE name LIKE '%{selected_med_name}%'"
            self.mycur.execute(cmd4)
            r2 = self.mycur.fetchall()
            if not r2:
                st.warning("No records found.")
            else:
                columns = ["Product Code", "Medicine Name", "Packing Details", "Expiry Date", "Company Name", "Batch", "Quantity", "Rate"]
                df = pd.DataFrame(r2, columns=columns)
                st.table(df)

    def get_company_names(self):
        cmd_get_names = "SELECT DISTINCT Company FROM medicineslist"
        self.mycur.execute(cmd_get_names)
        companies = self.mycur.fetchall()
        return [company[0] for company in companies]

    def display_companies(self):
        st.header("Display Company-wise Medicines")
        company_names = self.get_company_names()
        company_name = st.selectbox("Select Company Name:", company_names, index=0, key="company_name")
        if st.button("Display"):
            cmd8 = f"SELECT * FROM medicineslist WHERE Company = '{company_name}'"
            self.mycur.execute(cmd8)
            r4 = self.mycur.fetchall()
            if not r4:
                st.warning("No records found.")
            else:
                columns = ["Product Code", "Medicine Name", "Packing Details", "Expiry Date", "Company Name", "Batch", "Quantity", "Rate"]
                df = pd.DataFrame(r4, columns=columns)
                st.table(df)

    def check_expiry_stock(self):
        expdate = datetime.date.today()
        y1 = expdate.year
        cmd6 = f"SELECT ProductCode, name, Expirydate, Batch, Quantity FROM medicineslist WHERE Expirydate <= '{str(expdate)}'"
        self.mycur.execute(cmd6)
        r2 = self.mycur.fetchall()
        st.header("Expiry Stock Module")
        if not r2:
            st.warning("No Expired Stock Found.")
        else:
            columns = ["Product Code", "Name", "Expiry Date", "Batch", "Quantity"]
            df = pd.DataFrame(r2, columns=columns)
            st.table(df)            

    def delete_medicine(self):
        st.header("Delete Medicine")
        medicine_names = self.get_medicine_names()
        selected_med_name = st.selectbox("Select Medicine Name:", medicine_names, index=0, key="selected_med_name")
        cmd_get_product_code = f"SELECT ProductCode FROM medicineslist WHERE name = '{selected_med_name}'"
        self.mycur.execute(cmd_get_product_code)
        product_code = self.mycur.fetchone()
        if product_code is not None:
            st.write(f"Product Code: {product_code[0]}")
            if st.button("Delete"):
                cmd3 = f"SELECT COUNT(*) FROM customertable WHERE Productcode={product_code[0]}"
                self.mycur.execute(cmd3)
                r3 = self.mycur.fetchone()
                total_record = r3[0]
                if total_record == 0:
                    cmd7 = f"DELETE FROM medicineslist WHERE ProductCode={product_code[0]}"
                    self.mycur.execute(cmd7)
                    self.mycn.commit()
                    st.success("Record has been deleted.")
                else:
                    cmd7 = f"UPDATE medicineslist SET quantity=0 WHERE ProductCode={product_code[0]}"
                    self.mycur.execute(cmd7)
                    self.mycn.commit()
                    st.warning("This medicine has already been sold, so it can't be deleted. The quantity of this medicine is set to zero.")
        else:
            st.warning("No product code found for the selected medicine.")


    def user_selection_page(self):
        st.markdown("## Please select an option to proceed.")
        # user_type = st.radio("", ["login", "signup","display"],horizontal=True)
        user_type = st.radio("", ["login", "signup"],horizontal=True)
        if user_type == "login":
            self.login()
        elif user_type == "signup":
            self.sign_up()
        elif user_type == "display":
            self.display_tables()
    
    def main(self, menu):
        self.customer=[]
        self.menu=menu
        self.createdb()
        st.set_page_config(page_title="app", page_icon="")
        st.sidebar.title("Medicine Management System")
        with open('customer.txt', 'r') as f:
            print("")
            for line in f:
                self.customer.append(line.strip())
        if "user_id" not in st.session_state:
            st.session_state.user_id = None
        if len(self.customer)==2:
            self.cust=self.customer[0]
            st.session_state.user_id=int(self.customer[1])
        if st.session_state.user_id is None:
            self.user_selection_page()
        elif st.session_state.user_id == 1:
            self.admin()
        elif st.session_state.user_id == 2:
            mms = class_Customer(self.customer[0])
            mms.main(["Add Bill","Search Bill"])
            
    def admin(self):
        st.sidebar.subheader("Customer Actions")
        admin_actions = ["Add Medicine", "Display Medicines", "Search Medicines", "Display Companies", "Check Expiry Stock", "Delete Medicine"]
        with st.sidebar:
            choice=option_menu(
                menu_title="Menu",
                options=admin_actions,
                menu_icon="cast",
                default_index=0,
            )
        if choice == "Add Medicine":
            self.add_medicine()
        elif choice == "Display Medicines":
            self.display_medicine()
        elif choice == "Search Medicines":
            self.search_medicine()
        elif choice == "Display Companies":
            self.display_companies()
        elif choice == "Check Expiry Stock":
            self.check_expiry_stock()
        elif choice == "Delete Medicine":
            self.delete_medicine()
        if st.sidebar.button('Logout'):
            st.sidebar.write('Logging out')
            with open('customer.txt', 'w'):
                pass
            st.session_state.user_id = None



class class_Customer():
    def __init__(self,customer_name):
        self.mycn = None
        self.mycur = None
        self.customer_name = customer_name.lower()
        self.dupli = customer_name.lower() + "dupli"
        self.create_db()
        self.get_tables_list()

    def create_db(self):
        conn = sqlite3.connect('MedicalManagement.db')
        self.mycur = conn.cursor()
        self.mycn = sqlct.connect(host="localhost", user="root", password="shannu", database="MedicalManagement")
        self.mycur = self.mycn.cursor()
    
    def create_table(self):
        self.mycur.execute("SHOW TABLES LIKE 'medicineslist'")
        result = self.mycur.fetchone()
        if result is None:
            cmd1 = """
            CREATE TABLE medicineslist (
            ProductCode INT PRIMARY KEY,
            name CHAR(50) NOT NULL,
            Packing CHAR(50),
            Expirydate DATE,
            Company CHAR(50),
            Batch CHAR(10),
            Quantity INT,
            Rate FLOAT
            )"""
            self.mycur.execute(cmd1)
            self.mycur.execute(f"CREATE TABLE IF NOT EXISTS {self.dupli} (ProductCode INT, MedicineName VARCHAR(50), Quantity INT, CostPerPiece DECIMAL(10, 2), TotalCost DECIMAL(10, 2), FOREIGN KEY (ProductCode) REFERENCES medicineslist(ProductCode))")
            print("\tThank you for choosing to shop with Apollo Medical Store.")
        self.mycn.commit()

    def get_tables_list(self):
        self.mycur.execute("SHOW TABLES;")
        table_names = self.mycur.fetchall()
        self.bill_numbers=[]
        table_names = [name[0] for name in table_names]
        for i in table_names:
            if self.customer_name == str(i)[:-3]:
                self.bill_numbers.append(int(i[-3:]))
        if self.bill_numbers:
            self.current_bill_number=max(self.bill_numbers)+1
        else:
            self.current_bill_number=1
        
    
    def main(self, menu):
        self.create_db()
        st.title(f"Hello {self.customer_name.capitalize()}!")
        with st.sidebar:
            choice=option_menu(
                menu_title="Menu",
                options=menu,
                menu_icon="cast",
                default_index=0,
            )
        if choice=="Add Bill":
            self.add_bill()
        elif choice=="Search Bill":
            self.search_bill()
        elif choice=="Display Tables":
            self.display_table()
        if st.sidebar.button('Logout'):
            st.sidebar.write('Logging out')
            with open('customer.txt', 'w'):
                pass
            st.session_state.user_id = None


    def add_bill(self):
        st.markdown("## Add Bill")
        self.mycur.execute(f"CREATE TABLE IF NOT EXISTS {self.dupli} (ProductCode INT, MedicineName VARCHAR(50), Quantity INT, CostPerPiece DECIMAL(10, 2), TotalCost DECIMAL(10, 2), FOREIGN KEY (ProductCode) REFERENCES medicineslist(ProductCode))")
        BillNumber=self.current_bill_number
        st.markdown(f"#Bill number : {BillNumber}")
        medicine_names = self.get_medicine_names()
        selected_med_name = st.selectbox("Select Medicine Name:", medicine_names, index=0, key="selected_med_name")
        product_code = self.get_product_code_by_name(selected_med_name)
        cost = self.get_cost_by_product_code(product_code)
        Quantity = st.number_input("Enter quantity:", step=1, value=1)
        cost1, cost2= st.columns(2)
        with cost1:
            st.write(f"Rate per piece: {cost}")
        total_cost = round(cost * Quantity,2)
        with cost2:
            st.write(f"Total Cost: {total_cost}")
        
        col1, col2, col3= st.columns(3)
        with col1:
            if st.button("Add to Bill"):
                cmd_check = f"SELECT COUNT(*) FROM {self.dupli} WHERE ProductCode = %s"
                self.mycur.execute(cmd_check, (product_code,))
                count = self.mycur.fetchone()[0]
                if count > 0:
                    cmd_update = f"UPDATE {self.dupli} SET Quantity = Quantity + %s, TotalCost = TotalCost + %s WHERE ProductCode = %s"
                    data_update = (Quantity, total_cost, product_code)
                    self.mycur.execute(cmd_update, data_update)
                else:
                    cmd_insert = f"INSERT INTO {self.dupli} (Productcode,MedicineName,Quantity, CostPerPiece, TotalCost) VALUES (%s, %s, %s, %s, %s)"
                    data_insert = (product_code, selected_med_name, Quantity, cost, total_cost)
                    self.mycur.execute(cmd_insert, data_insert)
                self.mycn.commit()
        with col2:
            if st.button("Delete Bill"):
                self.clear_table()
        with col3:
            self.mycur.execute(f"SELECT COUNT(*) FROM {self.dupli}")
            num_rows = self.mycur.fetchone()[0]
            if num_rows>0:
                if st.button("Generate Bill"):
                    self.generate_bill(BillNumber)
                    BillNumber+=1
        self.display_table()
    
    
    def delete_row(self, row_number):
        cmd = f"DELETE FROM {self.dupli} WHERE ROWID = {row_number}"
        self.mycur.execute(cmd)
        self.mycn.commit()

    def generate_bill(self, BillNumber):
        number="{:03d}".format(BillNumber)
        table_name = self.customer_name + number
        self.mycur.execute(f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM {self.dupli}")
        self.mycn.commit()
        self.mycur.execute(f"SELECT * FROM {self.dupli}")
        result = self.mycur.fetchall()
        data = [list(row) for row in result]
        st.success(f"Bill : {BillNumber} has been created successfully.")
        self.update_medicineslist_quantity()
        self.clear_table()
        
    def update_medicineslist_quantity(self):
        cmd = f"UPDATE medicineslist SET Quantity = Quantity - (SELECT SUM(Quantity) FROM {self.dupli} WHERE medicineslist.ProductCode = {self.dupli}.ProductCode) WHERE ProductCode IN (SELECT ProductCode FROM {self.dupli})"
        self.mycur.execute(cmd)
        self.mycn.commit()

    def clear_table(self):
        cmd = f"DELETE FROM {self.dupli}"
        self.mycur.execute(cmd)
        self.mycn.commit()

    def display_table(self):
        cmd = f"SELECT * FROM {self.dupli}"
        self.mycur.execute(cmd)
        result = self.mycur.fetchall()
        if result:
            df = pd.DataFrame(result, columns=["Productcode","MedicineName","Quantity", "CostPerPiece", "TotalCost"])
            df["TotalCost"] = df["TotalCost"].astype(float)
            df = df[["Productcode","MedicineName","Quantity", "CostPerPiece", "TotalCost"]]
            st.dataframe(df)
            total_cost = df["TotalCost"].sum()
            st.write(f"Total Cost: {total_cost}")

    def get_cost_by_product_code(self, product_code):
        cmd = f"SELECT Rate FROM medicineslist WHERE ProductCode = {product_code}"
        self.mycur.execute(cmd)
        result = self.mycur.fetchone()
        return result[0] if result is not None else None

    def get_medicine_names(self):
        cmd = "SELECT DISTINCT name FROM medicineslist"
        self.mycur.execute(cmd)
        medicine_names = [row[0] for row in self.mycur.fetchall()]
        return medicine_names

    def get_product_code_by_name(self, medicine_name):
        cmd = f"SELECT ProductCode FROM medicineslist WHERE name = '{medicine_name}'"
        self.mycur.execute(cmd)
        result = self.mycur.fetchone()
        return result[0] if result is not None else None
    
    def search_bill(self):
        bill_number = st.number_input("Enter Bill Number:", step=1, value=1)
        if st.button("Search"):
            if bill_number in self.bill_numbers:
                number="{:03d}".format(bill_number)
                table_name = self.customer_name + number
                cmd = f"SELECT * FROM {table_name}"
                self.mycur.execute(cmd)
                result = self.mycur.fetchall()
                if result:
                    df = pd.DataFrame(result, columns=["Productcode","MedicineName","Quantity", "CostPerPiece", "TotalCost"])
                    df["TotalCost"] = df["TotalCost"].astype(float)
                    df = df[["Productcode","MedicineName","Quantity", "CostPerPiece", "TotalCost"]]
                    st.dataframe(df)
                    total_cost = df["TotalCost"].sum()
                    st.write(f"Total Cost: {total_cost}")
            else:
                st.warning("No records found.")
    


if __name__ == "__main__":
    login_system = LoginSystem()
    login_system.main(["login", "sign_up","Display Tables",])
