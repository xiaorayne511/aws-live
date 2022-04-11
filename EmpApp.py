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

@app.route("/addnewemp", methods=['GET','POST']) 
def home():
    return render_template('AddEmp.html')

@app.route("/getemp", methods=['GET','POST'])
def GetEmp():
    return render_template('GetEmp.html')

@app.route("/editemp", methods=['GET','POST'])
def diredit():
    return render_template('UpdateEmp.html')

@app.route("/attendanceemp", methods=['GET','POST'])
def diratt():
    return render_template('TakeAttendance.html')

@app.route("/delemp", methods=['GET','POST'])
def diratt():
    return render_template('DelEmp.html')

@app.route("/about", methods=['POST'])
def about():
    return render_template('AboutUs.html')

def showimage(bucket):
    s3_client = boto3.client('s3')
    public_urls = []
    emp_id = request.form['emp_id']
    try:
        for item in s3_client.list_objects(Bucket=bucket)['Contents']:
            presigned_url = s3_client.generate_presigned_url('get_object', Params = {'Bucket': bucket, 'Key': item['Key']}, ExpiresIn = 100)
            public_urls.append(presigned_url)
    except Exception as e:
        pass
    return public_urls

@app.route("/addemp", methods=['GET','POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    fname = request.form['fname']
    lname = request.form['lname']
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

        cursor.execute(insert_sql, (emp_id,fname,lname,pri_skill,location,hire_date,salary,position,phone_no,benefit))
        db_conn.commit()
        emp_name = "" + fname + " " + lname
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

@app.route("/delemp", methods=['GET','POST'])
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

            fetch_emp_sql = "SELECT * FROM employee WHERE emp_id = %s"
            cursor.execute(fetch_emp_sql,(emp_id))
            emp = cursor.fetchall()
            (emp_id,fname,lname,pri_skill,location,hire_date,salary,position,phone_no,benefit) = emp[0]
            image_URL = show_image(custombucket)

            return render_template('GetEmpOutput.html', emp_id=emp_id,fname=fname,lname=lname,pri_skill=pri_skill
            ,location=location,hire_date=hire_date,salary=salary,position=position,phone_no=phone_no,benefit=benefit,
            image_URL=image_URL)


@app.route("/attendanceemp", methods=['GET','POST'])
def AttendanceEmp():
    now = datetime.now()
    dt_string = now.strftime("%d%m%Y%H%M%S")

    attendance_id = request.form['attendance_id'] + dt_string
    date = request.form['date']
    time = request.form['time']
    status = request.form['status']
    emp_id = request.form['emp_id']

    insert_sql = "INSERT INTO attendance VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()
   
    try:

        cursor.execute(insert_sql, (attendance_id, date, time, status, emp_id))
        db_conn.commit()

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    return render_template('AddEmpOutput.html', status=status)

@app.route("/edit", methods=['GET','POST'])
def empedit():
        emp_id = request.form['emp_id']
        fname = request.form['fname']
        lname = request.form['lname']
        pri_skill = request.form['pri_skill']
        location = request.form['location']
        hire_date = request.form['hire_date']
        salary = request.form['salary']
        position = request.form['position']
        phone_no = request.form['phone_no']
        benefit = request.form['benefit']
    
    update_sql = "UPDATE employee SET first_name = %s, last_name = %s, pri_skill = %s, location = %s, hire_date = %s, salary = %s, position = %s, phone_no = %s, benefit = %s WHERE emp_id = %s"
    cursor = db_conn.cursor()
    
    changefield = (fname, lname, pri_skill, location, hire_date, salary, position, phone_no, benefit, emp_id)
    cursor.execute(update_sql, (changefield))
    db_conn.commit()
    cursor.close()
    return render_template("UpdateEmpOutput.html")



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
