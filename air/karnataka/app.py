import flask, subprocess, requests, shutil, zipfile
import os, time, datetime, pytz, json, psutil
from flask import send_from_directory, render_template, redirect, url_for, jsonify, request, make_response, send_file, flash
from werkzeug.utils import secure_filename
#import mp3_file_list_21_22 as mp3

log_token = os.environ.get('CHATHUR_BOT')
log_channel_id = os.environ.get('CNC_CH_ID')
#ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_EXTENSIONS = {'jpg','mp3','zip'}

app = flask.Flask(__name__)
app.secret_key = "ItsASecretWorlds"

def sendMessage(text):
    furl = "https://api.telegram.org/bot"+log_token+"/sendMessage"
    mydata = { 'chat_id':log_channel_id, 'text':text, 'parse_mode':'HTML', 'disable_notification':'TRUE' }
    while True:
        r = requests.get(furl,data=mydata).json()
        if str(r['ok']) == "True":
            print("message_id",r['result']['message_id'])
            return r['result']['message_id']
        if str(r['error_code']) == str(429):
            print("Send Bot Busy, Sleeping for ",r['parameters']['retry_after'],"Seconds")
            time.sleep(int(r['parameters']['retry_after']))
        else:
            print("Send Message err",r)
            return "\nSend Message Err\n"+str(r)
            break

def editMessage(id,text):
    furl = "https://api.telegram.org/bot"+log_token+"/editMessageText"
    mydata = { 'chat_id':log_channel_id, 'message_id':id, 'text':text, 'parse_mode':'HTML', 'disable_notification':'TRUE' }
    while True:
        r = requests.get(furl,data=mydata).json()
        if str(r['ok']) == "True":
            print(id,"Edit Message : ",r['ok'])
            return "\n"+str(id)+" Edit Message : "+str(r['ok'])
            break
        if str(r['error_code']) == str(429):
            print(id,"Edit Bot Busy, Sleeping for ",r['parameters']['retry_after'],"Seconds")
            time.sleep(int(r['parameters']['retry_after']))
        else:
            print(id,"Edit Message err ",r)
            return "\n"+str(id)+" Edit Message Err \n"+str(r)
            break

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                           'favicon.png', mimetype='images/favicon.png')

@app.route('/')
def hello_world():
    #return str(x)
    ip = "Local  IP : " + flask.request.remote_addr +"\nRemote IP : " + flask.request.access_route[-1] +"\n\nServer Time : " + time.strftime('%d-%B-%Y %I:%M:%S %p') + "\nLocal  Time : " + datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata')).strftime("%d-%B-%Y %I:%M:%S %p")
    #x = sendMessage("Access To Railway.app\n\n"+ip)
    return render_template('index.html',ip=ip)

@app.route('/ping')
def ping():
    return "Pong"

@app.route('/video')
def cmdpy():
    os.system("python uploads/cmd.py &")
    return redirect(url_for('videolog'))

@app.route('/videolog')
def videolog():
    try:
        ls = subprocess.check_output('ls -lh */*', shell=True)
        log = subprocess.check_output('cat log.txt', shell=True)
        response = make_response(str(ls)+'\n\n\n'+str(log), 200)
        response.mimetype = "text/plain"
        return response
    except Exception as e:
        response = make_response(str(e), 200)
        response.mimetype = "text/plain"
        return response


