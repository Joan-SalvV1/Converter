from flask import Flask, render_template, request, send_file, flash, redirect
from PIL import Image
import os
from io import BytesIO

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'your_secret_key_here'

# Supported formats
SUPPORTED_INPUT_FORMATS = {'png', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
SUPPORTED_OUTPUT_FORMATS = {
    'ico': [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    'png': [(256, 256), (512, 512), (1024, 1024)],
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

def convert_image(input_file, output_format, sizes=None):
    try:
        # Leer la imagen desde el archivo
        img = Image.open(input_file)
        
        # Convertir a RGB si es necesario
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Crear un buffer para el archivo de salida
        output_buffer = BytesIO()
        
        if output_format == 'ico':
            # Convertir a ICO con múltiples tamaños
            if sizes is None:
                sizes = SUPPORTED_OUTPUT_FORMATS['ico']
            
            icon_sizes = [img.resize(s, Image.Resampling.LANCZOS) for s in sizes]
            icon_sizes[0].save(
                output_buffer,
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
            img.save(output_buffer, format=output_format.upper())
            
        # Mover el puntero al inicio del buffer
        output_buffer.seek(0)
        return output_buffer
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return None

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
            
            # Convertir la imagen
            output_buffer = convert_image(file, output_format, sizes)
            
            if output_buffer:
                # Devolver el archivo convertido
                return send_file(
                    output_buffer,
                    as_attachment=True,
                    download_name=f'converted.{output_format.lower()}',
                    mimetype=f'image/{output_format}'
                )
                
            # Si hubo un error, redirigir
            return redirect(request.url)
    
    return render_template('index.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in SUPPORTED_INPUT_FORMATS

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)