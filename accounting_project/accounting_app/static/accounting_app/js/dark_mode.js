document.addEventListener('DOMContentLoaded', (event) => {
    const toggleButton = document.getElementById('theme-toggler'); // theme-toggler 
    const htmlElement = document.documentElement;
    

    toggleButton.addEventListener('click', () => {
        if (htmlElement.getAttribute('data-bs-theme') === 'dark') {
            htmlElement.setAttribute('data-bs-theme', 'light');
            // toggleButton.classList.remove('bg-black');
        } else {
            htmlElement.setAttribute('data-bs-theme', 'dark');

        }
    });
});