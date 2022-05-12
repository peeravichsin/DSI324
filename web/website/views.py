from flask import Blueprint, Flask, redirect, render_template, request, flash, session, url_for
from .auth import login_is_required
from website import auth
from flask_mysqldb import  MySQLdb
from . import mysql
import ast


views = Blueprint('views', __name__)


# Default home
@views.route("/")
def home():
    return render_template('home.html')





# Enroll
@views.route("/enroll", methods =['GET','POST'])
def enroll():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    user_id = auth.session["google_id"]
    if user_id:
        cur.execute(f'select * from student where user_id = {user_id}')
        student = cur.fetchone()      
    s_id = request.form.get("enroll_sem")
    p_id = 'DSP'+str(s_id)
    enrolled_list = []
    sp = []
    cur.execute('select * from study_plan')
    study_plans = cur.fetchall()
    for study_plan in study_plans:
        sp.append(study_plan)
    for i in range(len(sp)):
        if int(student["study_year"]) > int(str(sp[i]["studyplan_id"])[3:4]):
            x = []
            p = '1'
            x.append(sp[i]["studyplan_id"])
            x.append(p)
            enrolled_list.append(x)
        else:
            x = []
            p = '0'
            x.append(sp[i]["studyplan_id"])
            x.append(p)
            enrolled_list.append(x)
    print(enrolled_list)        
    # print(f'{p_id} (p_id) ')
    if p_id != 'DSPNone' and p_id != 'DSP':
        cur.execute(f'select * from study_plan where studyplan_id = "{p_id}"')
    plans = cur.fetchone()
    module_id = request.form.get("module_id")

    
    year = []
    modules = ''
    
# Decode id to Understandable text

    if s_id is not None:
        for i in str(s_id):
            if i == "S":
                i = "ภาคฤดูร้อน"
                year.append(i)
            else:
                year.append(i)

    if module_id is not None:
        if module_id == '3':
            modules = "Actuarial Analytics"
        elif module_id == '4':
            modules = "Artificial Intelligence"
        elif module_id == '5':
            modules = "Digital Forensic"
        elif module_id == '6':
            modules = "Digital Transformation"
        elif module_id == '7':
            modules = "Health Informatics"

# Decode id to Understandable text

    plan_list = []
    if plans is not None:
        if p_id != "DSP41" and module_id != "":
           modules = None
           year = None
           flash('อ่ะ..จ๊ะเอ๋ตัวเอง!! ก็เขียนบอกอยู่ว่าของปี 4 เทอม 1', category='error')
        elif p_id == "" and module_id != "":
           modules = None
           year = None
           flash('โปรดเลือกชั้นปีที่ 4 เทอมที่ 1 ก่อน', category='error')
        
        elif p_id == 'DSP11' or p_id == 'DSP12' or p_id == 'DSP21' or p_id == 'DSP22' or p_id == 'DSP31' or p_id == 'DSP32':
            plan_list = plans['plan'].split(',')          
        elif p_id == 'DSP3S' or p_id == 'DSP42' :
            plan_list.append(plans.plan)      
        elif p_id == 'DSP41' and module_id == "":
            flash('โปรดเลือก Module ก่อน', category='error')
        else:
            module = ast.literal_eval(plans.plan)
            plan_list = module[module_id].split(',')
    else:
        flash('โปรดเลือกใส่ภาคการศึกษา', category='error')   
    print(f'study Plan : {plan_list} (plan_list)')

    enrolled = []
    donthave = []

    for i in range(6):   
        e = request.form.get(f'enrolled{i}')
        if e is not None and e!= "":
            cur.execute(f'select * from subjects where subject_id = "{e}"')
            have_sub = cur.fetchone()
            if have_sub:
                enrolled.append(e)
            else:
                donthave.append(e)

    print(f'Have {enrolled} in database (enrolled)')
    print(f'Don\'t have {donthave} in database (donthave)')
    for i in range(len(donthave)):
        try:
            donthave.remove('')
        except ValueError:
            break
    con_list = []
    
    if enrolled !=[] and donthave is not None:
        con_list =[*enrolled, *donthave]
    if  p_id == 'DSP':
        flash(f'ใจเย็นใส่ชั้นปีกับเทอมก่อน', category='error')
        enrolled = None
        year = None
        modules = None
    elif p_id == 'DSP41' and modules == '':
        flash(f'เลือกปี 4 เทอม 1 แล้วต้องเลือก Module ด้วย', category='error')
        year = None
        modules = None
        con_list = None
        redirect(url_for('views.studyplan'))
    elif con_list == []:
        flash(f'ต่อจากนี้การใส่รหัสวิชาจะทรงประสิทธิภาพ', category='error')
        year = None
        modules = None
        redirect(url_for('views.studyplan'))
    elif len(con_list) == len(plan_list):
        pass
    elif len(con_list) > len(plan_list) and plan_list is not None:
        flash(f'ลงวิชาเกิน {len(con_list)-len(plan_list)} ตัว สำหรับ ปี {year[0]} เทอม {year[1]}', category='error')
    elif len(con_list) > len(plan_list) and plan_list is not None and year[1] =='ภาคฤดูร้อน':
        flash(f'ลงวิชาเกิน {len(con_list)-len(plan_list)} ตัว สำหรับ ปี {year[0]} {year[1]}', category='error')
    elif len(con_list) < len(plan_list):
        flash(f'ลงวิชาขาดไป {len(plan_list)-len(con_list)} ตัว สำหรับ ปี {year[0]} เทอม {year[1]}', category='error')
    print(f"{con_list} (con_list) ")
    global error_list
    error_list = []
                
    check = []

    if con_list is not None:
        for i in range(len(con_list)):
            cur.execute(f'select * from subjects where subject_id = "{con_list[i]}"')
            pre = cur.fetchone()
            if pre is not None:
                if pre['subject_prerequisite']:
                    c = "Warning"
                    check.append(c)
                    el = f'วิชานี้ต้องลง{pre.subject_prerequisite}ก่อน'
                    error_list.append(el)

            if con_list[i] in plan_list:
                c = "Pass"
                check.append(c)
                el = 'ไม่มีปัญหา'
                error_list.append(el)
            elif con_list[i] == 'DSI480'and enrolled_list[6][1] == "1":
                c = "Pass"
                check.append(c)
                el = 'ผ่านการเข้าฝึกงานภาคฤดูร้อนมาแล้ว'
                error_list.append(el)
            elif con_list[i] not in plan_list and con_list[i] in donthave:
                c = "Failed"
                check.append(c)
                flash(f'วิชา {con_list[i]} ไม่มีในระบบ', category='error')
                el = 'ไม่พบวิชาที่ลง'
                error_list.append(el)
            elif con_list[i] not in plan_list:
                c = "Failed"
                check.append(c)
                flash(f'วิชา {con_list[i]} ไม่เป็นไปตามแผนการเรียน', category='error')
                el = 'วิชาที่ลงไม่เป็นไปตามแผนการเรียนที่เลือก'
                error_list.append(el)
            
    print(f'{check} (check)')
    print(f'{error_list} (error_list)')

    return render_template('enroll.html',modules=modules,year=year,con_list=con_list,check=check,error_list=error_list)




