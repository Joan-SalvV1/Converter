from flask import Flask, render_template, request, send_file, flash, redirect
from PIL import Image
import os
from io import BytesIO

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'your_secret_key_here'

# Supported formats
SUPPORTED_INPUT_FORMATS = {'png', 'jpeg', 'jpg', 'gif', 'bmp', 'tiff', 'webp'}
SUPPORTED_OUTPUT_FORMATS = {'ico', 'png', 'jpeg', 'webp', 'bmp', 'tiff', 'pdf'}

QUALITY_OPTIONS = {
    'jpeg': [10, 30, 50, 70, 90],
    'webp': [10, 30, 50, 70, 90]
}

def convert_image(input_file, output_format):
    try:
        # Leer la imagen desde el archivo
        img = Image.open(input_file)
        
        # Crear un buffer para el archivo de salida
        output_buffer = BytesIO()
        
        if output_format == 'ico':
            # Para ICO, necesitamos asegurarnos de que la imagen sea cuadrada y tenga un tamaño adecuado
            max_size = 256
            if img.size[0] > max_size or img.size[1] > max_size:
                # Redimensionar manteniendo la relación de aspecto
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Crear una imagen cuadrada con fondo transparente
            size = max(img.size)
            ico_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            
            # Pegar la imagen centrada en el lienzo cuadrado
            x = (size - img.size[0]) // 2
            y = (size - img.size[1]) // 2
            ico_img.paste(img, (x, y), img if img.mode == 'RGBA' else None)
            
            # Guardar como ICO
            ico_img.save(output_buffer, format='ICO', sizes=[(size, size)])
        else:
            # Para otros formatos, convertir a RGB si es necesario (excepto para formatos que soportan transparencia)
            if img.mode != 'RGB' and output_format not in ['png', 'webp', 'tiff']:
                img = img.convert('RGB')
            # Guardar manteniendo el tamaño original
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
            
            # Validar parámetros
            if output_format not in SUPPORTED_OUTPUT_FORMATS:
                flash('Invalid output format', 'error')
                return redirect(request.url)
            
            # Convertir la imagen
            output_buffer = convert_image(file, output_format)
            
            if output_buffer:
                # Devolver el archivo convertido
                # Configurar el mimetype correcto según el formato
                if output_format == 'ico':
                    mimetype = 'image/x-icon'
                elif output_format == 'pdf':
                    mimetype = 'application/pdf'
                else:
                    mimetype = f'image/{output_format}'
                
                try:
                    return send_file(
                        output_buffer,
                        as_attachment=True,
                        download_name=f'converted.{output_format.lower()}',
                        mimetype=mimetype
                    )
                except Exception as e:
                    app.logger.error(f"Error sending file: {str(e)}")
                    flash(f'Error al enviar el archivo: {str(e)}', 'error')
                    return redirect(request.url)
            else:
                flash('Error al convertir la imagen. Por favor, intenta con otra imagen o formato.', 'error')
    
    return render_template('index.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in SUPPORTED_INPUT_FORMATS

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)