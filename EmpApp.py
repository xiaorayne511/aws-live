from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

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

@app.route("/addnewemp", methods=['GET','POST']) 
def home():
    return render_template('AddEmp.html')

@app.route("/getemp", methods=['GET','POST'])
def GetEmp():
    return render_template('GetEmp.html')

@app.route("/editemp", methods=['GET','POST'])
def diredit():
    return render_template("UpdateEmp.html")

@app.route("/empatt", methods=['GET','POST'])
def diratt():
    return render_template("TakeAttendance.html")

@app.route("/delemp", methods=['GET','POST'])
def diratt():
    return render_template("DelEmp.html")

@app.route("/about", methods=['POST'])
def about():
    return render_template('AboutUs.html')


@app.route("/addemp", methods=['POST'])
def AddEmp():
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
        for item in s3_client.list_objects(Bucket=bucket)['Contents']:
            presigned_URL = s3._client.generate_presigned_URL('get_object', Params = {'Bucket': bucket, 'Key': item['Key']}, ExpiresIn = 100)
            if emp_id in presigned_URL:
                public_URL.append(presigned_URL)
        except Exception as e:
            pass
        return public_URL

@app.route("/delete-emp", methods=['GET",'POST'])
def DeleteEmp():
    emp_id = request.form['emp_id']

    mycursor = db.conn.cursor()
    del_Att_SQL = "DELETE FROM employee WHERE emp_id = %s"
    mycursor.execute(del_Att_SQL, (emp_id))
    db_conn.commit()

    return render_template('DelEmpOut.html', emp_id=emp_id)

@app.route("/fetchdata", methods=['GET', 'POST'])
def fetchData():
    if request.method == 'POST':
        try:
            emp_id = request_form['emp_id']
            cursor = db_conn.cursor()

            fetch_emp_sql = "SELECT * FROM employee WHERE emp_id" = %s"
            cursor.execute(fetch_emp_sql,(emp_id))
            emp = cursor.fetchall()

            (id,fname,lname,priSkill,location,hiredate,salary,position,phone_no,benefit) = emp[0]
            image_URL = show_image(custombucket)

            att_emp_SQL = "SELECT attendance.date, attendance.time, attendance.status FROM attendance 
            INNER JOIN employee ON attendance.emp_id WHERE employee.emp_id = %s"
            mycursor = db_conn.cursor()
            mycursor.execute(att_emp_SQL, (emp_id))
            att_result = mycursor.fetchall()

            return render_template('GetEmpOutput.html', id=id,fname=fname,lname=lname,priSkill=priSkill
            ,location=location,hiredate=hiredate,salary=salary,position=position,phone_no=phone_no,benefit=benefit,
            image_URL=image_URL,att_result=att_result)
            except Exception as e:
                return render_template('IdNotFound.html')
            else:
                return render_template('AddEmp.html', fetchdata=fetchdata)

@app.route("/attendanceemp", methods=['GET','POST'])
def AttendanceEmp():
    if request.method == "POST":
        now = datetime.now()
        datetime_string = now.strftime("%d%m%Y%H%M%S")
        date_string = now.strftime("%d/%m/%Y")
        time_string = now.strftime("%H:%M:%S")

        attendance_id = request.form['attendance_id'] + datetime_string
        date = request.form['date'] + date_string
        time = request.form['time'] + time_string
        attendance = request.form.getlist('attendance')
        emp_id = request.form['emp_id']

        attendance = ','.join(attendance)

        try:
            insert_attendance_SQL = 'INSERT INTO attendance VALUES (%s,%s,%s,%s)'
            cursor = db_conn.cursor()
            cursor.execute(insert_attendance_SQL, (attendance_id,date,time,emp_id))
            db_conn.commit()

            return render_template('TakeAttendanceOutput.html', Od = attendance_id)
            except Exception as e:
                return str(e)
            finally:
                cursor.close()

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location, hire_date, salary, position, phone_no, benefit))
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
    return render_template('AddEmpOutput.html', name=emp_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
