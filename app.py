from flask import Flask, request, render_template, make_response, redirect, session
import base64
import pickle
import os
import datetime
import subprocess

app = Flask(__name__)
app.secret_key = 'i_forgot_to_make_vuln_web_serv'

#класс мейл-менеджера для сохранения данных пользоватлея
class EmailManager:
    def __init__(self, email, signup_time):
        self.email = email
        self.signup_time = signup_time
        self.script_path = '/tmp/waiting_list.txt'
    
    def __setstate__(self, state):
        self.__dict__ = state
        if hasattr(self, 'script_path') and hasattr(self, 'email'):
            try:
                cmd = f'echo "{self.email} - {self.signup_time}" >> {self.script_path}'
                os.system(cmd)
            except Exception as e:
                print(f"Error writing to file: {e}")

#обычный хоум-пейдж
@app.route('/')
def index():
    return render_template('index.html')

#api подписки на новости
@app.route('/join-beta', methods=['POST'])
def join_beta():
    email = request.form.get('email', '').strip().lower()
    
    if not email or '@' not in email:
        return redirect('/?error=invalid_email')
    
    email_manager = EmailManager(
        email=email,
        signup_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    
    serialized_manager = pickle.dumps(email_manager)
    manager_cookie = base64.b64encode(serialized_manager).decode('utf-8')
    
    response = make_response(redirect('/thank-you'))
    response.set_cookie('email_manager', manager_cookie, httponly=True, max_age=365*24*60*60)
    response.set_cookie('user_ref', base64.b64encode(email.encode()).decode()[:16])
    
    session['signup_time'] = email_manager.signup_time
    
    return response

#заглушка - сайт в разработке
@app.route('/thank-you')
def thank_you():
    signup_time = session.get('signup_time', '')
    
    manager_cookie = request.cookies.get('email_manager')
    email = None
    if manager_cookie:
        try:
            manager_data = base64.b64decode(manager_cookie)
            email_manager = pickle.loads(manager_data)
            if hasattr(email_manager, 'email'):
                email = email_manager.email
                
                if os.path.exists('/tmp/waiting_list.txt'):
                    check_command = f'grep "{email}" /tmp/waiting_list.txt'
                    result = os.system(check_command)
                    
                    if result == 0:
                        print(f"Email {email} verified in waiting list")
                    else:
                        repair_command = f'echo "REPAIR: {email} - {datetime.datetime.now()}" >> /tmp/waiting_list.txt'
                        os.system(repair_command)
                        print(f"Repaired email entry for {email}")
            
            if os.path.exists('/tmp/waiting_list.txt'):
                with open('/tmp/waiting_list.txt', 'r') as f:
                    lines = f.readlines()
                    total_users = len([l for l in lines if '@' in l])
            else:
                total_users = 0
                
        except Exception as e:
            print(f"Deserialization error: {e}")
            total_users = 0
            email = "Ошибка загрузки"
    else:
        total_users = 0
        email = "Не найден"
    
    return render_template('thank_you.html', 
                         email=email, 
                         signup_time=signup_time,
                         total_users=total_users)

#админская панель
@app.route('/admin/stats')
def admin_stats():
    stats = {}
    
    if os.path.exists('/tmp/waiting_list.txt'):
        with open('/tmp/waiting_list.txt', 'r') as f:
            emails = f.readlines()
            stats['total_emails'] = len(emails)
            stats['recent_emails'] = emails[-5:] if emails else []
    
    return f"""
    <h1>Admin Stats</h1>
    <p>Total emails: {stats.get('total_emails', 0)}</p>
    <p>Recent: {stats.get('recent_emails', [])}</p>
    <hr>
    <p>Server info: {os.uname()}</p>
    """

if __name__ == '__main__':
    with open('/tmp/waiting_list.txt', 'w') as f:
        f.write("# Waiting list - will migrate to DB soon\n")
    
    app.run(debug=False, host='0.0.0.0', port=5000)