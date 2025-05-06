document.addEventListener('DOMContentLoaded', () => {
    // File upload handling
    const fileInput = document.getElementById('file');
    const uploadArea = document.querySelector('.upload-area');
    const previewContainer = document.getElementById('preview-container');
    const previewImage = document.getElementById('preview-image');
    const loadingElement = document.getElementById('loading');
    const form = document.getElementById('converter-form');
    const downloadFrame = document.getElementById('download-frame');

    // Click handler for upload area
    uploadArea.addEventListener('click', () => fileInput.click());

    // Drag and drop handlers
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        e.preventDefault();
        e.stopPropagation();
        uploadArea.classList.add('dragover');
    }

    function unhighlight(e) {
        e.preventDefault();
        e.stopPropagation();
        uploadArea.classList.remove('dragover');
    }

    // Handle file drop
    uploadArea.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        e.preventDefault();
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            handleFiles(files);
        }
    }

    // Handle file selection
    function handleFiles(files) {
        const file = files[0];
        
        if (file && allowedFile(file.name)) {
            fileInput.files = files;
            previewFile(file);
        } else if (file) {
            alert('Unsupported file format. Please select an image in PNG, JPEG, GIF, BMP, TIFF, or WEBP format.');
        }
    }

    // File input change handler
    fileInput.addEventListener('change', function(e) {
        if (this.files.length > 0) {
            handleFiles(this.files);
        }
    });

    // File validation
    function allowedFile(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        return ['png', 'jpeg', 'jpg', 'gif', 'bmp', 'tiff', 'webp'].includes(ext);
    }

    // Preview image
    function previewFile(file) {
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                previewImage.src = e.target.result;
                previewContainer.classList.remove('d-none');
            };
            reader.readAsDataURL(file);
        }
    }

    // Output format selection styling
    document.querySelector('select[name="output_format"]').addEventListener('change', (e) => {
        const selected = e.target.value;
    });

    // Form submission handling
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Check if file is selected
        if (!fileInput.files.length) {
            alert('Please select an image to convert.');
            return;
        }

        // Check if output format is selected
        const outputFormat = document.querySelector('select[name="output_format"]').value;
        if (!outputFormat) {
            alert('Please select an output format.');
            return;
        }

        // Show loading
        if (loadingElement) {
            loadingElement.classList.remove('d-none');
        }
        
        // Usar fetch para una mejor compatibilidad y manejo de errores
        const formData = new FormData(form);
        
        fetch(form.action || window.location.href, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Server response error');
            }
            
            // Obtener el nombre del archivo del header Content-Disposition
            const contentDisposition = response.headers.get('content-disposition');
            let filename = 'converted';
            
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
                if (filenameMatch && filenameMatch[1]) {
                    filename = filenameMatch[1].replace(/['"]/g, '');
                }
            }
            
            // Si no se pudo obtener el nombre del header, usar el formato seleccionado
            if (filename === 'converted') {
                const outputFormat = document.querySelector('select[name="output_format"]').value;
                const originalFile = fileInput.files[0].name;
                const originalName = originalFile.lastIndexOf('.') > -1 
                    ? originalFile.substring(0, originalFile.lastIndexOf('.'))
                    : originalFile;
                filename = `${originalName}.${outputFormat}`;
            }
            
            return response.blob().then(blob => ({
                blob,
                filename
            }));
        })
        .then(({ blob, filename }) => {
            // Crear un enlace temporal para la descarga
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            
            // Limpiar
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            // Ocultar el indicador de carga
            if (loadingElement) {
                loadingElement.classList.add('d-none');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            if (loadingElement) {
                loadingElement.classList.add('d-none');
            }
            alert('There was an error processing the image. Please try again.');
        });
    });

    // Form validation
    (() => {
        'use strict'
        const forms = document.querySelectorAll('.needs-validation')
        Array.from(forms).forEach(form => {
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault()
                    event.stopPropagation()
                }
                form.classList.add('was-validated')
            }, false)
        })
    })()
});