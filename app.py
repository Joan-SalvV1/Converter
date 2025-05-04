from flask import Flask, render_template, request, send_file, flash, redirect
from PIL import Image
import os
from io import BytesIO

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'your_secret_key_here'

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Supported formats
SUPPORTED_INPUT_FORMATS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
SUPPORTED_OUTPUT_FORMATS = {
    'ico': [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    'png': [(256, 256), (512, 512), (1024, 1024)],
    'jpg': [(256, 256), (512, 512), (1024, 1024)],
    'jpeg': [(256, 256), (512, 512), (1024, 1024)],
    'webp': [(256, 256), (512, 512), (1024, 1024)],
    'bmp': [(256, 256), (512, 512), (1024, 1024)],
    'tiff': [(256, 256), (512, 512), (1024, 1024)],
    'pdf': [(256, 256)]
}

QUALITY_OPTIONS = {
    'jpeg': [10, 30, 50, 70, 90],
    'webp': [10, 30, 50, 70, 90]
}

def convert_image(input_path, output_path, output_format, sizes=None):
    try:
        with Image.open(input_path) as img:
            # Convertir a RGB si es necesario
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            if output_format == 'ico':
                # Convertir a ICO con múltiples tamaños
                if sizes is None:
                    sizes = SUPPORTED_OUTPUT_FORMATS['ico']
                
                icon_sizes = [img.resize(s, Image.Resampling.LANCZOS) for s in sizes]
                icon_sizes[0].save(
                    output_path,
                    format="ICO",
                    append_images=icon_sizes[1:],
                    quality=100,
                    bitdepth=32
                )
            else:
                # Convertir a otros formatos
                if sizes:
                    img = img.resize(sizes[0], Image.Resampling.LANCZOS)
                
                # Guardar con el formato correcto
                img.save(output_path, format=output_format.upper())
                
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
            # Obtener parámetros del formulario
            output_format = request.form.get('output_format')
            selected_sizes = request.form.getlist('sizes')
            sizes = [tuple(map(int, size.split(','))) for size in selected_sizes] if selected_sizes else None
            
            # Validar parámetros
            if output_format not in SUPPORTED_OUTPUT_FORMATS:
                flash('Invalid output format', 'error')
                return redirect(request.url)
            
            # Generar nombre de archivo único
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            output_filename = os.path.splitext(filename)[0] + f'.{output_format.lower()}'
            file.save(filename)
            
            if convert_image(filename, output_filename, output_format, sizes):
                # Devolver el archivo convertido
                return send_file(
                    output_filename,
                    as_attachment=True,
                    download_name=os.path.basename(output_filename)
                )
                
            # Limpieza
            os.remove(filename)
            if os.path.exists(output_filename):
                os.remove(output_filename)
                
    return render_template('index.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in SUPPORTED_INPUT_FORMATS

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)