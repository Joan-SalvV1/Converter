document.addEventListener('DOMContentLoaded', () => {
    // File upload handling
    const fileInput = document.getElementById('file');
    const uploadArea = document.querySelector('.upload-area');
    const previewContainer = document.getElementById('preview-container');
    const previewImage = document.getElementById('preview-image');

    // Click handler
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
        uploadArea.style.borderColor = 'var(--secondary-color)';
        uploadArea.style.background = 'rgba(91, 164, 230, 0.1)';
    }

    function unhighlight(e) {
        e.preventDefault();
        e.stopPropagation();
        uploadArea.style.borderColor = 'var(--primary-color)';
        uploadArea.style.background = 'rgba(42, 92, 130, 0.05)';
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
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            fileInput.files = dataTransfer.files;
            
            previewContainer.classList.remove('d-none');
            previewImage.src = URL.createObjectURL(file);
            
            document.querySelector('form').classList.remove('was-validated');
        }
    }

    // File input change handler
    fileInput.addEventListener('change', function(e) {
        handleFiles(this.files);
    });

    // File validation
    function allowedFile(filename) {
        return filename.toLowerCase().endsWith('.png');
    }

    // Size selection styling
    document.querySelectorAll('.size-option').forEach(option => {
        option.addEventListener('click', () => {
            const checkbox = option.querySelector('input[type="checkbox"]');
            checkbox.checked = !checkbox.checked;
            option.classList.toggle('selected', checkbox.checked);
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
    })();
});