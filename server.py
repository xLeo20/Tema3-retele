import socket
import json
import os
import threading
from datetime import datetime

# Configuration
SERVER_HOST = 'localhost'
SERVER_PORT = 5000
FILES_DIR = 'files'
DEFAULT_USER = 'student'
DEFAULT_PASSWORD = '1234'

# Istoric global pentru operatiuni (Task Student)
operation_history = []

def add_to_history(username, action, details):
    """Adauga o actiune in istoricul serverului"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] User '{username}' {action} -> {details}"
    operation_history.append(log_entry)

def ensure_files_dir():
    """Ensure files directory exists"""
    if not os.path.exists(FILES_DIR):
        os.makedirs(FILES_DIR)
        print(f"✓ Directory '{FILES_DIR}' created")

def authenticate(username, password):
    """Authenticate user"""
    return username == DEFAULT_USER and password == DEFAULT_PASSWORD

def handle_client(conn, addr):
    """Handle client connection"""
    print(f"\n🔗 Client connected from {addr}")
    authenticated = False
    current_user = None
    
    try:
        while True:
            # Receive request
            request_data = conn.recv(4096).decode('utf-8')
            if not request_data:
                break
            
            try:
                request = json.loads(request_data)
                command = request.get('command')
                
                print(f"📨 Command received: {command}")
                
                # Authentication
                if command == 'login':
                    username = request.get('username')
                    password = request.get('password')
                    
                    if authenticate(username, password):
                        authenticated = True
                        current_user = username
                        response = {'status': 'success', 'message': f'Welcome {username}!'}
                        add_to_history(current_user, "LOGIN", "Logged into the system")
                        print(f"✓ User {username} authenticated")
                    else:
                        response = {'status': 'error', 'message': 'Invalid credentials'}
                        print(f"✗ Authentication failed for user {username}")
                
                elif not authenticated:
                    response = {'status': 'error', 'message': 'Not authenticated. Use login first'}
                
                # File operations
                elif command == 'create_file':
                    filename = request.get('filename')
                    content = request.get('content', '')
                    
                    filepath = os.path.join(FILES_DIR, filename)
                    with open(filepath, 'w') as f:
                        f.write(content)
                    
                    add_to_history(current_user, "CREATE", f"File '{filename}'")
                    response = {'status': 'success', 'message': f'File {filename} created on server'}
                    print(f"✓ File created: {filename}")
                
                elif command == 'upload':
                    filename = request.get('filename')
                    content = request.get('content')
                    
                    filepath = os.path.join(FILES_DIR, filename)
                    with open(filepath, 'w') as f:
                        f.write(content)
                    
                    add_to_history(current_user, "UPLOAD", f"File '{filename}'")
                    response = {'status': 'success', 'message': f'File {filename} uploaded'}
                    print(f"✓ File uploaded: {filename}")
                
                # --- STUDENT IMPLEMENTATIONS ---
                
                elif command == 'rename_file':
                    old_name = request.get('old_name')
                    new_name = request.get('new_name')
                    old_path = os.path.join(FILES_DIR, old_name)
                    new_path = os.path.join(FILES_DIR, new_name)
                    
                    if os.path.exists(old_path):
                        os.rename(old_path, new_path)
                        add_to_history(current_user, "RENAME", f"'{old_name}' to '{new_name}'")
                        response = {'status': 'success', 'message': f'File renamed from {old_name} to {new_name}'}
                        print(f"✓ File renamed: {old_name} -> {new_name}")
                    else:
                        response = {'status': 'error', 'message': f"File '{old_name}' does not exist"}
                
                elif command == 'read_file':
                    filename = request.get('filename')
                    filepath = os.path.join(FILES_DIR, filename)
                    
                    if os.path.exists(filepath):
                        with open(filepath, 'r') as f:
                            content = f.read()
                        add_to_history(current_user, "READ", f"File '{filename}'")
                        response = {'status': 'success', 'message': 'File read successfully', 'content': content}
                    else:
                        response = {'status': 'error', 'message': f"File '{filename}' does not exist"}
                
                elif command == 'download':
                    filename = request.get('filename')
                    filepath = os.path.join(FILES_DIR, filename)
                    
                    if os.path.exists(filepath):
                        with open(filepath, 'r') as f:
                            content = f.read()
                        add_to_history(current_user, "DOWNLOAD", f"File '{filename}'")
                        response = {'status': 'success', 'message': 'File downloaded successfully', 'content': content}
                        print(f"✓ File downloaded: {filename}")
                    else:
                        response = {'status': 'error', 'message': f"File '{filename}' does not exist"}
                
                elif command == 'edit_file':
                    filename = request.get('filename')
                    new_content = request.get('content')
                    filepath = os.path.join(FILES_DIR, filename)
                    
                    if os.path.exists(filepath):
                        with open(filepath, 'w') as f:
                            f.write(new_content)
                        add_to_history(current_user, "EDIT", f"File '{filename}'")
                        response = {'status': 'success', 'message': f"File '{filename}' successfully updated"}
                        print(f"✓ File edited: {filename}")
                    else:
                        response = {'status': 'error', 'message': f"File '{filename}' does not exist"}
                
                elif command == 'see_file_operation_history':
                    response = {'status': 'success', 'message': 'History retrieved', 'history': operation_history}
                    print(f"✓ History requested by {current_user}")
                
                # --- END STUDENT IMPLEMENTATIONS ---
                
                elif command == 'list_files':
                    files = os.listdir(FILES_DIR)
                    response = {'status': 'success', 'files': files}
                    print(f"✓ Files listed: {len(files)} files found")
                
                elif command == 'logout':
                    add_to_history(current_user, "LOGOUT", "Logged out of the system")
                    authenticated = False
                    current_user = None
                    response = {'status': 'success', 'message': 'Logged out'}
                    print(f"✓ User logged out")
                
                else:
                    response = {'status': 'error', 'message': f'Unknown command: {command}'}
                
            except Exception as e:
                response = {'status': 'error', 'message': str(e)}
                print(f"✗ Error: {str(e)}")
            
            # Send response
            conn.send(json.dumps(response).encode('utf-8'))
    
    except Exception as e:
        print(f"✗ Connection error: {str(e)}")
    finally:
        conn.close()
        print(f"🔌 Client disconnected from {addr}")

def start_server():
    """Start FTP server"""
    ensure_files_dir()
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)
    
    print("=" * 60)
    print("🚀 FTP SERVER STARTED")
    print("=" * 60)
    print(f"Host: {SERVER_HOST}")
    print(f"Port: {SERVER_PORT}")
    print(f"Files Directory: {FILES_DIR}")
    print(f"Default User: {DEFAULT_USER}")
    print(f"Default Password: {DEFAULT_PASSWORD}")
    print("=" * 60)
    
    try:
        while True:
            conn, addr = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.daemon = True
            client_thread.start()
    except KeyboardInterrupt:
        print("\n\n⛔ Server shutting down...")
    finally:
        server_socket.close()

if __name__ == '__main__':
    start_server()