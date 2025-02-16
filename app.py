from flask import Flask, render_template, request, send_file, flash, redirect
from PIL import Image
import os
from io import BytesIO

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'your_secret_key_here'  # Needed for flash messages

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def convert_png_to_ico(input_path, output_path, sizes=[(256, 256)]):
    try:
        with Image.open(input_path) as img:
            if img.size[0] < max(s[0] for s in sizes):
                flash('Warning: Original image is smaller than requested sizes!', 'warning')
                
            icon_sizes = [img.resize(s, Image.Resampling.LANCZOS) for s in sizes]
            icon_sizes[0].save(
                output_path,
                format="ICO",
                append_images=icon_sizes[1:],
                quality=100,
                bitdepth=32
            )
            return True
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            # Get selected sizes from form
            selected_sizes = request.form.getlist('sizes')
            sizes = [tuple(map(int, size.split(','))) for size in selected_sizes]
            
            # Generate unique filename
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            ico_filename = os.path.splitext(filename)[0] + '.ico'
            file.save(filename)
            
            if convert_png_to_ico(filename, ico_filename, sizes):
                # Return the converted file
                return send_file(
                    ico_filename,
                    as_attachment=True,
                    download_name=os.path.basename(ico_filename)
                )
                
            # Cleanup
            os.remove(filename)
            if os.path.exists(ico_filename):
                os.remove(ico_filename)
                
    return render_template('index.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png'}

if __name__ == '__main__':
    app.run(debug=True)