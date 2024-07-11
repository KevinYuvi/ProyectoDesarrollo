let currentSlide = 0;

function showSlide(index) {
    const slides = document.querySelectorAll('.carousel-item');
    if (index >= slides.length) {
        currentSlide = 0;
    } else if (index < 0) {
        currentSlide = slides.length - 1;
    } else {
        currentSlide = index;
    }
    document.querySelector('.carousel-inner').style.transform = `translateX(-${currentSlide * 100}%)`;
}

function moveSlide(n) {
    showSlide(currentSlide + n);
}

document.addEventListener('DOMContentLoaded', () => {
    showSlide(currentSlide);
    setInterval(() => moveSlide(1), 3000); // Cambia de diapositiva cada 3 segundos
});

//Beneficios 
function toggleAdditionalBenefits() {
    var additionalBenefits = document.getElementById('additionalBenefits');
    var showMoreBtn = document.getElementById('showMoreBtn');

    if (additionalBenefits.style.display === 'none') {
        additionalBenefits.style.display = 'block';
        showMoreBtn.textContent = 'Ver menos beneficios';
    } else {
        additionalBenefits.style.display = 'none';
        showMoreBtn.textContent = 'Ver más beneficios';
    }
}
 

