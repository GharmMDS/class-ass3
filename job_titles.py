import tkinter as tk
from tkinter import ttk
import mysql.connector

class LocalizationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Employee Job Titles - Ksawery Raszczak")
        self.create_widgets()
        self.populate_language_dropdown()
        self.db_connect()

    def db_connect(self):
        try:
            self.conn = mysql.connector.connect(
                user="gharm",
                password="gharm",
                host="localhost",
                database="assignment3",
                collation="utf8mb4_general_ci"
            )
            self.cursor = self.conn.cursor()
        except mysql.connector.Error as err:
            print(f"Error connecting to database: {err}")
            self.status_label.config(text=f"Database Connection Error: {err}")
            self.add_update_button['state'] = tk.DISABLED
            self.conn = None
            self.cursor = None

    def db_disconnect(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()

    def create_widgets(self):
        self.language_label = tk.Label(self.root, text="Select Language:")
        self.language_label.pack()

        self.language_combobox = ttk.Combobox(self.root, values=[])
        self.language_combobox.pack()
        self.language_combobox.bind("<<ComboboxSelected>>", self.update_display)

        self.display_frame = tk.Frame(self.root)
        self.display_frame.pack()

        self.key_name_label = tk.Label(self.root, text="Enter Key Name:")
        self.key_name_label.pack()
        self.key_name_entry = tk.Entry(self.root)
        self.key_name_entry.pack()

        self.translation_label = tk.Label(self.root, text="Enter Translation:")
        self.translation_label.pack()
        self.translation_entry = tk.Entry(self.root)
        self.translation_entry.pack()

        self.add_update_button = tk.Button(self.root, text="Add/Update Translation", command=self.add_or_update_translation)
        self.add_update_button.pack()

        self.status_label = tk.Label(self.root, text="")
        self.status_label.pack()

    def populate_language_dropdown(self):
        languages = ["en", "fr", "es", "zh"]
        self.language_combobox['values'] = languages
        self.language_combobox.set(languages[0])

    def update_display(self, event=None):
        self.clear_display()
        selected_language = self.language_combobox.get()
        translations = self.fetch_translations(selected_language)
        for key, translation in translations.items():
            tk.Label(self.display_frame, text=f"{key}: {translation}").pack()

    def clear_display(self):
        for widget in self.display_frame.winfo_children():
            widget.destroy()

    def fetch_translations(self, language_code):
        try:
            if self.conn:
                self.cursor.execute("SELECT key_name, translation_text FROM translations WHERE language_code=%s", (language_code,))
                results = self.cursor.fetchall()
                return {row[0]: row[1] for row in results}
            else:
                return {}
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            self.status_label.config(text=f"Database Error: {err}")
            return {}

    def add_or_update_translation(self):
        key_name = self.key_name_entry.get()
        translation_text = self.translation_entry.get()
        language_code = self.language_combobox.get()

        if key_name and translation_text and language_code:
            try:
                if self.conn:
                    self.cursor.execute(
                        "INSERT INTO translations (key_name, language_code, translation_text) VALUES (%s, %s, %s) "
                        "ON DUPLICATE KEY UPDATE translation_text=%s",
                        (key_name, language_code, translation_text, translation_text),
                    )
                    self.conn.commit()
                    self.status_label.config(text="Translation added/updated successfully.")
                    self.update_display()
                    self.clear_fields()
            except mysql.connector.Error as err:
                print(f"Database error: {err}")
                self.status_label.config(text=f"Database Error: {err}")
            finally:
                pass
        else:
            self.status_label.config(text="Please fill in all fields.")

    def clear_fields(self):
        self.key_name_entry.delete(0, tk.END)
        self.translation_entry.delete(0, tk.END)

    def __del__(self):
        try:
            if self.conn:
                self.db_disconnect()
        except Exception as e:
            print(f"Error in __del__: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LocalizationApp(root)
    root.mainloop()
