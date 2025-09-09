import os
import shortuuid
import qrcode
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename
from PIL import Image
from io import BytesIO
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['QRCODE_FOLDER'] = 'static/qrcodes'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Create directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['QRCODE_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def generate_short_id():
    return shortuuid.uuid()[:8]

@app.route('/')
def index():
    return render_template('index''.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        flash('No files selected')
        return redirect(request.url)
    
    files = request.files.getlist('files')
    
    if len(files) == 0 or files[0].filename == '':
        flash('No files selected')
        return redirect(url_for('index'))
    
    results = []
    
    for file in files:
        if file and allowed_file(file.filename):
            # Generate unique filename
            short_id = generate_short_id()
            filename = secure_filename(file.filename)
            file_extension = filename.rsplit('.', 1)[1].lower()
            new_filename = f"{short_id}.{file_extension}"
            
            # Save the file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
            file.save(file_path)
            
            # Generate URLs
            base_url = request.host_url
            short_link = f"{base_url}i/{short_id}"
            long_link = f"{base_url}static/uploads/{new_filename}"
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(short_link)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_filename = f"{short_id}.png"
            qr_path = os.path.join(app.config['QRCODE_FOLDER'], qr_filename)
            qr_img.save(qr_path)
            
            # Convert QR code to base64 for inline display
            buffered = BytesIO()
            qr_img.save(buffered, format="PNG")
            qr_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            results.append({
                'original_name': filename,
                'short_id': short_id,
                'short_link': short_link,
                'long_link': long_link,
                'qr_code': f"data:image/png;base64,{qr_base64}",
                'file_url': url_for('static', filename=f'uploads/{new_filename}')
            })
        else:
            flash(f'File {file.filename} is not an allowed image type')
    
    return render_template('index.html', results=results)

@app.route('/i/<short_id>')
def get_image(short_id):
    # Look for the file with the given short_id
    upload_dir = app.config['UPLOAD_FOLDER']
    for filename in os.listdir(upload_dir):
        if filename.startswith(short_id):
            return send_from_directory(upload_dir, filename)
    
    return "Image not found", 404

if __name__ == '__main__':
    app.run(debug=True)