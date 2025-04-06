document.addEventListener('DOMContentLoaded', () => {
    const upload = document.getElementById('upload1');
    const preview = document.getElementById('preview');
    const imageInput = document.getElementById('image');
    const detectButton = document.getElementById('detectButton');
    const loadingIndicator = document.querySelector('.loading-indicator');
    
    let imageLoaded = false;

    // Create floating particles
    createFloatingParticles();

    function createFloatingParticles() {
        const particles = document.querySelector('.particles');
        if (particles) {
            for (let i = 0; i < 50; i++) {
                const particle = document.createElement('div');
                particle.className = 'particle';
                particle.style.left = `${Math.random() * 100}%`;
                particle.style.top = `${Math.random() * 100}%`;
                particle.style.animationDuration = `${Math.random() * 3 + 2}s`;
                particle.style.animationDelay = `${Math.random() * 2}s`;
                particles.appendChild(particle);
            }
        }
    }

    // Create glowing lines
    createGlowLines();

    function createGlowLines() {
        const glowLines = document.querySelector('.glow-lines');
        if (glowLines) {
            for (let i = 0; i < 5; i++) {
                const line = document.createElement('div');
                line.className = 'glow-line';
                line.style.left = `${Math.random() * 100}%`;
                line.style.animationDuration = `${Math.random() * 3 + 2}s`;
                line.style.animationDelay = `${Math.random() * 2}s`;
                glowLines.appendChild(line);
            }
        }
    }

    // Handle click on upload box
    if (upload) {
        upload.addEventListener('click', () => {
            console.log('Upload box clicked');  // Debug log
            imageInput.click();
        });
    }

    // Handle file input change
    if (imageInput) {
        imageInput.addEventListener('change', (e) => {
            console.log('File input changed');  // Debug log
            handleFileSelect(imageInput);
        });
    }

    // Enhanced file selection handler
    function handleFileSelect(input) {
        console.log('Handling file selection');  // Debug log
        const file = input.files[0];
        if (file && file.type.startsWith('image/')) {
            console.log('Valid image file selected:', file.name);  // Debug log
            const reader = new FileReader();
            
            upload.classList.add('loading');
            
            reader.onload = (e) => {
                console.log('File loaded successfully');  // Debug log
                const img = document.createElement('img');
                img.src = e.target.result;
                
                preview.innerHTML = '';
                preview.appendChild(img);
                
                preview.classList.add('active');
                upload.classList.add('has-image');
                
                const scanEffect = document.createElement('div');
                scanEffect.className = 'scan-effect';
                preview.appendChild(scanEffect);
                
                const analysisGrid = document.createElement('div');
                analysisGrid.className = 'analysis-grid';
                preview.appendChild(analysisGrid);
                
                imageLoaded = true;
                updateDetectButton();
                upload.classList.remove('loading');
                
                const uploadContent = upload.querySelector('.upload-content');
                if (uploadContent) {
                    uploadContent.style.opacity = '0';
                    setTimeout(() => {
                        uploadContent.style.display = 'none';
                    }, 300);
                }
            };
            
            reader.onerror = (error) => {
                console.error('Error reading file:', error);  // Debug log
                alert('Error reading the selected file. Please try again.');
            };
            
            reader.readAsDataURL(file);
        } else {
            console.log('Invalid file type selected');  // Debug log
            alert('Please select a valid image file (PNG, JPG, or JPEG).');
        }
    }

    // Enhanced drag and drop handling
    if (upload) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            upload.addEventListener(eventName, preventDefaults, false);
        });

        upload.addEventListener('dragenter', () => {
            console.log('Drag enter');  // Debug log
            upload.classList.add('dragover');
            const hologram = upload.querySelector('.hologram-effect');
            if (hologram) hologram.style.opacity = '1';
            
            const icon = upload.querySelector('.upload-content i');
            if (icon) {
                icon.style.transform = 'scale(1.2)';
                icon.style.filter = 'brightness(1.5)';
            }
        });

        upload.addEventListener('dragleave', () => {
            console.log('Drag leave');  // Debug log
            upload.classList.remove('dragover');
            const hologram = upload.querySelector('.hologram-effect');
            if (hologram) hologram.style.opacity = '0.5';
            
            const icon = upload.querySelector('.upload-content i');
            if (icon) {
                icon.style.transform = 'scale(1)';
                icon.style.filter = 'none';
            }
        });

        upload.addEventListener('drop', (e) => {
            console.log('File dropped');  // Debug log
            upload.classList.remove('dragover');
            const hologram = upload.querySelector('.hologram-effect');
            if (hologram) hologram.style.opacity = '0.5';
            
            const icon = upload.querySelector('.upload-content i');
            if (icon) {
                icon.style.transform = 'scale(1)';
                icon.style.filter = 'none';
            }
            
            const file = e.dataTransfer.files[0];
            if (file && file.type.startsWith('image/')) {
                imageInput.files = e.dataTransfer.files;
                handleFileSelect(imageInput);
            } else {
                alert('Please drop a valid image file (PNG, JPG, or JPEG).');
            }
        });
    }

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Enhanced detect button state update
    function updateDetectButton() {
        const wasDisabled = detectButton.disabled;
        detectButton.disabled = !imageLoaded;
        
        if (wasDisabled && !detectButton.disabled) {
            detectButton.classList.add('ready');
            detectButton.querySelector('.button-glitch').style.animation = 'glitchEffect 3s linear infinite';
            setTimeout(() => detectButton.classList.remove('ready'), 1000);
        }
    }

    // Enhanced detect button click handler
    if (detectButton) {
        detectButton.addEventListener('click', async () => {
            if (!imageLoaded) {
                console.log('No image loaded');
                alert('Please upload an image first.');
                return;
            }

            console.log('Starting image processing');
            const loadingIndicator = document.querySelector('.loading-indicator');
            if (loadingIndicator) loadingIndicator.classList.remove('hidden');
            detectButton.disabled = true;

            try {
                const formData = new FormData();
                const fileInput = document.getElementById('image');
                if (!fileInput || !fileInput.files || !fileInput.files[0]) {
                    throw new Error('No file selected');
                }
                
                formData.append('image', fileInput.files[0]);
                console.log('Sending file:', fileInput.files[0].name);

                const response = await fetch('/process_image', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                console.log('Received response:', data);

                if (!data.success) {
                    throw new Error(data.error || 'Unknown error occurred');
                }

                // Update result images
                document.getElementById('referenceImage').innerHTML = `<img src="${data.reference_image}" alt="Reference Image">`;
                document.getElementById('currentImage').innerHTML = `<img src="${data.processed_image}" alt="Current Image">`;
                document.getElementById('diffMap').innerHTML = `<img src="${data.diff_map}" alt="Difference Map">`;
                document.getElementById('changesOverlay').innerHTML = `<img src="${data.contour_overlay}" alt="Changes Overlay">`;

                // Update analysis results
                document.getElementById('classifiedRegion').textContent = data.area || 'N/A';
                document.getElementById('detectedArea').textContent = formatNumber(data.total_change_area) || 'N/A';
                document.getElementById('confidence').textContent = data.confidence ? `${(data.confidence * 100).toFixed(2)}%` : 'N/A';
                document.getElementById('changePercentage').textContent = data.change_percentage ? `${data.change_percentage.toFixed(2)}%` : 'N/A';

                document.querySelector('.analysis-results').classList.remove('hidden');

            } catch (error) {
                console.error('Error processing image:', error);
                alert(`Error processing image: ${error.message}`);
            } finally {
                if (loadingIndicator) loadingIndicator.classList.add('hidden');
                detectButton.disabled = false;
            }
        });
    }

    function formatNumber(num) {
        if (num === undefined || num === null) return 'N/A';
        return num.toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    // Add hover effects for upload box
    upload.addEventListener('mouseover', () => {
        const icon = upload.querySelector('.upload-content i');
        icon.style.transform = 'scale(1.1) rotate(5deg)';
        upload.querySelector('.hologram-effect').style.opacity = '0.8';
    });

    upload.addEventListener('mouseout', () => {
        const icon = upload.querySelector('.upload-content i');
        icon.style.transform = 'scale(1) rotate(0deg)';
        upload.querySelector('.hologram-effect').style.opacity = '0.5';
    });

    // Add parallax effect to cyber background
    document.addEventListener('mousemove', (e) => {
        const moveX = (e.clientX - window.innerWidth / 2) * 0.01;
        const moveY = (e.clientY - window.innerHeight / 2) * 0.01;
        
        document.querySelector('.grid-overlay').style.transform = 
            `perspective(500px) rotateX(45deg) translate(${moveX}px, ${moveY}px)`;
    });
});

// Create modal for enlarged images
const modal = document.createElement('div');
modal.className = 'image-modal';
modal.innerHTML = `
    <div class="modal-content">
        <button class="close-modal"><i class="fas fa-times"></i></button>
        <img src="" alt="Enlarged map">
    </div>
`;
document.body.appendChild(modal);

// Function to show modal with enlarged image
function showImageModal(imageSrc) {
    const modalImg = modal.querySelector('img');
    modalImg.src = imageSrc;
    modal.classList.add('active');
}

// Close modal when clicking close button or outside the image
modal.addEventListener('click', (e) => {
    if (e.target === modal || e.target.closest('.close-modal')) {
        modal.classList.remove('active');
    }
});

// Close modal with escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.classList.contains('active')) {
        modal.classList.remove('active');
    }
}); 