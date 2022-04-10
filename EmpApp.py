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
    return render_template('AddEmp.html')

@app.route("/getemp", methods=['POST'])
def GetEmp():
    return render_template('GetEmp.html', GetEmp=GetEmp)

def show_image(bucket):
    s3_client = boto3.client('s3')
    public_URL = []

    emp_id = request.form['emp_id']

    try:
        for item in s3_client.list_objects(Bucket=bucket)['Contents']:
            presigned_URL = s3._client.generate_presigned_URL('get_object', Params = {'Bucket': bucket, 'Key': item['Key']}, ExpiresIn = 100)
            if emp_id in presigned_URL:
                public_URL.append(presigned_URL)
        except Exception as e:
            pass
        return public_URL

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

            return render_template('GetEmpOutput.html', id=id,fname=fname,lname=lname,priSkill=priSkill
            ,location=location,hiredate=hiredate,salary=salary,position=position,phone_no=phone_no,benefit=benefit,image_URL=image_URL)
            except Exception as e:
                return render_template('IdNotFound.html')
            else:
                return render_template('AddEmp.html', fetchdata=fetchdata)

@app.route("/addemp", methods=['GET",'POST'])
def DeleteEmp():
    emp_id = request.form['emp_id']

    mycursor = db_conn.cursor()
    del_Att_SQL = "DELETE FROM attendance WHERE emp_id = %s"
    mycursor.execute(del_Att_SQL, (emp_id))
    db_conn.commit()

    mycursor = db.conn.cursor()
    del_Att_SQL = "DELETE FROM employee WHERE emp_id = %s"
    mycursor.execute(del_Att_SQL, (emp_id))
    db_conn.commit()

    s3_client = boto3.client('s3')
    emp_image_file_name_in_s3 = "emp-id-" +str(emp_id) + "_image_file" 
    try:
        s3_client.delete_object(Bucket=custombucket, Key = emp_image_file_name_in_s3)
            return render_template('DeleteSuccess.html')
        except Exception as e:
            return render_template('DeleteFail.html')

# @app.route("/attendanceemp", methods=['GET','POST'])
# def AttendanceEmp():
#     if request.method == "POST":
#         now = datetime.now()
#         datetime_string = now.strftime("%d%m%Y%H%M%S")
#         date_string = now.strftime("%d/%m/%Y")
#         time_string = now.strftime("%H:%M:%S")

#         attendance_id = request.form['attendance_id'] + datetime_string
#         date = request.form['date'] + date_string
#         time = request.form['time'] + time_string
#         attendance = request.form.getlist('attendance')
#         emp_id = request.form['emp_id']

#         attendance = ','.join(attendance)
#         att_values = (attendance)

#         try:
#             insert_attendance_SQL = 'INSERT INTO attendance VALUES (%s,%s,%s,%s,%s)'
#             cursor = db_conn.cursor()
#             cursor.execute(insert_attendance_SQL, (attendance_id,date,time,att_values,emp_id))
#             db_conn.commit()

#             return render_template('SuccessAttendance.html', Od = attendance_id)
#             except Exception as e:
#                 return str(e)
#             finally:
#                 cursor.close()


@app.route("/addemp", methods=['GET','POST'])
def AddEmp():
    if request.method == 'POST':
        now = datetime.now()
        datetime_string = now.strftime("%d%m%Y%H%M%S")
        reg = now.strftime("%d/%m/%Y %H:%M:%S")
        
        emp_id = request.form['emp_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        pri_skill = request.form['pri_skill']
        location = request.form['location']
        salary = request.form['salary']
        position = request.form['position']
        phone_no = request.form['phone_no']
        benefit = request.form['benefit']
        
        emp_image_file = request.files['emp_image_file']

        insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()
        if emp_image_file.filename == "":
            return "Please select a file"

         try:

            cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location, salary, position, phone_no, benefit))
            db_conn.commit()
            emp_name = "" + first_name + " " + last_name
            # Uplaod image file in S3 #
            emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
            s3 = boto3.resource('s3')

        try:
            print("Uploading image to S3...")
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

    print("modification done")
    return render_template('AddEmpOutput.html', name=emp_name, id=emp_id)

    else:
        return render_template('GetEmp.html', AddEmp=AddEmp)

@app.route("/editemp", methods=['GET','POST'])
def EditEmp():
    if request.method == 'POST':

        first_name = request.form['first_name']
        last_name = request.form['last_name']
        pri_skill = request.form['pri_skill']
        location = request.form['location']
        salary = request.form['salary']
        position = request.form['position']
        phone_no = request.form['phone_no']
        benefit = request.form['benefit']
        emp_id = request.form['emp_id']
        emp_image_file = request.form['emp_image_file']

        update_SQL = "UPDATE employee SET first_name = %s, last_name = %s, pri_skill = %s, location = %s, salary = %s, position = %s, phone_no = %s, benefit = %s WHERE emp_id = %s"
        cursor = db_conn.cursor()

        changeField = (first_name, last_name, pri_skill, location, salary, position, phone_no, benefit, emp_id)

        try:
            cursor.execute(update_SQL, (changeField)
            db_conn.commit()
            emp_name = "" + first_name + "" + last_name

            if emp_image_file.filename == "":
                print("Select Nothing")

            else 
                s3_client = boto3.client('s3')
                emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
                s3_client.delete_object(Bucket=custombucket, Key = emp_image_file_name_in_s3)
                #upload image to s3
                s3 = boto3.resource('s3')

            try:
                print("Uploading image to s3...")
                s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
                bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
                s3_location = (bucket_location['LocationConstraint'])

                if s3_location is None:
                    s3_location = ''
                else:
                    s3_location = '-' +s3_location

                object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(s3_location, custombucket, emp_image_file_name_in_s3)

            except Exception as e:
                return str(e)
            
            print("modification done")
            return render_template('AddEmpOutput.html', name=emp_name. id=emp_id)
        else:
            return render_template('GetEmp.html', AddEmp=AddEmp)
            
@app.route("/editbenefit-emp", methods=['GET','POST'])
def EditBenefitEmp():
    if request.method == 'POST':
        emp_id = request.form['emp_id']
        benefit = request.form['benefit']

        update_SQL = "UPDATE employee SET benefit = %s WHERE emp_id = %s"
        cursor = db_conn.cursor()

        changeField = (benefit, emp_id)

        try:
            cursor.execute(update_SQL, (changeField))
            db_conn.commit()

        finally:
            cursor.close()
        
        print("modification done")
        return render_template('EditBenefitSuccess.html')

    else:
        return render_template('GetEmp.html', AddEmp=AddEmp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
