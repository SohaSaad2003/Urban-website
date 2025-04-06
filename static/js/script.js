document.addEventListener('DOMContentLoaded', () => {
    const splashScreen = document.getElementById('splash');
    const mainContent = document.getElementById('main');
    const slides = document.querySelectorAll('.slide');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const indicators = document.querySelectorAll('.indicator');
    let currentSlide = 0;
    const totalSlides = slides.length;
    
    // Show splash screen for 5 seconds
    setTimeout(() => {
        // Fade out splash screen
        splashScreen.classList.add('hidden');
        
        // Show main content after splash screen fades out
        setTimeout(() => {
            splashScreen.style.display = 'none';
            mainContent.style.display = 'block';
            
            // Add fade-in effect for main content
            mainContent.style.opacity = 0;
            setTimeout(() => {
                mainContent.style.transition = 'opacity 0.8s ease-in-out';
                mainContent.style.opacity = 1;
            }, 50);
        }, 800);
    }, 5000);

    // Function to handle circular navigation
    function getNextIndex(current, direction) {
        if (direction === 'next') {
            return (current + 1) % totalSlides;
        } else {
            return current === 0 ? totalSlides - 1 : current - 1;
        }
    }

    // Function to update slide with transition direction
    function updateSlide(newIndex, direction = 'next') {
        const currentSlideElement = slides[currentSlide];
        const newSlideElement = slides[newIndex];
        
        // Reset transforms
        slides.forEach(slide => {
            slide.style.transform = '';
            slide.style.transition = 'none';
            slide.classList.remove('active');
        });
        
        // Set initial positions
        if (direction === 'next') {
            newSlideElement.style.transform = 'translateX(50px)';
            currentSlideElement.style.transform = 'translateX(0)';
        } else {
            newSlideElement.style.transform = 'translateX(-50px)';
            currentSlideElement.style.transform = 'translateX(0)';
        }
        
        // Force reflow
        newSlideElement.offsetHeight;
        
        // Add transitions back
        newSlideElement.style.transition = 'all 0.8s ease-in-out';
        currentSlideElement.style.transition = 'all 0.8s ease-in-out';
        
        // Animate slides
        newSlideElement.style.transform = 'translateX(0)';
        currentSlideElement.style.transform = direction === 'next' ? 'translateX(-50px)' : 'translateX(50px)';
        
        // Update active states
        newSlideElement.classList.add('active');
        indicators.forEach(indicator => indicator.classList.remove('active'));
        indicators[newIndex].classList.add('active');
        
        currentSlide = newIndex;
    }

    // Event listeners for navigation
    prevBtn.addEventListener('click', () => {
        updateSlide(getNextIndex(currentSlide, 'prev'), 'prev');
    });

    nextBtn.addEventListener('click', () => {
        updateSlide(getNextIndex(currentSlide, 'next'), 'next');
    });

    // Event listeners for indicators
    indicators.forEach((indicator, index) => {
        indicator.addEventListener('click', () => {
            if (index === currentSlide) return;
            const direction = index > currentSlide ? 'next' : 'prev';
            updateSlide(index, direction);
        });
    });

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') {
            updateSlide(getNextIndex(currentSlide, 'prev'), 'prev');
        } else if (e.key === 'ArrowRight') {
            updateSlide(getNextIndex(currentSlide, 'next'), 'next');
        }
    });

    // Touch navigation
    let touchStartX = 0;
    let touchEndX = 0;
    
    document.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
    });

    document.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    });

    function handleSwipe() {
        const swipeThreshold = 50;
        const diff = touchStartX - touchEndX;
        
        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0) {
                // Swipe left, go next
                updateSlide(getNextIndex(currentSlide, 'next'), 'next');
            } else {
                // Swipe right, go prev
                updateSlide(getNextIndex(currentSlide, 'prev'), 'prev');
            }
        }
    }
});
