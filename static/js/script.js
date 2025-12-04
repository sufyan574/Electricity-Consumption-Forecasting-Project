

document.addEventListener("DOMContentLoaded", function () {
    const inputs = document.querySelectorAll("input[type='text'], input[type='number']");

    inputs.forEach(input => {
        input.addEventListener("input", function () {
            this.value = this.value.replace(/[^0-9.]/g, '');
        });
    });
});
