import tkinter as tk
from tkinter import messagebox, simpledialog
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import json

class FileManager:
    def __init__(self, file_name="passwords.json"):
        self.file_name = file_name

    def load_from_json(self):
        try:
            with open(self.file_name, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"users": []}

    def save_to_json(self, data):
        with open(self.file_name, "w") as file:
            json.dump(data, file, indent=4)

class UserManager:
    def __init__(self):
        self.file_manager = FileManager()
        self.users = self.file_manager.load_from_json()

    def register(self, username, password):
        for user in self.users["users"]:
            if user["username"] == username:
                return False
        self.users["users"].append({"username": username, "master_password": password, "sites": []})
        self.file_manager.save_to_json(self.users)
        return True

    def login(self, username, password):
        for user in self.users["users"]:
            if user["username"] == username and user["master_password"] == password:
                return user
        return None

class AutoLogin:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option("useAutomationExtension", False)
        self.chrome_options.add_experimental_option("detach", True)

    def login_to_site(self, site_url, site_username, site_password):
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        driver.get(site_url)
        print(f"🌐 Actual URL opened: {driver.current_url}")

        try:
            username_field = driver.find_element(By.ID, "username")
            username_field.send_keys(site_username)

            print(f"✅ Username entered: {site_username}")

            password_field = driver.find_element(By.ID, "password")
            password_field.send_keys(site_password)

            print(f"✅ Filled in username and password for {site_url}.")

            input("Press Enter to continue...")

        except Exception as e:
            print(f"❌ Error occurred: {e}")
        finally:
            driver.quit()

class Interface:
    def __init__(self, root):
        self.user_manager = UserManager()
        self.user = None
        self.root = root
        self.root.title("Password Manager")
        self.root.geometry("400x400")
        self.login_screen()

    def login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Username:").pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()

        tk.Label(self.root, text="Password:").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        tk.Button(self.root, text="Login", command=self.login).pack()
        tk.Button(self.root, text="Register", command=self.register).pack()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.user = self.user_manager.login(username, password)
        if self.user:
            self.site_screen()
        else:
            messagebox.showerror("Error", "Login failed!")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if self.user_manager.register(username, password):
            messagebox.showinfo("Success", "Registration successful!")
        else:
            messagebox.showerror("Error", "This username is already taken!")

    def site_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text=f"Welcome {self.user['username']}").pack()
        tk.Button(self.root, text="Log Out", command=self.login_screen).pack()

        tk.Label(self.root, text="Saved Sites:").pack()

        self.site_listbox = tk.Listbox(self.root, height=5, selectmode=tk.SINGLE)
        for site in self.user["sites"]:
            self.site_listbox.insert(tk.END, site["site_name"])
        self.site_listbox.pack()

        tk.Button(self.root, text="Auto Login", command=self.auto_login).pack()
        tk.Button(self.root, text="Add New Site", command=self.add_new_site).pack()
        tk.Button(self.root, text="Delete Site", command=self.delete_site).pack()

    def add_new_site(self):
        site_name = simpledialog.askstring("Add New Site", "Enter Site Name:")
        site_username = simpledialog.askstring("Add New Site", "Enter Username:")
        site_password = simpledialog.askstring("Add New Site", "Enter Password:")

        if site_name and site_username and site_password:
            self.user["sites"].append({
                "site_name": site_name,
                "nickname": site_username,
                "password": site_password
            })
            self.user_manager.file_manager.save_to_json(self.user_manager.users)
            self.site_screen()
        else:
            messagebox.showerror("Error", "All fields must be filled!")

    def delete_site(self):
        selected_site_index = self.site_listbox.curselection()
        if selected_site_index:
            del self.user["sites"][selected_site_index[0]]
            self.user_manager.file_manager.save_to_json(self.user_manager.users)
            self.site_screen()
        else:
            messagebox.showerror("Error", "Please select a site!")

    def auto_login(self):
        selected_site_index = self.site_listbox.curselection()
        if selected_site_index:
            selected_site = self.user["sites"][selected_site_index[0]]
            site_name = selected_site["site_name"]
            site_username = selected_site["nickname"]
            site_password = selected_site["password"]

            auto_login = AutoLogin()
            auto_login.login_to_site(site_name, site_username, site_password)
        else:
            messagebox.showerror("Error", "Please select a site!")

root = tk.Tk()
app = Interface(root)
root.mainloop()