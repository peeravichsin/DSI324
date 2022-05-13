from flask import Flask
from flask_mysqldb import MySQL, MySQLdb
from os import path
import pandas as pd
DB_NAME = "dsi324"


def create_app():
    global mysql
    app = Flask(__name__)
    app.secret_key = "ifyouknowyouknowandifyoudontknowyoudontknow"
    app.config['MYSQL_HOST'] = "localhost"
    app.config['MYSQL_USER'] = "root"
    app.config['MYSQL_PASSWORD'] = "soccer481200"
    app.config['MYSQL_DB'] = "dsi324"
    mysql = MySQL(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    with app.app_context():
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        
          # Add Faculty

        faculty_num = "select * from faculty;"
        faculty_num = cur.execute(faculty_num)
        if faculty_num == 1:
            print(faculty_num)
            pass
        else:
            faculty_name = 'College of interdisciplinary studies'
            faculty_id = '24'
            cur.execute("insert into faculty( faculty_name, faculty_id ) values(%s,%s)",(faculty_name, faculty_id))
            mysql.connection.commit()
            print("Faculty Added !!!")

        
        # Add Subject

        n=[]
        f = open("subject.txt",encoding="utf-8")
        for i in f: 
            n.append(i)
        subject_num = len(n)
        subject_had = "select * from subjects;"
        subject_had = cur.execute(subject_had)
        if subject_num != subject_had:
            for l in n: 
                x = l.split(",")

                if len(x) == 4:
                    subject_id=x[0]
                    subject_name_th=x[1]
                    subject_name_en=x[2]
                    subject_credit=int(x[3])
                    cur.execute("insert into subjects(subject_id,subject_name_th,subject_name_en,subject_credit) values(%s,%s,%s,%s)",
                                (subject_id,subject_name_th,subject_name_en,subject_credit))
                    mysql.connection.commit()

                else:      
                    subject_id=x[0]
                    subject_name_th=x[1]
                    subject_name_en=x[2]
                    subject_credit=int(x[3])
                    subject_prerequisite=x[4]
                    cur.execute("insert into subjects(subject_id,subject_name_th,subject_name_en,subject_credit,subject_prerequisite) values(%s,%s,%s,%s,%s)",
                                (subject_id,subject_name_th,subject_name_en,subject_credit,subject_prerequisite))
                    mysql.connection.commit()

            print("Subjects Added !!!")



        # Add Major

        major_num = "select * from major;"
        major_num = cur.execute(major_num)
        if major_num == 3 :
            pass
        else:
            cur.executemany(
                """
                insert into major (major_id, major_name, faculty_id)
                values (%s,%s,%s)
                """ ,
                [
                ("20182067117526","Data Science and Innovation","24"),
                ("25550051100164","Philosophy, Politics and Economics","24"),
                ("25520051102782","Interdisciplinary Studies of Social Science","24")
                ]
                
            )
            mysql.connection.commit()
            print("Major Added !!!")
        
    
        # Add study plan

        plan_had = "select * from study_plan"
        plan_had = cur.execute(plan_had)
        plan_num = pd.read_csv('DSIstudyplan.csv')
        if plan_had != len(plan_num):
            for i in range(len(plan_num)):
                studyplan_id=plan_num.iloc[i][0]
                plan=plan_num.iloc[i][1]
                study_plan_years=str(plan_num.iloc[i][2])
                semester=plan_num.iloc[i][3]
                major_id=str(plan_num.iloc[i][4])
                cur.execute("insert into study_plan (studyplan_id, plan, study_plan_years, semester, major_id) values(%s,%s,%s,%s,%s)",
                            (studyplan_id, plan, study_plan_years, semester, major_id))
                mysql.connection.commit()
            print("Studyplan Added !!!")
        cur.close()

    return app

