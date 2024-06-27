// script.js
const carousel = document.querySelector('.carousel');
const carouselItems = document.querySelectorAll('.carousel-item');
let slideIndex = 0;
let isTransitioning = false;

function moveCarousel() {
    if (isTransitioning) return; // Evitar iniciar una nueva transición si aún no ha terminado la anterior
    isTransitioning = true;

    // Calcular el ancho de un item del carrusel
    const itemWidth = carouselItems[0].offsetWidth;

    // Calcular el número total de items en el carrusel
    const totalItems = carouselItems.length;

    // Mover el carrusel al siguiente item
    slideIndex = (slideIndex + 1) % totalItems;

    // Calcular el offset para el movimiento
    let offset = -slideIndex * itemWidth;

    // Animar el movimiento del carrusel
    carousel.style.transition = 'transform 0.5s ease';
    carousel.style.transform = `translateX(${offset}px)`;

    // Esperar a que termine la transición antes de restablecer para iniciar de nuevo desde el primer div
    setTimeout(() => {
        isTransitioning = false;
        if (slideIndex === totalItems - 1) {
            // Si llegamos al último item, volver al primer item sin transición
            carousel.style.transition = 'none';
            carousel.style.transform = `translateX(0)`;
            slideIndex = 0;
        }
    }, 500); // Tiempo igual a la duración de la transición
}

setInterval(moveCarousel, 3000); // Cambia de item cada 3 segundos (3000 milisegundos)
