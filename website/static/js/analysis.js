document.addEventListener('DOMContentLoaded', () => {
    const uploadBox = document.getElementById('uploadBox');
    const imagePreview = document.getElementById('imagePreview');
    const fileInput = document.getElementById('fileInput');
    const analyzeButton = document.getElementById('analysisBtn');
    const loadingIndicator = document.querySelector('.loading-indicator');
    
    let imageLoaded = false;

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

    // Handle click on upload box
    uploadBox.addEventListener('click', () => {
        if (!imageLoaded) {
            fileInput.click();
        }
    });

    // Prevent click propagation from preview area if image is loaded
    imagePreview.addEventListener('click', (e) => {
        if (imageLoaded) {
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
        if (!imageLoaded) {
            uploadBox.classList.add('dragover');
            uploadBox.querySelector('.hologram-effect').style.opacity = '1';
            
            // Add pulsing effect to icon
            const icon = uploadBox.querySelector('.upload-content i');
            icon.style.transform = 'scale(1.2)';
            icon.style.filter = 'brightness(1.5)';
        }
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
        if (!imageLoaded) {
            uploadBox.classList.remove('dragover');
            uploadBox.querySelector('.hologram-effect').style.opacity = '0.5';
            
            // Reset icon effects
            const icon = uploadBox.querySelector('.upload-content i');
            icon.style.transform = 'scale(1)';
            icon.style.filter = 'none';
            
            const file = e.dataTransfer.files[0];
            if (file && file.type.startsWith('image/')) {
                fileInput.files = e.dataTransfer.files;
                handleFileSelect(fileInput);
            }
        }
    });

    // Enhanced file selection handler
    function handleFileSelect(input) {
        const file = input.files[0];
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            
            // Add loading state
            uploadBox.classList.add('loading');
            
            reader.onload = (e) => {
                // Create and set up image element
                const img = document.createElement('img');
                img.src = e.target.result;
                
                // Clear previous content
                imagePreview.innerHTML = '';
                imagePreview.appendChild(img);
                
                // Add active class and effects
                imagePreview.classList.add('active');
                uploadBox.classList.add('has-image');
                
                // Create and append new effects
                const scanEffect = document.createElement('div');
                scanEffect.className = 'scan-effect';
                imagePreview.appendChild(scanEffect);
                
                const analysisGrid = document.createElement('div');
                analysisGrid.className = 'analysis-grid';
                imagePreview.appendChild(analysisGrid);
                
                imageLoaded = true;
                updateAnalyzeButton();
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

    // Update analyze button state
    function updateAnalyzeButton() {
        const wasDisabled = analyzeButton.disabled;
        analyzeButton.disabled = !imageLoaded;
        
        if (wasDisabled && !analyzeButton.disabled) {
            analyzeButton.classList.add('ready');
            setTimeout(() => analyzeButton.classList.remove('ready'), 1000);
        }
    }

    // Handle file input change
    fileInput.addEventListener('change', () => handleFileSelect(fileInput));

    // Handle analyze button click
    analyzeButton.addEventListener('click', async () => {
        if (analyzeButton.disabled || !imageLoaded) return;

        // Show loading state
        analyzeButton.disabled = true;
        const buttonText = analyzeButton.textContent;
        analyzeButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';

        try {
            // Create FormData and append image
            const formData = new FormData();
            formData.append('image', fileInput.files[0]);

            // Send request to backend
            const response = await fetch('/analyze_image', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            console.log('Response from server:', data); // Debug log

            if (!response.ok || !data.success) {
                throw new Error(data.error || 'Analysis failed');
            }

            updateResults(data);

        } catch (error) {
            console.error('Analysis error:', error);
            showNotification(error.message || 'Analysis failed. Please try again.', 'error');
        } finally {
            // Reset button state
            analyzeButton.disabled = false;
            analyzeButton.innerHTML = `
                <span class="button-text">
                    <i class="fas fa-chart-line"></i>
                    Start Analysis
                </span>
                <div class="button-glow"></div>
                <div class="button-scanline"></div>
            `;
        }
    });

    // Update results in the UI
    function updateResults(results) {
        console.log('Updating results with:', results); // Debug log

        if (!results.success) {
            showNotification(results.error || 'Analysis failed', 'error');
            return;
        }

        try {
            // Update land change and empty land percentages
            updatePercentage('landChange', results.landChange);
            updatePercentage('emptyLand', results.emptyLand);
            
            // Update vegetation stats
            updatePercentage('denseVeg', results.denseVeg);
            updatePercentage('lowVeg', results.lowVeg);
            updatePercentage('nonVeg', results.nonVeg);

            // Update classification image
            const classificationContainer = document.querySelector('[data-image="classification"] .result-content');
            if (classificationContainer && results.classificationImage) {
                console.log('Setting classification image:', results.classificationImage); // Debug log
                classificationContainer.innerHTML = `
                    <img src="${results.classificationImage}" alt="Classification Result" style="width: 100%; height: 100%; object-fit: contain;">
                `;
            } else {
                console.error('Classification container not found or image URL missing');
            }

            // Update NDVI image
            const ndviContainer = document.querySelector('[data-image="ndvi"] .result-content');
            if (ndviContainer && results.ndviImage) {
                console.log('Setting NDVI image:', results.ndviImage); // Debug log
                ndviContainer.innerHTML = `
                    <img src="${results.ndviImage}" alt="NDVI Analysis Result" style="width: 100%; height: 100%; object-fit: contain;">
                `;
            } else {
                console.error('NDVI container not found or image URL missing');
            }

            // Show success message
            showNotification('Analysis completed successfully!', 'success');
        } catch (error) {
            console.error('Error updating results:', error);
            showNotification('Error updating results', 'error');
        }
    }

    // Update percentage displays with animation
    function updatePercentage(id, value) {
        console.log(`Updating percentage for ${id} with value ${value}`); // Debug log
        const box = document.querySelector(`[data-stat="${id}"]`);
        if (box) {
            const valueElement = box.querySelector('.percentage-value');
            const barElement = box.querySelector('.bar-fill');
            
            if (valueElement) {
                // Update the number with the percentage symbol
                const roundedValue = Math.round(value * 10) / 10; // Round to 1 decimal place
                valueElement.innerHTML = `${roundedValue}<span class="percentage-symbol">%</span>`;
            }
            
            if (barElement) {
                // Animate the bar fill
                barElement.style.transition = 'width 1s ease-in-out';
                barElement.style.width = `${value}%`;
            }
        } else {
            console.error(`Element with data-stat="${id}" not found`);
        }
    }

    // Add hover effects for upload box
    uploadBox.addEventListener('mouseover', () => {
        if (!imageLoaded) {
            const icon = uploadBox.querySelector('.upload-content i');
            icon.style.transform = 'scale(1.1) rotate(5deg)';
            uploadBox.querySelector('.hologram-effect').style.opacity = '0.8';
        }
    });

    uploadBox.addEventListener('mouseout', () => {
        const icon = uploadBox.querySelector('.upload-content i');
        icon.style.transform = 'scale(1) rotate(0deg)';
        uploadBox.querySelector('.hologram-effect').style.opacity = '0.5';
    });

    // Add parallax effect to cyber background
    document.addEventListener('mousemove', (e) => {
        const moveX = (e.clientX - window.innerWidth / 2) * 0.01;
        const moveY = (e.clientY - window.innerHeight / 2) * 0.01;
        
        document.querySelector('.grid-overlay').style.transform = 
            `perspective(500px) rotateX(45deg) translate(${moveX}px, ${moveY}px)`;
    });

    // Add notification function
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('show');
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => notification.remove(), 300);
            }, 3000);
        }, 100);
    }
}); 