
import sqlite3
import flask

from flask import request

from core import Innit
from core import Conn
from core import Config

App = flask.Flask(__name__)

Innit.GenerateDBStructure()

@App.route("/")
def LandingPage():
    conn,cursor = Conn.GetDBConnection()
    yield "<h1>Anti-furry OSINT DB Dashboard</h1>"
    yield "<hr>"
    
    targets = cursor.execute("SELECT id,start_vector_type,details FROM targets").fetchall()
    targets.reverse() # Reverse the targets list to show the new ones at the top

    for target in targets:
        if target[1] == "username":
            username_data = cursor.execute("SELECT username,platform FROM usernames WHERE target_id=? AND is_starting_vector=1",(target[0],)).fetchone()
            start_vector_element = f"<p>Username: {username_data[0]}</p> <p>Platform: {username_data[1]}</p>"

        yield f"<p>Id: {target[0]}</p> {start_vector_element} <p>Details: {target[2]}</p>"
        yield f"<a href='/target/view/{target[0]}'>View target in more detail</a>"
        yield "<hr>"
    
    yield f"<a href='/target/upload'>Add a new target</a>"

    conn.commit()
    cursor.close()
    conn.close()

@App.route("/target/upload")
def UploadTarget():
    # To access request["args"] i needed to use stream_with_context()
    def generate():
        try:
            start_vector_type = request.args["svt"]
        except:
            start_vector_type = None

        yield "<h1>Upload Target</h1>"
        yield "<hr>"

        if start_vector_type == None:
            yield "<label for='start_vector_type'>Start vector type:</label>"
            yield "<select id='start_vector_type'><option>Select One</option><option>username</option></select>"
            yield '<script>document.getElementById("start_vector_type").onchange = function(){if (document.getElementsByTagName("option")[document.getElementById("start_vector_type").selectedIndex].value != "Select One") {window.location.href = "/target/upload?svt=" + document.getElementsByTagName("option")[document.getElementById("start_vector_type").selectedIndex].value}}</script>'
        else:
            yield "<textarea id='details' placeholder='Details about target'></textarea>"

            yield "<hr>"
            yield f"<p> Start vector type: {start_vector_type}</p>"

            if start_vector_type == "username":
                yield "<label for='username'>Username:</label>"
                yield "<input type='text' id='username'/>"
                yield "<label for='platform'>Platform:</label>"
                yield "<select id='platform'>"
                for platform in Config.GetConfig()["supported_platforms"]:
                    yield f"<option>{platform}</option>"
                yield "</select>"
                yield "<button id='submit'>Submit data</button>"
                yield """<script>
    document.getElementById("submit").onclick = function () {
        resp = fetch("/api/target/post",{
        headers: {
            'Content-Type': 'application/json'
        },
        method:"POST",
        mode: "cors",
        body: JSON.stringify({ start_vector_type: 'username' , details:document.getElementById("details").value}),
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
                type:'username',
                username:document.getElementById("username").value,
                platform:document.getElementsByTagName("option")[document.getElementById("platform").selectedIndex].value,
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
    yield "<h1>View Target</h1>"
    yield "<hr>"
    
    conn,cursor = Conn.GetDBConnection()
    target = cursor.execute("SELECT id,start_vector_type,details FROM targets WHERE id=?",(target_id)).fetchone()

    if target[1] == "username":
        username_data = cursor.execute("SELECT username,platform FROM usernames WHERE target_id=? AND is_starting_vector=1",(target[0],)).fetchone()
        start_vector_element = f"<p>Username: {username_data[0]}</p> <p>Platform: {username_data[1]}</p>"

    yield f"<p>Id: {target[0]}</p> {start_vector_element} <p>Details: {target[2]}</p>"
    yield "<hr>"

    conn.commit()
    cursor.close()
    conn.close()


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

    conn.commit()
    cursor.close()
    conn.close()

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

    # If the vector type is username
    if vector_type == "username":
        username = request.get_json()["username"]
        platform = request.get_json()["platform"]

        cursor.execute("INSERT INTO usernames(username,platform,target_id,is_starting_vector) VALUES (?,?,?,?)",(username,platform,target_id,is_starting),)

    id = cursor.lastrowid

    conn.commit()
    cursor.close()
    conn.close()

    return flask.jsonify({"Message":"Vector Data was inserted succesfully!","Vector":{"Id":id}})

App.run(port=80)