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
    setInterval(() => moveSlide(1), 5000); // Cambia de diapositiva cada 3 segundos
});

//Beneficios 
function despliegue_beneficios() {
    var despliegue = document.getElementById('despliegue');
    var MostraMasBtn = document.getElementById('MostraMasBtn');

    if (despliegue.style.display === 'none') {
        despliegue.style.display = 'block';
        MostraMasBtn.textContent = 'Ver menos beneficios';
    } else {
        despliegue.style.display = 'none';
        MostraMasBtn.textContent = 'Ver más beneficios';
    }
}

