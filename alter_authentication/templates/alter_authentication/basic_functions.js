function getCookie(name) {
    var cookies = document.cookie.split(';'); // Разделяем все cookies на массив
    for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i].trim(); // Убираем лишние пробелы
        if (cookie.startsWith(name + '=')) { // Ищем cookie с указанным именем
            return decodeURIComponent(cookie.substring(name.length + 1)); // Возвращаем значение cookie
        }
    }
    return null; // Возвращаем null, если cookie не найдено
}

    
// Функция для установки cookie
function setCookie(name, value, days, sameSite = 'Lax', isSecure = true) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000)); // Устанавливаем срок действия в миллисекундах
        expires = "; expires=" + date.toUTCString(); // Преобразуем в формат UTC
    }
    var secureFlag = isSecure ? "; Secure" : ""; // Устанавливаем флаг безопасности, если включен HTTPS
    var sameSitePolicy = "; SameSite=" + sameSite; // Политика SameSite (по умолчанию "Lax")
    document.cookie = name + "=" + encodeURIComponent(value) + expires + sameSitePolicy + secureFlag + "; path=/";
}

    
function refreshCSRFToken() {
    const csrfToken = getCookie('csrftoken'); // Получаем текущий CSRF токен

    $.ajax({
        url: '{% url "get_csrf_token" %}',  // URL эндпоинта, возвращающего новый CSRF токен
        type: 'GET',
        headers: {
            'X-CSRFToken': csrfToken // Передаем текущий токен в заголовке
        },
        success: function(data) {
            // Обновляем CSRF токен в cookie
            document.cookie = `csrftoken=${data.new_csrf_token}; path=/`;
        }
    });
}
