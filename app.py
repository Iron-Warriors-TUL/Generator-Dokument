import os
import subprocess
import pandas as pd
import unicodedata # NEW: For handling Polish characters in filenames
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = 'change_this_to_something_secret'

# --- CONFIG ---
TEMPLATE_DIR = "latex_templates"
OUTPUT_DIR = "generated"

# --- HELPER: CLEAN FILENAMES ---
def safe_filename(text):
    """
    Converts 'Anna Kowalska' to 'Anna_Kowalska'
    Converts 'Michał Żółkiewski' to 'Michal_Zolkiewski'
    """
    # Normalize unicode characters (turn ł -> l, ń -> n, etc.)
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    # Replace spaces with underscores
    text = text.replace(' ', '_')
    # Remove any other characters that aren't letters, numbers, or underscores
    return "".join([c for c in text if c.isalnum() or c == '_'])

def get_latex_env():
    import jinja2
    template_loader = jinja2.FileSystemLoader(searchpath=TEMPLATE_DIR)
    return jinja2.Environment(
        loader=template_loader,
        block_start_string='\BLOCK{',
        block_end_string='}',
        variable_start_string='\VAR{',
        variable_end_string='}',
        comment_start_string='\#{',
        comment_end_string='}',
        autoescape=False
    )

# --- AUTH ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id == 'admin': return User(user_id)
    return None

# --- ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin':
            login_user(User('admin'))
            return redirect(url_for('dashboard'))
        flash('Błędne dane (admin/admin)')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    # 1. Load Students
    try:
        df_students = pd.read_csv('students.csv')
        students = df_students.to_dict(orient='records')
    except FileNotFoundError:
        students = []
        flash("Brakuje pliku students.csv!")

    # 2. Load Signers
    try:
        df_signers = pd.read_csv('signers.csv')
        signers = df_signers.to_dict(orient='records')
    except FileNotFoundError:
        signers = []

    # 3. Load Templates
    try:
        files = os.listdir(TEMPLATE_DIR)
        templates = [f for f in files if f.endswith('.tex')]
    except FileNotFoundError:
        templates = []
        os.makedirs(TEMPLATE_DIR, exist_ok=True)

    return render_template('dashboard.html', 
                         students=students, 
                         signers=signers, 
                         templates=templates)

@app.route('/generate_custom', methods=['POST'])
@login_required
def generate_custom():
    # 1. Gather Form Data
    student_id = int(request.form['student_id'])
    template_filename = request.form['template_name'] # e.g., "civic.tex"
    
    signer_left_id = int(request.form['signer_left'])
    signer_right_id = int(request.form['signer_right'])

    # 2. Find Student
    df_students = pd.read_csv('students.csv')
    student_data = df_students[df_students['id'] == student_id]
    if student_data.empty: return "Student not found", 404
    student = student_data.iloc[0].to_dict()

    # 3. Find Signers
    df_signers = pd.read_csv('signers.csv')
    
    # Left Signer
    s_left = df_signers[df_signers['id'] == signer_left_id].iloc[0]
    student['signer_left_name'] = s_left['name']
    student['signer_left_role'] = s_left['role']
    
    # Right Signer
    s_right = df_signers[df_signers['id'] == signer_right_id].iloc[0]
    student['signer_right_name'] = s_right['name']
    student['signer_right_role'] = s_right['role']

    # Add Timestamp
    student['timestamp'] = datetime.now().strftime("%d.%m.%Y")

    # 4. Render LaTeX
    latex_env = get_latex_env()
    try:
        template = latex_env.get_template(template_filename)
        rendered_tex = template.render(**student)
    except Exception as e:
        return f"Template Error: {e}", 500

    # --- 5. CREATE CUSTOM FILENAME ---
    # Logic: Name_Surname_Index_DocType.pdf
    
    clean_name = safe_filename(student['name'])   # Anna Kowalska -> Anna_Kowalska
    clean_index = str(student['index'])           # 123456
    doc_type = template_filename.replace('.tex', '') # civic.tex -> civic
    
    # Final name: Anna_Kowalska_123456_civic
    base_filename = f"{clean_name}_{clean_index}_{doc_type}"
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    tex_path = os.path.join(OUTPUT_DIR, f"{base_filename}.tex")
    
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(rendered_tex)

    try:
        # Compile twice
        for _ in range(2):
            subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', '-output-directory', OUTPUT_DIR, tex_path],
                check=True, stdout=subprocess.DEVNULL
            )
        
        pdf_path = os.path.join(OUTPUT_DIR, f"{base_filename}.pdf")
        
        # Send file with the specific download name
        return send_file(pdf_path, as_attachment=True, download_name=f"{base_filename}.pdf")
        
    except Exception as e:
        return f"Compilation Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)