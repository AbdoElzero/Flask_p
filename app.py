from flask import Flask, render_template, request, redirect, url_for, session, flash, g
import sqlite3
import os
import qrcode
import uuid

app = Flask(__name__)
application = app
app.secret_key = 'your_secret_key' 

DATABASE = 'reports.db'


QR_CODE_FOLDER = 'static/qrcodes'
if not os.path.exists(QR_CODE_FOLDER):
    os.makedirs(QR_CODE_FOLDER)


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row 
    return g.db

@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                national_id TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                field1 TEXT,
                field2 TEXT,
                field3 TEXT,
                field4 TEXT,
                field5 TEXT,
                field6 TEXT,
                field7 TEXT,
                field8 TEXT,
                field9 TEXT,
                field10 TEXT,
                field11 TEXT,
                field12 TEXT,
                field13 TEXT,
                field14 TEXT,
                field15 TEXT,
                field16 TEXT,
                report_id TEXT NOT NULL UNIQUE,
                qr_code_path TEXT NOT NULL,
                report_link TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        db.commit()


@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        national_id = request.form['national_id']
        password = request.form['password']

        db = get_db()
        cursor = db.cursor()

        
        cursor.execute('SELECT * FROM users WHERE national_id = ?', (national_id,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('⚠️ الرقم القومي مسجل بالفعل. الرجاء تسجيل الدخول.', 'error')
            return redirect(url_for('login'))

        
        cursor.execute('INSERT INTO users (national_id, password) VALUES (?, ?)', (national_id, password))
        db.commit()

        flash('✅ تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.', 'success')
        return redirect(url_for('home'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        national_id = request.form['national_id']
        password = request.form['password']

        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE national_id = ? AND password = ?', (national_id, password))
        user = cursor.fetchone()

        if user:
            session['user_id'] = user['id']
            return redirect(url_for('home'))
        else:
            flash('الرقم القومي أو كلمة المرور غير صحيحة', 'error')

    return render_template('login.html')

@app.route('/home')
def home():
    if 'user_id' not in session: 
        return redirect(url_for('login'))
    return render_template('home.html') 


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))



@app.route('/create_report', methods=['GET', 'POST'])
def create_report():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        fields = [request.form.get(f'field{i}', '') for i in range(1, 17)]

       
        report_id = str(uuid.uuid4())

        
        report_link = f"http://127.0.0.1:5000/report/{report_id}"

      
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(report_link)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')

        
        qr_code_path = os.path.join(QR_CODE_FOLDER, f"{report_id}.png")
        img.save(qr_code_path)

        
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO reports (user_id, field1, field2, field3, field4, field5, field6, field7, field8, field9, field10, field11, field12, field13, field14, field15, field16, report_id, qr_code_path, report_link)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], *fields, report_id, qr_code_path, report_link))
        db.commit()

        return redirect(url_for('show_report', report_id=report_id))

    return render_template('create_report.html')
@app.route('/saved_reports')
def saved_reports():
    if 'user_id' not in session:
        return redirect(url_for('login'))  

    db = get_db()
    cursor = db.cursor()
    

    cursor.execute('SELECT * FROM reports WHERE user_id = ?', (session['user_id'],))
    reports = cursor.fetchall()

    return render_template('saved_reports.html', reports=reports)


@app.route('/show_report/<report_id>')
def show_report(report_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT * FROM reports WHERE id = ?', (report_id,))
    report = cursor.fetchone()
    
    if not report:
        return redirect(url_for('saved_reports'))
    
    return render_template('show_report.html', report=report)

@app.route('/edit_report/<int:report_id>', methods=['GET', 'POST'])
def edit_report(report_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        field1 = request.form['field1']
        field2 = request.form['field2']
        field3 = request.form['field3']
        field4 = request.form['field4']
        field5 = request.form['field5']
        field6 = request.form['field6']
        field7 = request.form['field7']
        field8 = request.form['field8']
        field9 = request.form['field9']
        field10 = request.form['field10']
        field11 = request.form['field11']
        field12 = request.form['field12']
        field13 = request.form['field13']
        field14 = request.form['field14']
        field15 = request.form['field15']
        field16 = request.form['field16']

       
        cursor.execute('''
            UPDATE reports 
            SET field1 = ?, field2 = ?, field3 = ?, field4 = ?, field5 = ?, field6 = ?, field7 = ?, field8 = ?, field9 = ?, field10 = ?, field11 = ?, field12 = ?, field13 = ?, field14 = ?, field15 = ?, field16 = ?
            WHERE id = ?
        ''', (field1, field2, field3, field4, field5, field6, field7, field8, field9, field10, field11, field12, field13, field14, field15, field16, report_id))
        db.commit()
        flash('تم تحديث التقرير بنجاح', 'success')
        return redirect(url_for('show_report', report_id=report_id))

   
    cursor.execute('SELECT * FROM reports WHERE id = ?', (report_id,))
    report = cursor.fetchone()
    return render_template('edit_report.html', report=report)

@app.route('/delete_report/<int:report_id>', methods=['POST'])
def delete_report(report_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()

    cursor.execute('DELETE FROM reports WHERE id = ?', (report_id,))
    db.commit()
    flash('تم حذف التقرير بنجاح', 'success')
    return redirect(url_for('saved_reports'))

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)