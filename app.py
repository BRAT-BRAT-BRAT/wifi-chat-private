from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'group-chat-2026!'
socketio = SocketIO(app, cors_allowed_origins="*")

HTML = '''
<!DOCTYPE html>
<html>
<head>
<title>Group Chat - Share Photos</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width">
<style>
* {margin:0;padding:0;box-sizing:border-box;}
body {font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;padding:10px;}
.chat-container {max-width:800px;margin:0 auto;background:white;border-radius:20px;box-shadow:0 20px 40px rgba(0,0,0,0.1);overflow:hidden;}
.header {background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:20px;text-align:center;font-size:1.4em;font-weight:700;}
.messages {height:500px;overflow-y:auto;padding:20px;background:#f8f9ff;}
.message {margin-bottom:16px;padding:16px;background:white;border-radius:18px;box-shadow:0 2px 10px rgba(0,0,0,0.08);max-width:80%;}
.message strong {color:#667eea;display:block;margin-bottom:4px;}
.time {font-size:0.8em;color:#888;display:block;margin-top:4px;}
img {max-width:300px;max-height:300px;border-radius:12px;margin-top:8px;border:1px solid #eee;}
.download-link {color:#28a745!important;font-weight:500;text-decoration:none;padding:8px 16px;background:#d4edda;border-radius:20px;display:inline-block;margin-top:8px;}
.input-area {padding:24px;background:#f8f9ff;border-top:1px solid #eee;}
.input-group {display:flex;flex-wrap:wrap;gap:12px;max-width:100%;}
input[type=text],input[type=file] {flex:1;padding:16px;border:2px solid #e2e8f0;border-radius:12px;font-size:16px;min-width:160px;}
input:focus {outline:none;border-color:#667eea;}
.send-btn {padding:16px 32px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;border:none;border-radius:12px;font-size:16px;font-weight:600;cursor:pointer;flex-shrink:0;transition:all 0.2s;}
.send-btn:hover {transform:translateY(-1px);box-shadow:0 8px 25px rgba(102,126,234,0.4);}
.status {text-align:center;padding:12px;color:#666;font-style:italic;}
@media (max-width:600px) {.input-group{flex-direction:column;}.message{max-width:95%;}}
</style>
</head>
<body>
<div class="chat-container">
<div class="header">📱 Group Chat - Share Photos & Files</div>
<div class="status" id="status">Connecting...</div>
<div class="messages" id="messages"></div>
<div class="input-area">
<form class="input-group" id="text-form">
<input id="name" placeholder="Your name" maxlength="25" required>
<input id="message" placeholder="Type message..." required>
<button class="send-btn" type="submit">Send Message</button>
</form>
<form class="input-group" id="file-form">
<input type="file" id="file-input" accept="image/*,.pdf,.txt,.doc,.zip">
<button class="send-btn" type="submit">Send Photo/File</button>
</form>
</div>
</div>
<script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
<script>
const socket = io({timeout: 20000});
const statusEl = document.getElementById('status');
const messagesEl = document.getElementById('messages');
const textForm = document.getElementById('text-form');
const fileForm = document.getElementById('file-form');
const nameInput = document.getElementById('name');
const msgInput = document.getElementById('message');
const fileInput = document.getElementById('file-input');

function addMessage(name, text, isFile=false, fileData=null, timestamp=null) {
  const div = document.createElement('div
