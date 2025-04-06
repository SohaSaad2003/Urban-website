document.addEventListener('DOMContentLoaded', () => {
    const upload1 = document.getElementById('upload1');
    const upload2 = document.getElementById('upload2');
    const preview1 = document.getElementById('preview1');
    const preview2 = document.getElementById('preview2');
    const image1Input = document.getElementById('image1');
    const image2Input = document.getElementById('image2');
    const detectButton = document.getElementById('detectButton');
    const loadingIndicator = document.querySelector('.loading-indicator');
    
    let image1Loaded = false;
    let image2Loaded = false;

    // Create floating particles
    createFloatingParticles();

    function createFloatingParticles() {
        const particles = document.querySelector('.particles');
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

    // Create glowing lines
    createGlowLines();

    function createGlowLines() {
        const glowLines = document.querySelector('.glow-lines');
        for (let i = 0; i < 5; i++) {
            const line = document.createElement('div');
            line.className = 'glow-line';
            line.style.left = `${Math.random() * 100}%`;
            line.style.animationDuration = `${Math.random() * 3 + 2}s`;
            line.style.animationDelay = `${Math.random() * 2}s`;
            glowLines.appendChild(line);
        }
    }

    // Handle clicks on upload boxes
    [upload1, upload2].forEach(uploadBox => {
        uploadBox.addEventListener('click', () => {
            const input = uploadBox.querySelector('input[type="file"]');
            input.click();
        });

        // Prevent click propagation from preview area if image is already loaded
        uploadBox.querySelector('.preview').addEventListener('click', (e) => {
            if (uploadBox.classList.contains('has-image')) {
                e.stopPropagation();
            }
        });

        // Enhanced drag and drop handling
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadBox.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        uploadBox.addEventListener('dragenter', () => {
            uploadBox.classList.add('dragover');
            uploadBox.querySelector('.hologram-effect').style.opacity = '1';
            
            // Add pulsing effect to icon
            const icon = uploadBox.querySelector('.upload-content i');
            icon.style.transform = 'scale(1.2)';
            icon.style.filter = 'brightness(1.5)';
        });

        uploadBox.addEventListener('dragleave', () => {
            uploadBox.classList.remove('dragover');
            uploadBox.querySelector('.hologram-effect').style.opacity = '0.5';
            
            // Reset icon effects
            const icon = uploadBox.querySelector('.upload-content i');
            icon.style.transform = 'scale(1)';
            icon.style.filter = 'none';
        });

        uploadBox.addEventListener('drop', (e) => {
            uploadBox.classList.remove('dragover');
            uploadBox.querySelector('.hologram-effect').style.opacity = '0.5';
            
            // Reset icon effects
            const icon = uploadBox.querySelector('.upload-content i');
            icon.style.transform = 'scale(1)';
            icon.style.filter = 'none';
            
            const file = e.dataTransfer.files[0];
            if (file && file.type.startsWith('image/')) {
                const input = uploadBox.querySelector('input[type="file"]');
                input.files = e.dataTransfer.files;
                handleFileSelect(input);
            }
        });
    });

    // Enhanced file selection handler
    function handleFileSelect(input) {
        const file = input.files[0];
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            const preview = input.id === 'image1' ? preview1 : preview2;
            const uploadBox = input.closest('.upload-box');
            
            // Add loading state
            uploadBox.classList.add('loading');
            
            reader.onload = (e) => {
                // Create and set up image element
                const img = document.createElement('img');
                img.src = e.target.result;
                
                // Clear previous content
                preview.innerHTML = '';
                preview.appendChild(img);
                
                // Add active class and effects
                preview.classList.add('active');
                uploadBox.classList.add('has-image');
                
                // Create and append new effects
                const scanEffect = document.createElement('div');
                scanEffect.className = 'scan-effect';
                preview.appendChild(scanEffect);
                
                const analysisGrid = document.createElement('div');
                analysisGrid.className = 'analysis-grid';
                preview.appendChild(analysisGrid);
                
                if (input.id === 'image1') {
                    image1Loaded = true;
                } else {
                    image2Loaded = true;
                }
                
                updateDetectButton();
                uploadBox.classList.remove('loading');
                
                // Trigger hologram effect
                uploadBox.querySelector('.hologram-effect').style.animation = 'hologramShift 3s ease-in-out infinite';
                
                // Hide upload content when image is loaded
                const uploadContent = uploadBox.querySelector('.upload-content');
                uploadContent.style.opacity = '0';
                setTimeout(() => {
                    uploadContent.style.display = 'none';
                }, 300);
            };
            
            reader.readAsDataURL(file);
        }
    }

    // Enhanced detect button state update
    function updateDetectButton() {
        const wasDisabled = detectButton.disabled;
        detectButton.disabled = !(image1Loaded && image2Loaded);
        
        if (wasDisabled && !detectButton.disabled) {
            detectButton.classList.add('ready');
            // Add glitch effect
            detectButton.querySelector('.button-glitch').style.animation = 'glitchEffect 3s linear infinite';
            setTimeout(() => detectButton.classList.remove('ready'), 1000);
        }
    }

    // Handle file input change
    image1Input.addEventListener('change', () => handleFileSelect(image1Input));
    image2Input.addEventListener('change', () => handleFileSelect(image2Input));

    // Enhanced detect button click handler
    detectButton.addEventListener('click', async () => {
        if (detectButton.disabled) return;

        // Show loading indicator with animation
        loadingIndicator.classList.remove('hidden');
        detectButton.disabled = true;
        
        // Add processing animation to result boxes
        document.querySelectorAll('.result-box').forEach(box => {
            box.classList.add('processing');
            const overlay = box.querySelector('.analysis-overlay');
            if (overlay) {
                overlay.style.animation = 'scanMove 2s linear infinite';
            }
        });

        try {
            // Create FormData and append images
            const formData = new FormData();
            formData.append('image1', image1Input.files[0]);
            formData.append('image2', image2Input.files[0]);

            // Send request to backend
            const response = await fetch('/process_images', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to process images');
            }

            const data = await response.json();

            // Display results
            const changeMap1 = document.getElementById('changeMap1');
            const changeMap2 = document.getElementById('changeMap2');

            // Clear previous content
            changeMap1.innerHTML = '';
            changeMap2.innerHTML = '';

            // Create and append new images
            const img1 = document.createElement('img');
            const img2 = document.createElement('img');

            img1.src = data.change_map1;
            img2.src = data.change_map2;

            img1.style.maxWidth = '100%';
            img2.style.maxWidth = '100%';

            // Add click handlers for image enlargement
            [img1, img2].forEach(img => {
                img.addEventListener('click', () => {
                    showImageModal(img.src);
                });
            });

            changeMap1.appendChild(img1);
            changeMap2.appendChild(img2);

            // Show result info sections
            const resultInfos = document.querySelectorAll('.result-info');
            resultInfos.forEach(info => {
                info.classList.remove('hidden');
                // Update timestamp with Arabic locale
                const timeValue = info.querySelector('.time-value');
                const now = new Date();
                const options = {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit',
                    hour12: true
                };
                timeValue.textContent = now.toLocaleDateString('ar-EG', options);
            });

            // Add download handlers
            const downloadButtons = document.querySelectorAll('.download-btn');
            downloadButtons[0].onclick = () => downloadImage(data.change_map1, 'map1_red.jpg');
            downloadButtons[1].onclick = () => downloadImage(data.change_map2, 'map1_bw.jpg');

            // Add success effects
            document.querySelectorAll('.result-box').forEach(box => {
                box.classList.add('success');
                setTimeout(() => box.classList.remove('success'), 2000);
            });

        } catch (error) {
            console.error('Error:', error);
            // Show error message to user
            const errorMessage = document.createElement('div');
            errorMessage.className = 'error-message';
            errorMessage.textContent = error.message;
            document.querySelector('.results-section').prepend(errorMessage);
            
            // Remove error message after 5 seconds
            setTimeout(() => errorMessage.remove(), 5000);

        } finally {
            // Hide loading indicator
            loadingIndicator.classList.add('hidden');
            detectButton.disabled = false;
            
            // Remove processing animation
            document.querySelectorAll('.result-box').forEach(box => {
                box.classList.remove('processing');
                const overlay = box.querySelector('.analysis-overlay');
                if (overlay) {
                    overlay.style.animation = 'none';
                }
            });
        }
    });

    // Add hover effects for upload boxes
    [upload1, upload2].forEach(uploadBox => {
        uploadBox.addEventListener('mouseover', () => {
            const icon = uploadBox.querySelector('.upload-content i');
            icon.style.transform = 'scale(1.1) rotate(5deg)';
            uploadBox.querySelector('.hologram-effect').style.opacity = '0.8';
        });

        uploadBox.addEventListener('mouseout', () => {
            const icon = uploadBox.querySelector('.upload-content i');
            icon.style.transform = 'scale(1) rotate(0deg)';
            uploadBox.querySelector('.hologram-effect').style.opacity = '0.5';
        });
    });

    // Add parallax effect to cyber background
    document.addEventListener('mousemove', (e) => {
        const moveX = (e.clientX - window.innerWidth / 2) * 0.01;
        const moveY = (e.clientY - window.innerHeight / 2) * 0.01;
        
        document.querySelector('.grid-overlay').style.transform = 
            `perspective(500px) rotateX(45deg) translate(${moveX}px, ${moveY}px)`;
    });
});

// Function to download images
async function downloadImage(imageSrc, fileName) {
    try {
        const response = await fetch(imageSrc);
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = fileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error downloading image:', error);
        // Show error message to user
        const errorMessage = document.createElement('div');
        errorMessage.className = 'error-message';
        errorMessage.textContent = 'Failed to download image. Please try again.';
        document.querySelector('.results-section').prepend(errorMessage);
        setTimeout(() => errorMessage.remove(), 5000);
    }
}

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