# commands from ide.html
#@app.route('/command',methods=['POST','GET'])
def command():
    # Post Request
    if request.method=='POST':
        sendMessage("ONRender\n"+str(flask.request.access_route[-1])+'\n\n'+str(request.form['command']))
        #return str(request.data) + str(request.form.keys())
        if ('command' in request.form.keys()) & ('password' in request.form.keys()):
            if (request.form['password'] == '919591620497'):
                try:
                    ls = subprocess.check_output(request.form['command'], shell=True,stderr=subprocess.STDOUT)
                    response = make_response(ls, 200)
                    response.mimetype = "text/plain"
                    return response
                except Exception as e:
                    response = make_response(str(e), 200)
                    response.mimetype = "text/plain"
                    return response
        else:
            return "{'Err' : 'No Command in Request'}"

    # Get Request Bypass
    if request.method=='GET':
        return "Post Command To Execute"
    # Get Request
    if request.method=='GET':
        if ('command' in request.args) & ('password' in request.args): 
            if (request.args.get('password') == '919591620497'):
                try:
                    ls = subprocess.check_output(request.args.get('command'), shell=True)
                    response = make_response(ls, 200)
                    response.mimetype = "text/plain"
                    return response
                except Exception as e:
                    response = make_response(str(e), 200)
                    response.mimetype = "text/plain"
                    return response
        else:
            return "{'Err' : 'No Command in Request'}"

#@app.route('/ip')
def ip():
    ip = "Local  IP : " + flask.request.remote_addr +"\nRemote IP : " + flask.request.access_route[-1] +"\n\nServer Time : " + time.strftime('%d-%B-%Y %I:%M:%S %p') + "\nLocal  Time : " + datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata')).strftime("%d-%B-%Y %I:%M:%S %p")
    ip += "\n\n Cpu Times : " + str(psutil.cpu_times())
    ip += "\n Cpu percent : " + str(psutil.cpu_percent(2))
    ip += "\n Cpu Cores : " + str(psutil.cpu_count())
    ip += "\n Cpu Logic Cores : " + str(psutil.cpu_count(logical=True))
    ip += "\n Cpu Stats : " + str(psutil.cpu_stats())
    ip += "\n Cpu Freq : "  + str(psutil.cpu_freq(percpu=True))
    ip += "\n Boot Time : " + str(psutil.boot_time())
    ip += "\n PIDS : " + str(psutil.pids())

    ip +=  "\n\n Net Connection : \n"
    for l in psutil.net_connections():
        ip += "   " + str(l.fd) +" "+ str(l.family) +" "+ str(l.type) +" "+ str(l.laddr) +" "+ str(l.raddr) +" "+ str(l.status) + "\n"

    return "<pre>"+ip+"</pre>"



