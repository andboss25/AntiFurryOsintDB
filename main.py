
import sqlite3
import flask
from flask import request
import logging
import flask.logging
import os
import waitress

# Disable logs
import flask.cli
flask.cli.show_server_banner = lambda *args: None

from colorama import Fore

from core import Innit
from core import Conn
from core import Config
from core import Style

App = flask.Flask(__name__)

print('Anti-Furry OSINT DB')
print('This project was made by anti-furries')
print('(If you wish to encrypt or decrypt the databse you must run "encrypt.py" or "decrypt.py")')
print(Fore.BLUE + 'Dashboard on http://127.0.0.1:1642' + Fore.WHITE)
print(Fore.RED + '**THIS IS NOT MADE TO BE HOSTED AND OPEN TO THE ACTUAL INTERNET AS IT CONTAINS MULTIPLE VULNERABILITES**' + Fore.WHITE)

if os.path.isfile('OSINT.db'):
    pass
elif os.path.isfile('OSINT.db.enc'):
    print(Fore.RED + "There is a encrypted database and no normal database file , you must run decrypt.py and enter the password." + Fore.WHITE)
    quit(0)
else:
    pass

Innit.GenerateDBStructure()

@App.route("/")
def LandingPage():
    yield ''.join(Style.StylePage())
    conn,cursor = Conn.GetDBConnection()
    yield "<h1>Anti-furry OSINT DB Dashboard</h1>"
    yield "<hr>"
    
    targets = cursor.execute("SELECT id,start_vector_type,details FROM targets").fetchall()
    targets.reverse() # Reverse the targets list to show the new ones at the top

    for target in targets:
        v_data = cursor.execute(f"SELECT * FROM {target[1]}s WHERE target_id=? AND is_starting_vector=1",(target[0],)).fetchone()

        index = 0

        yield "<div id='section' >"

        for x in Config.GetConfig()["vector_types"][target[1]]:
            if x.startswith("%"):
                pass
            else:
                yield f"<p>{x}: {v_data[index]}</p>"
                index = index + 1
            
        yield f"<p>Id: {target[0]}</p> <p>Details: {target[2]}</p>"
        yield f"<a href='/target/view/{target[0]}'>View target in more detail</a>"

        yield "</div>"
        yield "<hr>"
    
    yield f"<a href='/target/upload'>Add a new target</a>"

    Conn.EndDBConnection(conn,cursor)

@App.route("/target/upload")
def UploadTarget():
    # To access request["args"] i needed to use stream_with_context()
    def generate():
        yield ''.join(Style.StylePage())
        try:
            start_vector_type = request.args["svt"]
        except:
            start_vector_type = None

        yield "<h1>Upload Target</h1>"
        yield "<hr>"
        if start_vector_type == None:
            yield "<label for='start_vector_type'>Start vector type:</label>"
            yield "<select id='start_vector_type'><option>Select One</option>"
            for vector_type in Config.GetConfig()["vector_types"]:
                yield f"<option>{vector_type}</option>"
            yield "</select>"
            yield '<script>document.getElementById("start_vector_type").onchange = function(){if (document.getElementsByTagName("option")[document.getElementById("start_vector_type").selectedIndex].value != "Select One") {window.location.href = "/target/upload?svt=" + document.getElementsByTagName("option")[document.getElementById("start_vector_type").selectedIndex].value}}</script>'
        else:
            yield "<textarea id='details' placeholder='Details about target'></textarea>"

            yield "<hr>"
            yield f"<p> Start vector type: {start_vector_type}</p>"

            r = []
            for vector_type in Config.GetConfig()["vector_types"]:
                if vector_type == start_vector_type:
                    for field in Config.GetConfig()["vector_types"][vector_type]:
                        if Config.GetConfig()["vector_types"][vector_type][field] == "text":
                            yield f"<label for='{field}'>{field}:</label>"
                            yield f"<input type='text' id='{field}'/>"
                            r.append(f'{field}:document.getElementById("{field}").value,')
                        elif Config.GetConfig()["vector_types"][vector_type][field] == "options":
                            yield f"<label for='{field}'>{field}:</label>"
                            yield f"<select id='{field}'>"
                            for opt in Config.GetConfig()[Config.GetConfig()["vector_types"][vector_type]["%" + field + "_opt!"]['option_list']]:
                                yield f"<option>{opt}</option>"
                            yield "</select>"
                            r.append(f'{field}:document.getElementsByTagName("option")[document.getElementById("{field}").selectedIndex].value,')
                    yield "<button id='submit'>Submit data</button>"
                    yield """<script>
        document.getElementById("submit").onclick = function () {
            resp = fetch("/api/target/post",{
            headers: {
                'Content-Type': 'application/json'
            },
            method:"POST",
            mode: "cors",
            body: JSON.stringify({ start_vector_type: '""" + start_vector_type + """' , details:document.getElementById("details").value}),
        })  .then((response) => response.json())
    .then((data) => {
                fetch("/api/vector/post",{
                method:"POST",
                headers: {
                    "Accept":"application/json", 
                    "Content-Type":"application/json"
                },
                mode: "cors",
                body: JSON.stringify({
                    type:'""" + start_vector_type + """',
                    """ + ''.join(r) + """
                    target_id:data.Target.Id,
                    is_starting:true
                })

        })
        window.location.href = '/target/view/' + data.Target.Id;
        })}
    </script>"""
    
    return flask.stream_with_context(generate())