@views.route("/profile")
def profile():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    id = auth.session['google_id']
    cur.execute(f'select * from student where user_id = {id}')
    profile_data = cur.fetchone()
    cur.execute(f'select * from major where major_id = {profile_data["major_id"]}')
    major_data = cur.fetchone()
    cur.execute(f'select * from faculty where faculty_id = {profile_data["faculty_id"]}')
    faculty_data = cur.fetchone()
    return render_template('profile.html', profile_data=profile_data, major_data=major_data, faculty_data=faculty_data)
   
@views.route("/login")
def login():
    return render_template('login.html')


@views.route("/auth_home")
@login_is_required
def auth_home():
    return render_template('auth_home.html')


@views.route("/studyplan" ,methods =['GET','POST'])
def studyplan():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    s_id = request.form.get("semester")
    p_id = 'DSP'+str(s_id)
    module_id = request.form.get("module_id")
    plans = None
    cur.execute('select * from study_plan where studyplan_id = %s',(p_id,))
    plans = cur.fetchone()
    plan_list = []
    year = []
    modules = ''

    if s_id is not None:
        for i in str(s_id):
            if i == "S":
                i = "ภาคฤดูร้อน"
                year.append(i)
            else:
                year.append(i)

    if module_id is not None:
        if module_id == '3':
            modules = "Actuarial Analytics"
        elif module_id == '4':
            modules = "Artificial Intelligence"
        elif module_id == '5':
            modules = "Digital Forensic"
        elif module_id == '6':
            modules = "Digital Transformation"
        elif module_id == '7':
            modules = "Health Informatics"

    if plans is not None:
        if p_id != "DSP41" and module_id != "":
            modules = None
            year = None
            flash('อ่ะ..จ๊ะเอ๋ตัวเอง!! ก็เขียนบอกอยู่ว่าของปี 4 เทอม 1', category='error') 
        elif p_id == 'DSP11' or p_id == 'DSP12' or p_id == 'DSP21' or p_id == 'DSP22' or p_id == 'DSP31' or p_id == 'DSP32':
            plan_list = plans['plan'].split(',')            
        elif p_id == 'DSP3S' or p_id == 'DSP42' :
            plan_list.append(plans.plan)            
        elif p_id == 'DSP41' and module_id == "":
            flash('โปรดเลือก Module ก่อน', category='error')
        else:
            module = ast.literal_eval(plans['plan'])
            plan_list = module[module_id].split(',')

       

    print(plan_list)
    sub_desc = []    
    for sub_id in plan_list:
        cur.execute(f'select * from subjects where subject_id = "{sub_id}"')
        desc = cur.fetchone()
        sub_desc.append(desc)

    
    return render_template('studyplan.html', plan_list=plan_list, sub_desc=sub_desc,year=year,modules=modules)