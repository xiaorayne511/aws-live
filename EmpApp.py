from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *
from datetime import datetime


app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('Home.html')

@app.route("/addemp", methods=['GET','POST']) 
def AddEmp():
    return render_template('AddEmp.html', AddEmp=AddEmp)

@app.route("/getemp", methods=['GET','POST'])
def GetEmp():
    return render_template('GetEmp.html', GetEmp=GetEmp)

@app.route("/editemp", methods=['GET','POST'])
def EditEmp():
    return render_template('UpdateEmp.html', EditEmp=EditEmp)

@app.route("/attendanceemp", methods=['GET','POST'])
def AttendanceEmp():
    return render_template('TakeAttendance.html', AttendanceEmp=AttendanceEmp)

@app.route("/delemp", methods=['GET','POST'])
def DeleteEmp():
    return render_template('DelEmp.html', DeleteEmp=DeleteEmp)

@app.route("/about", methods=['POST'])
def about():
    return render_template('AboutUs.html', about=about)

def showimage(bucket):
    s3_client = boto3.client('s3')
    public_urls = []

    emp_id = request.form['emp_id']
    try:
        for item in s3_client.list_objects(Bucket=bucket)['Contents']:
            presigned_url = s3_client.generate_presigned_url('get_object', Params = {'Bucket': bucket, 'Key': item['Key']}, ExpiresIn = 100)
        if emp_id in presigned_url:
            public_urls.append(presigned_url)
    except Exception as e:
        pass
    return public_urls

@app.route("/addemp", methods=['GET','POST'], endpoint='AddEmp')
def AddEmp():
    if request.method == 'POST':

        emp_id = request.form['emp_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        pri_skill = request.form['pri_skill']
        location = request.form['location']
        hire_date = request.form['hire_date']
        salary = request.form['salary']
        position = request.form['position']
        phone_no = request.form['phone_no']
        benefit = request.form['benefit']

        emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id,first_name,last_name,pri_skill,location,hire_date,salary,position,phone_no,benefit))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')
        
        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                    s3_location = ''
            else:
                    s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                    s3_location,
                    custombucket,
                    emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

        print("all modification done...")
        return render_template('AddEmpOutput.html', name=emp_name, id=emp_id)

@app.route("/delemp", methods=['GET','POST'], endpoint='DeleteEmp')
def DeleteEmp():
    emp_id = request.form['emp_id']

    mycursor = db_conn.cursor()
    del_emp_SQL = "DELETE FROM employee WHERE emp_id = %s"
    mycursor.execute(del_emp_SQL, (emp_id))
    db_conn.commit()

    s3_client = boto3.client('S3')
    emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
    try:
        s3_client.detele.object(Bucket=custombucket, Key = emp_image_file_name_in_s3)
    
        return render_template('DelEmpOut.html', emp_id=emp_id)
    except Exception as e:
        return render_template('Unsuccessful.html')

@app.route("/getemp", methods=['GET', 'POST'], endpoint='GetEmp')
def GetEmp():
    if request.method == 'POST':
        try:
            emp_id = request.form['emp_id']
            cursor = db_conn.cursor()

            get_emp_sql = "SELECT * FROM employee WHERE emp_id = %s"
            cursor.execute(get_emp_sql,(emp_id))
            emp = cursor.fetchall()
            (emp_id,first_name,last_name,pri_skill,location,hire_date,salary,position,phone_no,benefit) = emp[0]
            image_URL = show_image(custombucket)

            attendance_emp_sql = "SELECT attendance.date, attendance.time, attendance_status FROM attendance INNER JOIN employee ON attendance.emp_id = employee.emp_id WHERE employee.emp_id = %s"
            mycursor = db_conn.cursor()
            mycursor.execute(attendance_emp_sql, (emp_id))
            status = mycursor.fetchall()
      
            return render_template('GetEmpOutput.html', emp_id=emp_id,first_name=first_name,last_name=last_name,pri_skill=pri_skill
            ,location=location,hire_date=hire_date,salary=salary,position=position,phone_no=phone_no,benefit=benefit,
            image_URL=image_URL,status=status)
            
        except Exception as e:
            return render_template('NotFound.html')
    else:
        return render_template('AddEmp.html', GetEmp=GetEmp)

@app.route("/attendanceemp", methods=['GET','POST'], endpoint='AttendanceEmp')
def AttendanceEmp():
    if request.method == 'POST':

        now = datetime.now()
        dt_string = now.strftime("%d%m%Y%H%M%S")
        d_string = now.strftime("%d/%m/%Y")
        t_string = now.strftime("%H:%M:%S")
    
        attendance_id = request.form['attendance_id'] + dt_string
        date = request.form['date'] + d_string
        time = request.form['time'] + t_string
        status = request.form['status'].getlist('attendance')
        emp_id = request.form['emp_id']

        attendance = ','.join(attendance)
        status = (attendance)

    try:
        insert_sql = "INSERT INTO attendance VALUES (%s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()
        cursor.execute(insert_sql, (attendance_id, date, time, status, emp_id))
        db_conn.commit()

        return render_template('Successfully.html', id = attendance_id)
        
    except Exception as e:
            return str(e)

    finally:
            cursor.close()

@app.route("/editemp", methods=['GET','POST'], endpoint='EditEmp')
def EditEmp():
    if request.method =='POST':

        emp_id = request.form['emp_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        pri_skill = request.form['pri_skill']
        location = request.form['location']
        hire_date = request.form['hire_date']
        salary = request.form['salary']
        position = request.form['position']
        phone_no = request.form['phone_no']
        emp_image_file = request.files['emp_image_file']
    
        update_sql = "UPDATE employee SET first_name = %s, last_name = %s, pri_skill = %s, location = %s, hire_date = %s, salary = %s, position = %s, phone_no = %s WHERE emp_id = %s"
        cursor = db_conn.cursor()
    
        changefield = (first_name, last_name, pri_skill, location, hire_date, salary, position, phone_no, emp_id)
        
    try:
        cursor.execute(update_sql, (changefield))
        db_conn.commit()
        emp_name = " " + first_name + " " + last_name

        if emp_image_file == "":
                    print("Select nothing")
        else:
            s3 = boto3.client('s3')
            emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
            s3_client.detele.object(Bucket=custombucket, Key = emp_image_file_name_in_s3)

            s3 = boto3.resource('s3')

    except Exception as e:
        return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template("UpdateEmpOutput.html")

@app.route("/editBenefit", methods=['GET', 'POST'])
def EditBenefit():
    if request.method == 'POST':
        emp_id = request.form['emp_id']
        benefit = request.form['benefit']

        update_sql = "UPDATE employee SET benefit = %s WHERE emp_id = %s"
        cursor = db_conn.cursor()

        changefield = (benefit,emp_id)

        try:
            cursor.execute(update_sql, (changefield))
            db_conn.commit()
        finally:
            cursor.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)