@App.route("/target/view/<target_id>")
def ViewTarget(target_id):
    def generator():
        yield ''.join(Style.StylePage())
        yield "<h1>View Target</h1>"
        yield '<a href="/">Go back to Target dashboard</a>'
        yield "<hr>"
        
        conn,cursor = Conn.GetDBConnection()
        target = cursor.execute("SELECT id,start_vector_type,details FROM targets WHERE id=?",(target_id)).fetchone()
        v_data = cursor.execute(f"SELECT * FROM {target[1]}s WHERE target_id=? AND is_starting_vector=1",(target[0],)).fetchone()

        index = 0

        for x in Config.GetConfig()["vector_types"][target[1]]:
            if x.startswith("%"):
                pass
            else:
                yield f"<p>{x}: {v_data[index]}</p>"
                index = index + 1
                
        yield f"<p>Id: {target[0]}</p> <p>Details: {target[2]}</p>"
        yield "<hr>"

        for l in Config.GetConfig()["vector_types"]:
            data = cursor.execute(f"SELECT * FROM {l}s WHERE target_id=? AND is_starting_vector=0",(target[0],)).fetchall()

            for dataz in data:
                index = 0
                for x in Config.GetConfig()["vector_types"][l]:
                    if x.startswith("%"):
                        pass
                    else:
                        try:
                            yield f"<p>{x}: {dataz[index]}</p>"
                            index = index + 1
                        except:
                            pass
                yield "<hr>"
                        
        
        try:
            yield f"<p id='vector_type'>Selected vector type: {request.args["vt"]}<p/>"
            r = []
            for vector_type in Config.GetConfig()["vector_types"]:
                if vector_type == request.args["vt"]:
                    for field in Config.GetConfig()["vector_types"][vector_type]:
                        if Config.GetConfig()["vector_types"][vector_type][field] == "text":
                            yield f"<label for='{field}'>{field}:</label>"
                            yield f"<input type='text' id='{field}'/>"
                            r.append(f'{field}:document.getElementById("{field}").value,')
                        elif Config.GetConfig()["vector_types"][vector_type][field] == "options":
                            yield f"<label for='{field}'>{field}:</label>"
                            yield f"<select id='{field}'>"
                            for opt in Config.GetConfig()[Config.GetConfig()["vector_types"][vector_type]["%" + field + "_opt!"]['option_list']]:
                                yield f"<option>{opt}</option>"
                            yield "</select>"
                            r.append(f'{field}:document.getElementsByTagName("option")[document.getElementById("{field}").selectedIndex].value,')
                    yield "<button id='submit'>Submit data</button>"
                    yield """<script>
        document.getElementById("submit").onclick = function () {
                fetch("/api/vector/post",{
                method:"POST",
                headers: {
                    "Accept":"application/json", 
                    "Content-Type":"application/json"
                },
                mode: "cors",
                body: JSON.stringify({
                    type:'""" + request.args["vt"] + """',
                    """ + ''.join(r) + """
                    target_id:""" + target_id + """,
                    is_starting:false
                    })
                })

                window.location.href = '/target/view/""" + target_id + """'
        }
    </script>"""
        except:
            yield "<label for='vector_type'>Add a new vector to target:</label>"
            yield "<select id='vector_type'>"
            yield "<option>Select One</option>"
            for vector_type in Config.GetConfig()["vector_types"]:
                yield f"<option>{vector_type}</option>"
            yield "</select>"

        yield '<script>document.getElementById("vector_type").onchange = function(){if (document.getElementsByTagName("option")[document.getElementById("vector_type").selectedIndex].value != "Select One") {window.location.href = "/target/view/'+target_id+'?vt=" + document.getElementsByTagName("option")[document.getElementById("vector_type").selectedIndex].value}}</script>'

        Conn.EndDBConnection(conn,cursor)

    return flask.stream_with_context(generator())


@App.route("/api/target/post",methods=["POST"])
def TPostApi():

    start_vector_type = request.get_json()["start_vector_type"]

    try:
        details = request.get_json()["details"]
    except KeyError:
        details = None

    conn,cursor = Conn.GetDBConnection()

    cursor.execute("INSERT INTO targets(details,start_vector_type) VALUES (?,?)",(details,start_vector_type,))
    
    id = cursor.lastrowid

    Conn.EndDBConnection(conn,cursor)

    return flask.jsonify({"Message":"Target data was inserted succesfully!","Target":{"Id":id}})

@App.route("/api/vector/post",methods=["POST"])
def VPostApi():
    vector_type = request.get_json()["type"]
    target_id = request.get_json()["target_id"]

    try:
        is_starting = request.get_json()["is_starting"]
    except:
        is_starting = False   

    if is_starting == False:
        is_starting = 0
    elif is_starting == True:
        is_starting = 1

    conn,cursor = Conn.GetDBConnection()

    fields = Config.GetConfig()["vector_types"][vector_type]

    g = []
    for param in request.get_json():
        if param in fields:
            g.append(param)

    v=[]
    for param in request.get_json():
        if param in fields:
            v.append(request.get_json()[param])

    cursor.execute(f"INSERT INTO {vector_type + "s"}({','.join(g)},target_id,is_starting_vector) VALUES ({len(g) * "?,"}?,?)",(*v,target_id,is_starting),)
    
    id = cursor.lastrowid

    Conn.EndDBConnection(conn,cursor)

    return flask.jsonify({"Message":"Vector Data was inserted succesfully!","Vector":{"Id":id}})

waitress.serve(App,listen='0.0.0.0:1642 ')