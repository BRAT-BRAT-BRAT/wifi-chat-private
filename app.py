from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'wifi-chat-2026!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode=None)

# 🔒 CHANGE THIS TO YOUR WIFI (Step 2)
ALLOWED_IPS = ['192.168.1.36']  # WiFi only!

def is_wifi_client():
    client_ip = request.remote_addr.split(',')[0].strip()
    return any(client_ip.startswith(prefix) for prefix in ALLOWED_IPS)

HTML = '''
<!DOCTYPE html>
<html><head><title>🔒 Private WiFi Chat</title>
<meta charset="utf-8"><meta name="viewport" content="width=device-width">
<style>
body{font-family:Arial;margin:20px;background:#f0f0f0;}#chat{max-width:600px;margin:auto;background:white;border-radius:10px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.1);}
#status{padding:10px;background:#007bff;color:white;text-align:center;font-weight:bold;}
#messages{height:400px;overflow-y:auto;padding:15px;background:#fafafa;border-bottom:1px solid #eee;}
.msg{margin:8px 0;padding:8px;background:white;border-radius:8px;border-left:3px solid #007bff;}
.msg strong{color:#007bff;}img{max-width:200px;max-height:200px;border-radius:5px;}
form{padding:15px;background:white;display:flex;flex-wrap:wrap;gap:10px;}
input{padding:10px;border:1px solid #ddd;border-radius:5px;flex:1;min-width:150px;}
button{padding:10px 20px;background:#007bff;color:white;border:none;border-radius:5px;cursor:pointer;}
button:hover{background:#0056b3;}.time{font-size:0.85em;color:#666;}
</style></head><body>
<div id="chat">
<div id="status">Connecting...</div>
<div id="messages"></div>
<form id="msg-form">
<input id="name" placeholder="Your name" maxlength="20" required>
<input id="msg" placeholder="Type message..." required><button>📱 Send</button></form>
<form id="file-form"><input type="file" id="file" accept="image/*,.pdf,.txt"><button>🖼️ Send Image/File</button></form>
</div>
<script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
<script>
const socket=io({transports:['websocket']});const status=document.getElementById('status');
const msgs=document.getElementById('messages');const msgForm=document.getElementById('msg-form');
const fileForm=document.getElementById('file-form');const nameIn=document.getElementById('name');
const msgIn=document.getElementById('msg');const fileIn=document.getElementById('file');

function addMsg(html){const div=document.createElement('div');div.innerHTML=html;msgs.appendChild(div);msgs.scrollTop=msgs.scrollHeight;}

msgForm.onsubmit=e=>{e.preventDefault();const name=nameIn.value||'Anon';const text=msgIn.value.trim();if(text){socket.emit('chat',{name,text});msgIn.value='';}};

fileForm.onsubmit=e=>{e.preventDefault();const file=fileIn.files[0];if(file){const r=new FileReader();r.onload=ev=>{socket.emit('file',{name:file.name,data_url:ev.target.result,size:file.size})};r.readAsDataURL(file);fileIn.value='';}};

socket.on('connect',()=>status.innerHTML='✅ <strong>Connected!</strong> Private WiFi chat active');
socket.on('access_denied',()=>status.innerHTML='🚫 <strong>Access Denied</strong> - Wrong WiFi');
socket.on('chat',data=>{const t=new Date().toLocaleTimeString();addMsg(`<div class="msg"><strong>${data.name}</strong> <span class="time">[${t}]</span><br>${data.text}</div>`);});
socket.on('file',data=>{const t=new Date().toLocaleTimeString();const content=data.data_url.startsWith('data:image/')?'<br><img src="'+data.data_url+'" style="max-width:250px;">':'<br><a href="'+data.data_url+'" download="'+data.name+'" style="color:#28a745;">📎 Download '+data.name+' ('+(data.size/1024).toFixed(1)+'KB)</a>';addMsg(`<div class="msg"><strong>File:</strong> <span class="time">[${t}]</span>${content}</div>`);});
</script></body></html>
'''

@app.route('/')
def index():
    if not is_wifi_client(): return "🚫 Wrong WiFi network", 403
    return render_template_string(HTML)

@socketio.on('connect')
def connect(): 
    if not is_wifi_client(): emit('access_denied'); return False
    emit('status', 'Connected!')

@socketio.on('chat')
def chat(data): emit('chat', data, broadcast=True)

@socketio.on('file')
def file(data): emit('file', data, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    socketio.run(app, host='0.0.0.0', port=port)
