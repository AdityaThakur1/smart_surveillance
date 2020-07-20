import base64
import json
import requests
import cv2
from ximilar.client import RecognitionClient
import os
import smtplib
from email.mime.text import MIMEText
from flask import *
from datetime import datetime
app = Flask(__name__)  

smtp_ssl_host = 'smtp.gmail.com'  # smtp.mail.yahoo.com
smtp_ssl_port = 465
username = 'notif8015@gmail.com'
password = 'intel@123'
sender = 'notif8015@gmail.com'
targets = ['adit8015@gmail.com','notification.nisivita@gmail.com']

@app.route('/')  
def upload():  
    return render_template("index.html")  
 
@app.route('/success', methods = ['POST'])  
def success():  
    if request.method == 'POST':
        f = request.files['file']      
        f.save(f.filename)
        
        source = f.filename
        location = source.split('_')[0]
        count = 0
        cap = cv2.VideoCapture(f.filename) 
        success = 1
        #milliseconds = 200
        #cap.set(cv2.CAP_PROP_POS_MSEC, milliseconds) 
        
        fps = cap.get(cv2.CAP_PROP_FPS) 
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        duration = frame_count / fps

        second = 0
        success, image = cap.read()
        
        client = RecognitionClient(token="c314203aea89974139e03d057a39f6e743b3e9fc")
        task, status = client.get_task(task_id='12872b94-39eb-4853-a95d-73ab0d682407')
        
        incident = 'No accident detected'

        while success and second <= duration:           
            cap.set(cv2.CAP_PROP_POS_MSEC, second * 500)
            success, image = cap.read()
            if(success):
                count += 1
                retval, buffer = cv2.imencode('.jpg', image)
                encoded_string =  base64.b64encode(buffer).decode('utf-8')
                print("test")
                result = task.classify([{'_base64': encoded_string }])
                best_label = result['records'][0]['best_label']
                if( best_label['name'] == 'accident' ):
                    now = datetime.now()
                    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                    incident = 'Accident detected at location ' + location +  " at " + dt_string + " count=" + str(count)
                    #Send Email
                    msg = MIMEText(incident)
                    msg['Subject'] = 'Accident detected'
                    msg['From'] = sender
                    msg['To'] = ', '.join(targets)

                    server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
                    server.login(username, password)
                    server.sendmail(sender, targets, msg.as_string())
                    server.quit()
                    break                  
            
            second += 1
            cap.release()
        return render_template("generic.html", name = location, encoded = incident )  
  
if __name__ == '__main__':  
    app.run(debug = True)