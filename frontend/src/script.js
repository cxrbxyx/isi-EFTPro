document.addEventListener("DOMContentLoaded", function () {
    // Capturar el botón de inicio de sesión
    const loginButton = document.getElementById("loginButton");
    
    if (loginButton) {
        loginButton.addEventListener("click", function () {
            // Obtener los valores de los campos
            const username = document.getElementById("username").value.trim();
            const password = document.getElementById("password").value.trim();
            
            // PROBAR LOGIN CORRECTO CON USUARIO Y CONTRASEÑA
            const validUser = "Adrian";
            const validPass = "1234";

            // Validar que los campos no estén vacíos
            if (username === "" || password === "") {
                alert("Por favor, completa todos los campos.");
                return;
            }

            // Validar credenciales 
            if (username === validUser && password === validPass) {
                alert("Inicio de sesión exitoso. Redirigiendo...");
                // Redirigir a otra página (ejemplo: dashboard.html)
                window.location.href = "dashboard.html";
            } else {
                alert("Usuario o contraseña incorrectos.");
            }
        });
    }

    // Capturar el botón de Confirmar en la página de registro
    const confirmButton = document.getElementById("confirmButton");

    if (confirmButton) {
        confirmButton.addEventListener("click", function () {
            // Redirigir al login
            window.location.href = "login.html";
        });
    }

    if (registroButton) {
        registroButton.addEventListener("click", function () {
            // Redirigir al login
            window.location.href = "registro.html";
        });
    }
});