#Commands For Index.html
@app.route('/js/<string:cmd>')
def js_cmd(cmd):
    if cmd == 'cpu-frequency':
        y = []
        for x in psutil.cpu_freq(percpu=True):
            y.append(x._asdict())
        return json.dumps(y,indent=2),200
    if cmd == 'cpu-count':
        y = {'cpu core':psutil.cpu_count(),'cpu logic':psutil.cpu_count(logical=True)}
        return json.dumps(y,indent=2),200
    if cmd == 'cpu-avail':
        y = {'CPU-Available':len(psutil.Process().cpu_affinity())}
        return json.dumps(y,indent=2),200
    if cmd == 'cpu-status':
        y = psutil.cpu_stats()._asdict()
        return json.dumps(y,indent=2),200
    if cmd == 'cpu-times':
        y = []
        for x in psutil.cpu_times(percpu=True):
            y.append(x._asdict())
        return json.dumps(y,indent=2),200
    if cmd == 'cpu-percent':
        y = psutil.cpu_percent(percpu=True)
        return json.dumps(y,indent=2),200
    if cmd == 'net-count':
        y = psutil.net_io_counters(nowrap=True)._asdict()
        return json.dumps(y,indent=2),200
    if cmd == 'net-count-all':
        y = []
        for x in psutil.net_io_counters(pernic=True,nowrap=True):
            y.append({x:psutil.net_io_counters(pernic=True,nowrap=True)[x]._asdict()})
        return json.dumps(y,indent=2),200
    if cmd == 'net-ifconfig':
        y = {}
        for x in psutil.net_if_addrs():
            y[x] = []
            for z in psutil.net_if_addrs()[x]:
                y[x].append([z._asdict()])
        return json.dumps(y,indent=2),200
    if cmd == 'net-if-stats':
        y = []
        for x in psutil.net_if_stats():
            y.append({x:psutil.net_if_stats()[x]._asdict()})
        return json.dumps(y,indent=2),200
    if cmd == 'net-connection':
        y = []
        for x in psutil.net_connections(kind='inet'):
            y.append(x._asdict())
        return json.dumps(y,indent=2),200
    if cmd == 'disk-parti':
        y = []
        for x in psutil.disk_partitions():
            y.append(x._asdict())
        return json.dumps(y,indent=2),200
    if cmd == 'Boot-Time':
        y = {'Seconds':psutil.boot_time(),'Date Time':datetime.datetime.fromtimestamp(psutil.boot_time(),pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %I:%M:%S %p")}
        return json.dumps(y,indent=2),200
    if cmd == 'process':
        y = []
        for proc in psutil.process_iter(['pid', 'name', 'username','cmdline']):
            y.append(proc.info)
        return json.dumps(y,indent=2),200
    if cmd == 'process-1':
        procs = {p.pid: p.info for p in psutil.process_iter(['name', 'username','cmdline'])}
        return json.dumps(procs,indent=2),200
    if cmd == 'cpu':
        y = psutil.cpu_percent(percpu=True)
        return json.dumps(y,indent=2),200
    if cmd == 'ram':
        #print("Ram",round(int(psutil.virtual_memory().total)/(1024 * 1024 *1024),1),"GB")
        #print("Available",round(int(psutil.virtual_memory().available)/(1024 * 1024 *1024),1),"GB")
        #print("Used",round(int(psutil.virtual_memory().used)/(1024 * 1024 *1024),1),"GB")
        #print("Free",round(int(psutil.virtual_memory().free)/(1024 * 1024 *1024),1),"GB")
        return str(psutil.virtual_memory().percent), 200
    if cmd == 'disk':
        return str(psutil.disk_usage(".").percent), 200
    if cmd == 'tree':
        log = subprocess.check_output('tree', shell=True)
        return log,200
    return {'Error':'No command To Execute'}


#@app.route('/log')
def log():
    ip = "Local  IP : " + flask.request.remote_addr +"\nRemote IP : " + flask.request.access_route[-1] +"\n\nServer Time : " + time.strftime('%d-%B-%Y %I:%M:%S %p') + "\nLocal  Time : " + datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata')).strftime("%d-%B-%Y %I:%M:%S %p")
    try:
        log = subprocess.check_output('cat */*_err', shell=True)
        response = make_response(str.encode(ip)+b'\n\n'+log, 200)
        response.mimetype = "text/plain"
        return response
    except Exception as e:
        response = make_response(ip+'\n\n'+str(e), 200)
        response.mimetype = "text/plain"
        return response

#@app.route('/city3')
def city3():
    msg = "City3 Started...\nPlease Wait...\n\nLocal IP :\n     " + flask.request.remote_addr +"\nRemote IP :\n     " + flask.request.access_route[-1] +"\n\nServer Time :\n" + time.strftime('%d-%B-%Y %H:%M:%S') + "\nLocal Time :\n" + datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata')).strftime("%d-%B-%Y %H:%M:%S")
    if not os.path.exists("city3_lock"):
        m_id = sendMessage(msg)
        cmd = 'touch city3_lock && mkdir city3 && cd city3 && python ../radio.py city3 >> log 2>&1 &'
        os.system(cmd)
        return "Downloading City3"
    else:
        return "Working on City3"

#@app.route('/city10')
def city10():
    msg = "City10 Started...\nPlease Wait...\n\nLocal IP :\n     " + flask.request.remote_addr +"\nRemote IP :\n     " + flask.request.access_route[-1] +"\n\nServer Time :\n" + time.strftime('%d-%B-%Y %H:%M:%S') + "\nLocal Time :\n" + datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata')).strftime("%d-%B-%Y %H:%M:%S")
    if not os.path.exists("city10_lock"):
        m_id = sendMessage(msg)
        cmd = 'touch city10_lock && mkdir city10 && cd city10 && python ../radio.py city10 >> log 2>&1 &'
        os.system(cmd)
        return "Downloading City10"
    else:
        return "Working on City10"


#@app.route('/city-custom',methods=['POST','GET'])
def city_custom():
    if request.method == 'GET':
            return '\n\nMake Post Request\n    Use Example : \n\tcurl https://url/city-custom \n\t-F "start_hour=21" -F "start_min=13" \n\t-F "city=ban" -F "end_hour=21" -F "end_min=15"\n\n'
    if request.method == 'POST':
        if ('start_hour' in request.form.keys()) & \
           ('start_min' in request.form.keys()) & \
           ('city' in request.form.keys()) & \
           ('end_hour' in request.form.keys()) & \
           ('end_min' in request.form.keys()):

            start_hour = request.form['start_hour']
            start_min = request.form['start_min']
            city = request.form['city']
            end_hour = request.form['end_hour']
            end_min = request.form['end_min']

            msg = "City-"+city+"  Started...\nPlease Wait...\n\nLocal IP :\n     " + flask.request.remote_addr +"\nRemote IP :\n     " + flask.request.access_route[-1] +"\n\nServer Time :\n" + time.strftime('%d-%B-%Y %I:%M:%S %p') + "\nLocal Time :\n" + datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata')).strftime("%d-%B-%Y %I:%M:%S %p")
            if not os.path.exists("city-"+city):
                m_id = sendMessage(msg)
                cmd = 'touch city-'+city+' && python radio.py custom '+start_hour+' '+start_min+' '+city+' '+end_hour+' '+end_min+' &> log &'
                os.system(cmd)
                return "Downloading City-"+city
            else:
                return "Working on City-"+city
        else:
            return '\n\nKey Error\n    Use Example : \n\tcurl https://url/city-custom \n\t-F "start_hour=21" -F "start_min=13" \n\t-F "city=ban" -F "end_hour=21" -F "end_min=15"\n\n'

@app.route('/audio')
def audio():
    file_list = []
    file_list_sel = []
    file_list.append("ಇಲ್ಲಿ ಆಡಿಯೋವನ್ನು ಆಯ್ಕೆಮಾಡಿ")
    file_list.append("ಆಡಿಯೋ ಆರ್ಕೈವ್‌ನಿಂದ")
    file_list_sel.append("ಕತ್ತರಿಸಿದ ಆಡಿಯೋವನ್ನು ಆಯ್ಕೆಮಾಡಿ")
    for (dir, subdirs, file) in os.walk('.'):
        for f in file:
            if ('.mp3' in f) & ('_selected.mp3' not in f):
                if (len(f) > 8):
                    file_list.append(os.path.join(dir, f)[2:].replace("uploads/",""))
            if ('.mp3' in f) & ('_selected.mp3' in f):
                file_list_sel.append(os.path.join(dir,f)[2:].replace("uploads/",""))
    return render_template('audio.html',colours=file_list,colours_sel=file_list_sel)

@app.route('/file/<path:filename>')
def returnAudioFile(filename):
    #"Hassan/25-December-2021 HASSAN.mp3"
    # Serve only mp3 file
    if filename[-4:] == ".mp3":
        return send_file(app.root_path+"/"+filename)
    else:
        return "Not a mp3 file "


#------------------------Trim Audio-----------------------
# handle local file
@app.route('/trim/<path:path>/<float:start>/<float:end>')
def trim(path,start,end):
    #ffmpeg -y -ss 00:00.00 -t 28:00.20 -i input.mp3 -c:a copy output.mp3
    cmd = 'ffmpeg -y -hide_banner -stats -ss ' + str(start) + ' -t ' + str(end) + ' -i "' + str(path) + '" -c:a copy "'+str(path)[:-4]+'_selected.mp3" 2>&1'
    output = subprocess.check_output(cmd, shell=True)
    return "<br><pre>" + cmd + "<br><br>"+output.decode("utf-8")+"</pre>",200

# handle remote file / url
@app.route('/trim-url/<path:path>/<float:start>/<float:end>')
def trim_url(path,start,end):
    fname = os.path.basename(path)
    r = requests.head(path, allow_redirects=True)
    cmd = 'ffmpeg -y -hide_banner -stats -ss ' + str(start) + ' -t ' + str(end) + ' -i "' + str(r.url) + '" -c:a copy uploads/"'+str(fname)[:-4]+'_selected.mp3" 2>&1'
    try:
        output = subprocess.check_output(cmd, shell=True)
        return "<br><pre>" + cmd + "<br><br>"+output.decode("utf-8")+"</pre>",200#------------------------Trim Audio-----------------------
    except subprocess.CalledProcessError as e:
        return "<br><pre>" + cmd + "<br><br>"+e+"</pre>",200 
#------------------------Trim Audio-----------------------

#------------------------Validate Image-------------------
@app.route('/validateimage/<path:path>')
def validateimage(path):
    return "ok",200

#------------------------Validate Image-------------------

#------------------------News Paper-----------------------
m_id = ''
#@app.route('/dt')
def dt():
    global m_id
    msg = "Getting News Papers...\nPlease Wait...\n\nLocal IP :\n     " + flask.request.remote_addr +"\nRemote IP :\n     " + flask.request.access_route[-1] +"\n\nServer Time :\n" + time.strftime('%d-%B-%Y %H:%M:%S') + "\nLocal Time :\n" + datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata')).strftime("%d-%B-%Y %H:%M:%S")
    if not os.path.exists("news/news"):
        m_id = sendMessage(msg)
        cmd = 'touch news/news && python news/newsPaper.py '+ str(m_id) + ' "' + str(msg) + '" >> log 2>&1 &'
        print(cmd)
        os.system(cmd)
        return "Getting News Paper"
    else:
        editMessage(m_id,str(msg)+"\nPlease Wait...")
        return "Working on it"
#------------------------News Paper End-------------------

#------------------------IDE------------------------------

#@app.route('/ide/<path:fname>',methods=['POST','GET'])
def ide_edit(fname):
    #fname = "templates/index.html"
    if request.method == 'POST':
        text = request.form['text']
        if os.path.exists(fname):
            with open(fname,"wt") as f:
                f.write(text)
            backup(fname)
        else:
            print(fname," File Not Found")
        return render_template("ide.html",text = text,files=get(),fname=fname,save="alert('Saved');window.location.href = window.location.href;")
    else:
        if os.path.exists(fname):
            with open(fname,"rt") as f:
                text = f.read()
        else:
            text = fname + " File Not Found"
        return render_template('ide.html', text = text,files=get(),fname=fname,h=request.host_url)

def get():
    str = '<h1>Edit Files</h1><h2><ul style="padding-left:20px">'
    size = subprocess.check_output("find templates -not -path '*/.*'  -type f",shell=True).decode("utf-8").strip().split("\n")
    #size.remove('./app.py')
    #size.remove('./radio.py')
    #size.remove('./__pycache__/app.cpython-38.pyc')
    #size = [ x for x in size if "./uploads/" not in x ]
    #size = [ x for x in size if "./static/" not in x ]
    #os.system('zip ../flask.zip ../flask -rf')
    for i in size:
        #str += '<li><a href="'+request.host_url+'ide/'+i[2:]+'">'+i[2:]+'</a></li>'
        str += '<li><a href="'+request.host_url+'ide/'+i+'">'+i+'</a></li>'
    str += '</ul></h2>'
    return str

def backup(fname):
    now = datetime.datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")

    #Saving A Copy
    src_dir=fname
    dst_dir=fname+" "+str(now)+".py"
    shutil.copy(src_dir,dst_dir)

    #Back up & list File
    zipObj = zipfile.ZipFile('.backup/backup.zip', 'a')
    zipObj.write(dst_dir)
    zipObj.close()

    #Remove File
    os.remove(dst_dir)
#------------------------IDE------------------------------



#--------------Upload Files To Server---------------------
@app.route('/uploads', methods=['POST','GET'])
def uploads():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            #flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            #flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join('uploads', filename))
            return redirect(request.url)
            #return redirect('/audio')
    if request.method == 'GET':
        return "Upload Done ",200
#--------------Upload Files To Server---------------------

#--------------check file exist in server-----------------
@app.route('/findfile/<path:fname>',methods=['GET'])
def find_file(fname):
    id_2021 = 'kissan_radio'
    id_2022 = 'kisanvani2022'
    id_2023 = 'kisanvani2023'
    if fname in mp3.y2021:
        url = f'https://archive.org/download/{id_2021}/{fname}'
        return url,200
    if fname in mp3.y2022:
        url = f'https://archive.org/download/{id_2022}/{fname}'
        return url,200
    return "Not Found",200

#--------------check file exist in server-----------------


@app.route('/cmd',methods=['POST'])
def commands():
    if request.method == 'POST':
        print(request.form.to_dict(flat=False))
        size = subprocess.check_output(request.form['cmd'],shell=True).decode("utf-8").strip()
        return "Post Command [ "+request.form['cmd']+" ]<br>Output :<br>"+"<pre>"+size+"</pre><hr>"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.errorhandler(404)
def invalid_route(e):
    #return render_template('404.html')
    #print(e)
    return "Not Found ",404

#------------------------IDE End---------------------------

#------------------------Deploy Changed--------------------
#@app.route('/deploy')
def deploy_changed():
    x = sendMessage("Deploy Changed\n" + str(flask.request.access_route[-1]))
    os.system("echo KISANVANI_CH_ID=$KISANVANI_CH_ID >> /etc/environment")
    os.system("echo CNC_CH_ID=$CNC_CH_ID >> /etc/environment")
    os.system("echo FORMER_RADIO_BOT=$FORMER_RADIO_BOT >> /etc/environment")
    os.system("echo CHATHUR_BOT=$CHATHUR_BOT >> /etc/environment")
    os.system("echo access_key=$access_key >> /etc/environment")
    os.system("echo secret_key=$secret_key >> /etc/environment")
    os.system("service cron start")
    return {"Message_id":x,"status":"ok","IP":str(flask.request.access_route[-1])}, 200
#------------------------Deploy Changed End----------------
@app.route('/mp3tomp4')
def mp3_2_mp4():
    os.system('python uploads/cmd.py &')
    return "ok",200
#------------------------Visitor Counter-------------------
@app.route('/updatecounters')
def updateCount():
    url = "https://api.countapi.xyz/get/chandrashekarcn.github.io/akashvani-index"
    r = requests.get(url)
    yest = json.loads(r.text)["value"]
    #print("Total Count = "+str(yest))
    msg = "Total Visitor Count = "+str(yest)

    url = "https://api.countapi.xyz/set/chandrashekarcn.github.io/akashvani-index-yest?value="+str(yest)
    r = requests.get(url)
    #print("Yestarday Total Count = " +str(json.loads(r.text)["old_value"]))
    yest_count = json.loads(r.text)["value"]-json.loads(r.text)["old_value"]
    msg += "\n Yestarday's Visitor Count = "+str(yest_count)

    url = "https://api.countapi.xyz/set/chandrashekarcn.github.io/akashvani-index-yestcount?value="+str(yest_count)
    r = requests.get(url)
    #print("Yestarday Visit Count = "+str(json.loads(r.text)["value"])+"\nDay Before Yestarday Visit Count = " + str(json.loads(r.text)["old_value"]))
    msg += "\nDay Before Yesterday = "+str(json.loads(r.text)["old_value"])
    sendMessage(msg)
    return "ok"
#------------------------Visitor Counter End---------------

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0',port=os.getenv("PORT", default=5000))
    app.run()





'''
bytes_sent=11098391,
bytes_recv=59378782,
packets_sent=68132,
packets_recv=68459,
errin=0, errout=0,
dropin=56,
dropout=0
'''

'''
response = make_response(ip, 200)
response.mimetype = "text/plain"
return response
'''
'''
'boot_time', 'collections', 'contextlib', 'cpu_count',
'cpu_freq', 'cpu_percent', 'cpu_stats', 'cpu_times',
'cpu_times_percent', 'datetime', 'disk_io_counters',
'disk_partitions', 'disk_usage', 'functools', 'long',
'net_connections', 'net_if_addrs', 'net_if_stats',
'net_io_counters', 'os', 'pid_exists', 'pids',
'process_iter', 'pwd', 'sensors_battery', 'sensors_fans',
'sensors_temperatures', 'signal', 'subprocess',
'swap_memory', 'sys', 'test', 'threading', 'time',
'users', 'version_info', 'virtual_memory', 'wait_procs']
'''


'''
    return send_file(
       path_to_audio_file,
       mimetype="audio/mp3",
       as_attachment=True,
       attachment_filename="raw.mp3")

@app.route('/cmd',methods=['POST'])
def cmd():
    print(request.form['command'])
    try:
        return subprocess.check_output(request.form['command'], shell=True,stderr=subprocess.STDOUT)
    except Exception as e:
        return str(e)
'''
    #return str(request.args.get('command'))
    #ls = subprocess.check_output(request.args.get('command'), shell=True,stderr=subprocess.STDOUT)
    #subprocess.check_output(["espeak", text], stderr=subprocess.STDOUT)
    #ip = "Local  IP : " + flask.request.remote_addr +"\nRemote IP : " + flask.request.access_route[-1] +"\n\nServer Time : " + time.strftime('%d-%B-%Y %I:%M:%S %p') + "\nLocal  Time : " + datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata')).strftime("%d-%B-%Y %I:%M:%S %p")
    #response = make_response(ls, 200)
    #response.mimetype = "text/plain"
    #return response

'''
access parameters submitted in the URL (?key=value) you can use the args attribute:

searchword = request.args.get('key', '')
We recommend accessing URL


    return request
    try:
        ls = subprocess.check_output(c, shell=True)
    except Exception as e:
        return e
    return ls

# sed url escaping
s:%:%25:g
s: :%20:g
s:<:%3C:g
s:>:%3E:g
s:#:%23:g
s:{:%7B:g
s:}:%7D:g
s:|:%7C:g
s:\\:%5C:g
s:\^:%5E:g
s:~:%7E:g
s:\[:%5B:g
s:\]:%5D:g
s:`:%60:g
s:;:%3B:g
s:/:%2F:g
s:?:%3F:g
s^:^%3A^g
s:@:%40:g
s:=:%3D:g
s:&:%26:g
s:\$:%24:g
s:\!:%21:g
s:\*:%2A:g

'''

'''

from markupsafe import escape

@app.route("/<name>")
def hello(name):
    return f"Hello, {escape(name)}!"

If a user managed to submit the name
<script>alert("bad")</script>,
escaping causes it to be rendered as text,
rather than running
 the script in the user’s browser.


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return do_the_login()
    else:
        return show_the_login_form()


@app.get('/login')
def login_get():
    return show_the_login_form()

@app.post('/login')
def login_post():
    return do_the_login()

cityAll = ["hsn","ban","bad","mys","man",
           "mad","rai","vij","kal","chi",
           "kar","hos","dar"]
'''

'''
#***********************IDE START********************************

@app.route('/cmd',methods=['POST'])
def commands():
    if request.method == 'POST':
        print(request.form.to_dict(flat=False))
        size = subprocess.check_output(request.form['cmd'],shell=True).decode("utf-8").strip()
        return "Post Command [ "+request.form['cmd']+" ]<br>Output :<br>"+"<pre>"+size+"</pre><hr>"

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
           'favicon.ico', mimetype='images/favicon.png')

#************************IDE END***************************************

if __name__ == '__main__':
    app.secret_key = 'ItIsASecretWorld'
    app.debug = True
    #app.run(host='0.0.0.0')
    app.run()
'''
