"""
=============================================================
  Sierra Leone School Student Record System
  Limkokwing University – Principles of Structured Programming
  SDG 4: Quality Education
=============================================================
  Author  : [Your Name]
  Student : [Your Student ID]
  Date    : June 2026
  Tool    : Python 3 + tkinter (GUI)
=============================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

# ─────────────────────────────────────────────
#  DATA FILE
# ─────────────────────────────────────────────
DATA_FILE = "students.json"


# ─────────────────────────────────────────────
#  DATA FUNCTIONS  (backend / logic layer)
# ─────────────────────────────────────────────

def load_students():
    """Load all student records from the JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []


def save_students(students):
    """Save all student records to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(students, f, indent=4)


def generate_id(students):
    """Generate a unique student ID."""
    if not students:
        return "SL-0001"
    last_id = students[-1]["id"]
    number = int(last_id.split("-")[1]) + 1
    return f"SL-{number:04d}"


def add_student(students, name, age, gender, grade, district, guardian, contact):
    """Add a new student record."""
    student = {
        "id": generate_id(students),
        "name": name.strip().title(),
        "age": age,
        "gender": gender,
        "grade": grade,
        "district": district,
        "guardian": guardian.strip().title(),
        "contact": contact.strip(),
        "enrolled": datetime.now().strftime("%Y-%m-%d"),
        "scores": {}
    }
    students.append(student)
    save_students(students)
    return student


def delete_student(students, student_id):
    """Remove a student by ID."""
    updated = [s for s in students if s["id"] != student_id]
    save_students(updated)
    return updated


def search_students(students, query):
    """Search students by name, ID, or district."""
    query = query.lower()
    return [
        s for s in students
        if query in s["name"].lower()
        or query in s["id"].lower()
        or query in s["district"].lower()
    ]


def update_scores(students, student_id, subject, score):
    """Add or update a subject score for a student."""
    for s in students:
        if s["id"] == student_id:
            s["scores"][subject] = score
    save_students(students)


def calculate_average(scores):
    """Calculate average score from a dict of scores."""
    if not scores:
        return 0.0
    return sum(scores.values()) / len(scores)


def get_grade_letter(average):
    """Convert numeric average to a letter grade."""
    if average >= 90:
        return "A+"
    elif average >= 80:
        return "A"
    elif average >= 70:
        return "B"
    elif average >= 60:
        return "C"
    elif average >= 50:
        return "D"
    else:
        return "F"


def get_statistics(students):
    """Compute overall system statistics."""
    total = len(students)
    if total == 0:
        return {"total": 0, "male": 0, "female": 0, "avg_score": 0.0, "districts": {}}

    male = sum(1 for s in students if s["gender"] == "Male")
    female = total - male

    averages = []
    for s in students:
        if s["scores"]:
            averages.append(calculate_average(s["scores"]))

    avg_score = sum(averages) / len(averages) if averages else 0.0

    districts = {}
    for s in students:
        d = s["district"]
        districts[d] = districts.get(d, 0) + 1

    return {
        "total": total,
        "male": male,
        "female": female,
        "avg_score": round(avg_score, 2),
        "districts": districts
    }


# ─────────────────────────────────────────────
#  COLOUR & FONT CONSTANTS
# ─────────────────────────────────────────────
BG         = "#F0F4F8"
SIDEBAR_BG = "#1A3C5E"        # deep navy – Sierra Leone blue
ACCENT     = "#2ECC71"        # green – SDG education colour
ACCENT2    = "#E74C3C"        # red – danger / delete
WHITE      = "#FFFFFF"
TEXT_DARK  = "#1C2B3A"
TEXT_LIGHT = "#FFFFFF"
HEADER_BG  = "#154360"
ROW_ODD    = "#EAF2FB"
ROW_EVEN   = "#FFFFFF"

FONT_TITLE  = ("Helvetica", 22, "bold")
FONT_H2     = ("Helvetica", 14, "bold")
FONT_BODY   = ("Helvetica", 11)
FONT_SMALL  = ("Helvetica", 9)
FONT_BUTTON = ("Helvetica", 11, "bold")
FONT_SIDEBAR= ("Helvetica", 12, "bold")


# ─────────────────────────────────────────────
#  MAIN APPLICATION CLASS
# ─────────────────────────────────────────────

class StudentRecordApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sierra Leone School Student Record System")
        self.root.geometry("1100x680")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)

        self.students = load_students()
        self.current_frame = None

        self._build_layout()
        self.show_dashboard()

    # ── LAYOUT ────────────────────────────────

    def _build_layout(self):
        """Build the fixed sidebar + content area."""
        # Sidebar
        self.sidebar = tk.Frame(self.root, bg=SIDEBAR_BG, width=210)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # App title in sidebar
        tk.Label(
            self.sidebar,
            text="🎓 SL School\nRecord System",
            bg=SIDEBAR_BG, fg=WHITE,
            font=("Helvetica", 13, "bold"),
            justify="center", pady=20
        ).pack(fill="x")

        tk.Frame(self.sidebar, bg=ACCENT, height=2).pack(fill="x", padx=20)

        # Navigation buttons
        nav_items = [
            ("📊  Dashboard",       self.show_dashboard),
            ("➕  Add Student",     self.show_add_student),
            ("📋  View Records",    self.show_records),
            ("🔍  Search",          self.show_search),
            ("📝  Update Scores",   self.show_scores),
            ("📈  Statistics",      self.show_statistics),
        ]

        for label, cmd in nav_items:
            btn = tk.Button(
                self.sidebar, text=label,
                bg=SIDEBAR_BG, fg=WHITE,
                font=FONT_SIDEBAR,
                relief="flat", anchor="w",
                padx=20, pady=12,
                activebackground=ACCENT,
                activeforeground=WHITE,
                cursor="hand2",
                command=cmd
            )
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#1F5080"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=SIDEBAR_BG))

        # SDG badge at bottom
        tk.Frame(self.sidebar, bg=SIDEBAR_BG).pack(expand=True, fill="y")
        tk.Label(
            self.sidebar,
            text="🌍 Aligned with\nSDG 4: Quality Education",
            bg=SIDEBAR_BG, fg="#AED6F1",
            font=FONT_SMALL, justify="center", pady=14
        ).pack(fill="x")

        # Content area
        self.content = tk.Frame(self.root, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

    def _clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def _header(self, title, subtitle=""):
        frame = tk.Frame(self.content, bg=HEADER_BG, pady=18)
        frame.pack(fill="x")
        tk.Label(frame, text=title, bg=HEADER_BG, fg=WHITE,
                 font=FONT_TITLE).pack()
        if subtitle:
            tk.Label(frame, text=subtitle, bg=HEADER_BG, fg="#AED6F1",
                     font=FONT_BODY).pack()

    # ── DASHBOARD ─────────────────────────────

    def show_dashboard(self):
        self._clear_content()
        self._header("Welcome to SL Student Record System",
                     "Supporting Quality Education in Sierra Leone")

        stats = get_statistics(self.students)

        card_frame = tk.Frame(self.content, bg=BG, pady=20)
        card_frame.pack(fill="x", padx=30)

        cards = [
            ("Total Students", stats["total"], "👨‍🎓", ACCENT),
            ("Male Students",  stats["male"],  "👦",  "#2980B9"),
            ("Female Students",stats["female"],"👧",  "#8E44AD"),
            ("Avg Score",      f"{stats['avg_score']}%", "📊", "#E67E22"),
        ]

        for i, (label, value, icon, color) in enumerate(cards):
            card = tk.Frame(card_frame, bg=WHITE, relief="flat",
                            highlightbackground=color, highlightthickness=2,
                            padx=20, pady=16, width=180)
            card.grid(row=0, column=i, padx=12, pady=8)
            card.grid_propagate(False)
            tk.Label(card, text=icon, bg=WHITE, font=("Helvetica", 28)).pack()
            tk.Label(card, text=str(value), bg=WHITE,
                     fg=color, font=("Helvetica", 20, "bold")).pack()
            tk.Label(card, text=label, bg=WHITE,
                     fg=TEXT_DARK, font=FONT_SMALL).pack()

        # Recent registrations
        tk.Label(self.content, text="Recent Registrations",
                 bg=BG, fg=TEXT_DARK, font=FONT_H2).pack(anchor="w", padx=30, pady=(20, 5))

        recent_frame = tk.Frame(self.content, bg=WHITE, relief="flat",
                                highlightbackground="#D5D8DC", highlightthickness=1)
        recent_frame.pack(fill="x", padx=30, pady=5)

        headers = ["ID", "Name", "Grade", "District", "Enrolled"]
        for col, h in enumerate(headers):
            tk.Label(recent_frame, text=h, bg=SIDEBAR_BG, fg=WHITE,
                     font=("Helvetica", 10, "bold"), padx=10, pady=6,
                     anchor="w").grid(row=0, column=col, sticky="ew", padx=1)
            recent_frame.columnconfigure(col, weight=1)

        recent = self.students[-5:][::-1]
        for row, s in enumerate(recent, start=1):
            bg = ROW_ODD if row % 2 == 0 else ROW_EVEN
            for col, val in enumerate([s["id"], s["name"], s["grade"],
                                        s["district"], s["enrolled"]]):
                tk.Label(recent_frame, text=val, bg=bg, fg=TEXT_DARK,
                         font=FONT_BODY, padx=10, pady=5,
                         anchor="w").grid(row=row, column=col, sticky="ew", padx=1)

        if not recent:
            tk.Label(recent_frame, text="No students registered yet.",
                     bg=WHITE, fg="gray", font=FONT_BODY,
                     pady=12).grid(row=1, column=0, columnspan=5)

    # ── ADD STUDENT ───────────────────────────

    def show_add_student(self):
        self._clear_content()
        self._header("Add New Student", "Register a new student into the system")

        form = tk.Frame(self.content, bg=BG, padx=40, pady=20)
        form.pack(fill="both", expand=True)

        districts = ["Western Area Urban", "Western Area Rural",
                     "Bo", "Kenema", "Makeni", "Kono",
                     "Kailahun", "Pujehun", "Bonthe", "Tonkolili", "Kambia", "Port Loko"]

        grades = ["Grade 1", "Grade 2", "Grade 3", "Grade 4",
                  "Grade 5", "Grade 6", "JSS 1", "JSS 2", "JSS 3",
                  "SSS 1", "SSS 2", "SSS 3"]

        fields = [
            ("Full Name",         "entry",    None),
            ("Age",               "entry",    None),
            ("Gender",            "combo",    ["Male", "Female"]),
            ("Grade / Class",     "combo",    grades),
            ("District",          "combo",    districts),
            ("Guardian Name",     "entry",    None),
            ("Contact Number",    "entry",    None),
        ]

        self.add_vars = {}

        for row, (label, ftype, options) in enumerate(fields):
            tk.Label(form, text=label + ":", bg=BG, fg=TEXT_DARK,
                     font=FONT_BODY, anchor="w").grid(
                row=row, column=0, sticky="w", pady=8, padx=(0, 20))

            if ftype == "entry":
                var = tk.StringVar()
                widget = tk.Entry(form, textvariable=var, font=FONT_BODY,
                                  width=34, relief="solid", bd=1)
            else:
                var = tk.StringVar(value=options[0])
                widget = ttk.Combobox(form, textvariable=var,
                                      values=options, state="readonly",
                                      font=FONT_BODY, width=32)

            widget.grid(row=row, column=1, sticky="w", pady=8)
            self.add_vars[label] = var

        # Submit button
        def submit():
            name     = self.add_vars["Full Name"].get().strip()
            age      = self.add_vars["Age"].get().strip()
            gender   = self.add_vars["Gender"].get()
            grade    = self.add_vars["Grade / Class"].get()
            district = self.add_vars["District"].get()
            guardian = self.add_vars["Guardian Name"].get().strip()
            contact  = self.add_vars["Contact Number"].get().strip()

            if not name or not age or not guardian or not contact:
                messagebox.showerror("Missing Fields",
                                     "Please fill in all required fields.")
                return
            if not age.isdigit() or not (4 <= int(age) <= 25):
                messagebox.showerror("Invalid Age",
                                     "Age must be a number between 4 and 25.")
                return

            student = add_student(self.students, name, int(age), gender,
                                  grade, district, guardian, contact)
            self.students = load_students()
            messagebox.showinfo("Success",
                                f"Student registered!\nID: {student['id']}")
            self.show_dashboard()

        tk.Button(form, text="  ✔  Register Student  ",
                  bg=ACCENT, fg=WHITE, font=FONT_BUTTON,
                  relief="flat", padx=10, pady=8,
                  activebackground="#27AE60", cursor="hand2",
                  command=submit).grid(row=len(fields), column=1,
                                       sticky="w", pady=20)

    # ── VIEW RECORDS ──────────────────────────

    def show_records(self):
        self._clear_content()
        self._header("All Student Records", f"Total: {len(self.students)} students")

        # Scrollable table
        container = tk.Frame(self.content, bg=BG)
        container.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("ID", "Name", "Age", "Gender", "Grade", "District", "Enrolled")
        tree = ttk.Treeview(container, columns=columns, show="headings", height=22)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", background=SIDEBAR_BG,
                        foreground=WHITE, font=("Helvetica", 10, "bold"))
        style.configure("Treeview", rowheight=28, font=FONT_BODY,
                        background=WHITE, fieldbackground=WHITE)
        style.map("Treeview", background=[("selected", ACCENT)])

        widths = [80, 180, 50, 80, 90, 160, 100]
        for col, w in zip(columns, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="w")

        tree.tag_configure("odd",  background=ROW_ODD)
        tree.tag_configure("even", background=ROW_EVEN)

        for i, s in enumerate(self.students):
            tag = "odd" if i % 2 == 0 else "even"
            tree.insert("", "end", iid=s["id"],
                        values=(s["id"], s["name"], s["age"], s["gender"],
                                s["grade"], s["district"], s["enrolled"]),
                        tags=(tag,))

        scroll_y = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll_y.set)
        scroll_y.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        # Delete selected
        def delete_selected():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("No Selection", "Please select a student to delete.")
                return
            sid = sel[0]
            name = tree.item(sid)["values"][1]
            if messagebox.askyesno("Confirm Delete",
                                   f"Delete student {name} ({sid})?\nThis cannot be undone."):
                self.students = delete_student(self.students, sid)
                self.show_records()

        btn_frame = tk.Frame(self.content, bg=BG)
        btn_frame.pack(fill="x", padx=20, pady=6)
        tk.Button(btn_frame, text="🗑  Delete Selected",
                  bg=ACCENT2, fg=WHITE, font=FONT_BUTTON,
                  relief="flat", padx=10, pady=6,
                  activebackground="#C0392B", cursor="hand2",
                  command=delete_selected).pack(side="left")

    # ── SEARCH ────────────────────────────────

    def show_search(self):
        self._clear_content()
        self._header("Search Students", "Search by name, ID, or district")

        top = tk.Frame(self.content, bg=BG, pady=16)
        top.pack(fill="x", padx=30)

        self.search_var = tk.StringVar()
        entry = tk.Entry(top, textvariable=self.search_var, font=("Helvetica", 13),
                         width=38, relief="solid", bd=1)
        entry.pack(side="left", ipady=6)
        entry.bind("<Return>", lambda e: do_search())

        tk.Button(top, text="  🔍 Search  ",
                  bg=SIDEBAR_BG, fg=WHITE, font=FONT_BUTTON,
                  relief="flat", padx=8, pady=6, cursor="hand2",
                  command=lambda: do_search()).pack(side="left", padx=10)

        result_frame = tk.Frame(self.content, bg=BG)
        result_frame.pack(fill="both", expand=True, padx=20)

        def do_search():
            for w in result_frame.winfo_children():
                w.destroy()
            query = self.search_var.get().strip()
            if not query:
                messagebox.showwarning("Empty Query", "Please enter a search term.")
                return
            results = search_students(self.students, query)
            tk.Label(result_frame, text=f"{len(results)} result(s) found",
                     bg=BG, fg=TEXT_DARK, font=FONT_H2).pack(anchor="w", pady=(6, 4))

            columns = ("ID", "Name", "Age", "Grade", "District", "Guardian")
            tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=14)
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=140, anchor="w")
            for s in results:
                tree.insert("", "end", values=(
                    s["id"], s["name"], s["age"],
                    s["grade"], s["district"], s["guardian"]))
            tree.pack(fill="both", expand=True, pady=6)

    # ── UPDATE SCORES ─────────────────────────

    def show_scores(self):
        self._clear_content()
        self._header("Update Student Scores", "Enter subject marks for a student")

        form = tk.Frame(self.content, bg=BG, padx=40, pady=20)
        form.pack(fill="both", expand=True)

        subjects = ["Mathematics", "English", "Science", "Social Studies",
                    "ICT", "Agriculture", "Civics"]

        # Student ID selection
        tk.Label(form, text="Student ID:", bg=BG, fg=TEXT_DARK,
                 font=FONT_BODY).grid(row=0, column=0, sticky="w", pady=8)
        ids = [s["id"] + " – " + s["name"] for s in self.students]
        id_var = tk.StringVar(value=ids[0] if ids else "")
        id_combo = ttk.Combobox(form, textvariable=id_var, values=ids,
                                state="readonly", font=FONT_BODY, width=38)
        id_combo.grid(row=0, column=1, sticky="w", pady=8)

        score_vars = {}
        for row, subject in enumerate(subjects, start=1):
            tk.Label(form, text=subject + ":", bg=BG, fg=TEXT_DARK,
                     font=FONT_BODY).grid(row=row, column=0, sticky="w", pady=6)
            var = tk.StringVar()
            tk.Entry(form, textvariable=var, font=FONT_BODY,
                     width=10, relief="solid", bd=1).grid(row=row, column=1, sticky="w")
            score_vars[subject] = var

        def load_existing(*args):
            """Pre-fill scores if student already has them."""
            sel = id_var.get()
            if not sel:
                return
            sid = sel.split(" – ")[0]
            for s in self.students:
                if s["id"] == sid:
                    for subj, var in score_vars.items():
                        var.set(str(s["scores"].get(subj, "")))
                    break

        id_combo.bind("<<ComboboxSelected>>", load_existing)

        def save_scores():
            sel = id_var.get()
            if not sel:
                messagebox.showwarning("No Student", "Please select a student.")
                return
            sid = sel.split(" – ")[0]
            errors = []
            for subj, var in score_vars.items():
                val = var.get().strip()
                if val == "":
                    continue
                if not val.replace(".", "", 1).isdigit() or not (0 <= float(val) <= 100):
                    errors.append(subj)
                    continue
                update_scores(self.students, sid, subj, float(val))

            if errors:
                messagebox.showerror("Invalid Score",
                                     f"Scores must be 0–100.\nInvalid: {', '.join(errors)}")
                return

            self.students = load_students()
            for s in self.students:
                if s["id"] == sid:
                    avg = calculate_average(s["scores"])
                    letter = get_grade_letter(avg)
                    messagebox.showinfo("Scores Saved",
                                       f"Scores updated for {s['name']}!\n"
                                       f"Average: {avg:.1f}% — Grade: {letter}")
                    break

        row_count = len(subjects) + 1
        tk.Button(form, text="  ✔  Save Scores  ",
                  bg=ACCENT, fg=WHITE, font=FONT_BUTTON,
                  relief="flat", padx=10, pady=8,
                  activebackground="#27AE60", cursor="hand2",
                  command=save_scores).grid(row=row_count, column=1,
                                            sticky="w", pady=20)

    # ── STATISTICS ────────────────────────────

    def show_statistics(self):
        self._clear_content()
        self._header("System Statistics", "Overview of school enrolment and performance")

        stats = get_statistics(self.students)

        frame = tk.Frame(self.content, bg=BG, padx=40, pady=20)
        frame.pack(fill="both", expand=True)

        # Summary box
        summary = tk.Frame(frame, bg=WHITE, relief="flat",
                           highlightbackground="#D5D8DC", highlightthickness=1,
                           padx=20, pady=16)
        summary.pack(fill="x", pady=10)
        tk.Label(summary, text="Enrolment Summary",
                 bg=WHITE, fg=SIDEBAR_BG, font=FONT_H2).pack(anchor="w")
        tk.Label(summary, text=f"Total Students   :  {stats['total']}",
                 bg=WHITE, fg=TEXT_DARK, font=FONT_BODY).pack(anchor="w", pady=2)
        tk.Label(summary, text=f"Male Students    :  {stats['male']}",
                 bg=WHITE, fg=TEXT_DARK, font=FONT_BODY).pack(anchor="w", pady=2)
        tk.Label(summary, text=f"Female Students  :  {stats['female']}",
                 bg=WHITE, fg=TEXT_DARK, font=FONT_BODY).pack(anchor="w", pady=2)
        tk.Label(summary, text=f"Overall Average  :  {stats['avg_score']}%",
                 bg=WHITE, fg=ACCENT, font=("Helvetica", 12, "bold")).pack(anchor="w", pady=2)

        # District breakdown
        tk.Label(frame, text="Students by District",
                 bg=BG, fg=TEXT_DARK, font=FONT_H2).pack(anchor="w", pady=(16, 4))

        dist_frame = tk.Frame(frame, bg=WHITE, relief="flat",
                              highlightbackground="#D5D8DC", highlightthickness=1)
        dist_frame.pack(fill="x")

        if stats["districts"]:
            for row, (district, count) in enumerate(
                    sorted(stats["districts"].items(), key=lambda x: -x[1])):
                bg = ROW_ODD if row % 2 == 0 else ROW_EVEN
                tk.Label(dist_frame, text=district, bg=bg, fg=TEXT_DARK,
                         font=FONT_BODY, padx=16, pady=6,
                         anchor="w").grid(row=row, column=0, sticky="ew")
                # simple bar
                bar_len = max(4, count * 20)
                bar = tk.Frame(dist_frame, bg=ACCENT, width=bar_len, height=14)
                bar.grid(row=row, column=1, sticky="w", padx=8)
                tk.Label(dist_frame, text=str(count), bg=bg, fg=TEXT_DARK,
                         font=FONT_BODY).grid(row=row, column=2, padx=10)
                dist_frame.columnconfigure(0, weight=1)
        else:
            tk.Label(dist_frame, text="No data yet.",
                     bg=WHITE, fg="gray", font=FONT_BODY,
                     pady=10).pack()

        # Per-student performance table
        tk.Label(frame, text="Student Performance",
                 bg=BG, fg=TEXT_DARK, font=FONT_H2).pack(anchor="w", pady=(16, 4))

        cols = ("ID", "Name", "Subjects Taken", "Average (%)", "Grade")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=8)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor="center")

        for s in self.students:
            avg = calculate_average(s["scores"])
            letter = get_grade_letter(avg) if s["scores"] else "—"
            avg_str = f"{avg:.1f}" if s["scores"] else "—"
            tree.insert("", "end", values=(
                s["id"], s["name"], len(s["scores"]), avg_str, letter))

        tree.pack(fill="x")


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentRecordApp(root)
    root.mainloop()