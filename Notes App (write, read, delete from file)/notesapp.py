import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import threading

class AdvancedNotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📒 AI-Style Advanced Notes App")
        self.root.geometry("850x550")
        self.root.configure(bg="#eaeaea")

        self.notes_dir = "notes"
        os.makedirs(self.notes_dir, exist_ok=True)
        self.notes = []

        self.theme = "light"
        self.auto_save = True

        self.create_widgets()
        self.load_notes()
        self.start_autosave()

    def create_widgets(self):
        # --- Menu ---
        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Change Notes Directory", command=self.change_directory)
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        theme_menu = tk.Menu(menu_bar, tearoff=0)
        theme_menu.add_command(label="Toggle Dark Mode", command=self.toggle_theme)
        menu_bar.add_cascade(label="View", menu=theme_menu)
        self.root.config(menu=menu_bar)

        # --- Top Section ---
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill=tk.X)

        ttk.Label(top_frame, text="Title:").pack(side=tk.LEFT, padx=(0, 5))
        self.title_entry = ttk.Entry(top_frame, width=40)
        self.title_entry.pack(side=tk.LEFT)

        ttk.Label(top_frame, text="Search:").pack(side=tk.LEFT, padx=(20, 5))
        self.search_entry = ttk.Entry(top_frame, width=30)
        self.search_entry.pack(side=tk.LEFT)
        self.search_entry.bind("<KeyRelease>", self.search_notes)

        # --- Paned Window ---
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # --- Notes List ---
        self.list_frame = ttk.Frame(paned, padding=10)
        paned.add(self.list_frame, weight=1)
        ttk.Label(self.list_frame, text="📋 Saved Notes", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.notes_listbox = tk.Listbox(self.list_frame, font=("Segoe UI", 10))
        self.notes_listbox.pack(fill=tk.BOTH, expand=True)
        self.notes_listbox.bind("<Double-Button-1>", lambda e: self.load_selected_note())

        # --- Text Editor ---
        self.editor_frame = ttk.Frame(paned, padding=10)
        paned.add(self.editor_frame, weight=3)
        ttk.Label(self.editor_frame, text="🖊️ Note Content", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.text_area = tk.Text(self.editor_frame, font=("Consolas", 11), wrap="word", height=20)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        self.text_area.bind("<KeyRelease>", self.update_status)

        # --- Buttons ---
        button_frame = ttk.Frame(self.root, padding=10)
        button_frame.pack(fill=tk.X)
        ttk.Button(button_frame, text="💾 Save", command=self.save_note).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📂 Load", command=self.load_selected_note).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Delete", command=self.delete_note).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🧹 Clear", command=self.clear_fields).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Refresh", command=self.load_notes).pack(side=tk.LEFT, padx=5)

        # --- Status Bar ---
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, anchor='w')
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def update_status(self, event=None):
        text = self.text_area.get("1.0", tk.END)
        words = len(text.split())
        chars = len(text.strip())
        self.status_var.set(f"Words: {words} | Characters: {chars}")

    def change_directory(self):
        folder = filedialog.askdirectory()
        if folder:
            self.notes_dir = folder
            self.load_notes()

    def toggle_theme(self):
        if self.theme == "light":
            self.text_area.config(bg="#1e1e1e", fg="white", insertbackground="white")
            self.notes_listbox.config(bg="#2e2e2e", fg="white")
            self.theme = "dark"
        else:
            self.text_area.config(bg="white", fg="black", insertbackground="black")
            self.notes_listbox.config(bg="white", fg="black")
            self.theme = "light"

    def load_notes(self):
        self.notes_listbox.delete(0, tk.END)
        self.notes = [f[:-4] for f in os.listdir(self.notes_dir) if f.endswith(".txt")]
        for note in sorted(self.notes):
            self.notes_listbox.insert(tk.END, note)

    def save_note(self):
        title = self.title_entry.get().strip()
        content = self.text_area.get("1.0", tk.END).strip()
        if not title or not content:
            messagebox.showwarning("Input Required", "Please provide both a title and content.")
            return

        filepath = os.path.join(self.notes_dir, f"{title}.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        self.status_var.set("✅ Note saved.")
        self.load_notes()

    def load_selected_note(self):
        selection = self.notes_listbox.curselection()
        if not selection:
            return

        title = self.notes_listbox.get(selection[0])
        filepath = os.path.join(self.notes_dir, f"{title}.txt")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, title)
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert(tk.END, content)
            self.status_var.set(f"📄 Loaded: {title}")

    def delete_note(self):
        selection = self.notes_listbox.curselection()
        if not selection:
            return
        title = self.notes_listbox.get(selection[0])
        confirm = messagebox.askyesno("Delete", f"Are you sure you want to delete '{title}'?")
        if confirm:
            os.remove(os.path.join(self.notes_dir, f"{title}.txt"))
            self.clear_fields()
            self.load_notes()
            self.status_var.set(f"🗑️ Deleted: {title}")

    def clear_fields(self):
        self.title_entry.delete(0, tk.END)
        self.text_area.delete("1.0", tk.END)
        self.notes_listbox.selection_clear(0, tk.END)
        self.status_var.set("Cleared")

    def search_notes(self, event=None):
        query = self.search_entry.get().lower()
        self.notes_listbox.delete(0, tk.END)
        for note in sorted(self.notes):
            if query in note.lower():
                self.notes_listbox.insert(tk.END, note)

    def start_autosave(self):
        def auto_save_task():
            while self.auto_save:
                self.root.after(5000, self.auto_draft_save)
        threading.Thread(target=auto_save_task, daemon=True).start()

    def auto_draft_save(self):
        title = self.title_entry.get().strip()
        content = self.text_area.get("1.0", tk.END).strip()
        if title and content:
            filepath = os.path.join(self.notes_dir, f"{title}_draft.txt")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            self.status_var.set("💾 Auto-saved draft.")

# --- Run App ---
if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedNotesApp(root)
    root.mainloop()
