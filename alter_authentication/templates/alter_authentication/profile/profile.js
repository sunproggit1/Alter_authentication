{% include 'alter_authentication/basic_functions.js' %}

$(document).ready(function() {

    // Функция для блокировки/разблокировки элементов
    function toggleElements(isActive) {
        if (isActive) {
            // Разблокируем выпадающий список и все поля ввода
            $('#methodSelect').prop('disabled', false);
            $('.second-factor-form :input').prop('disabled', false);
        } else {
            // Блокируем выпадающий список и все поля ввода
            $('#methodSelect').prop('disabled', true);
            $('.second-factor-form :input').prop('disabled', true);
        }
    }

    // Инициализация состояния элементов на основе начального состояния чекбокса
    toggleElements($('#activeToggle').is(':checked')); // Если чекбокс активен, элементы включены

    // Переключение состояния элементов при изменении чекбокса
    $('#activeToggle').on('change', function() {
        if (!$(this).is(':checked')) {
            // Подтверждение отключения двухфакторной аутентификации
            if (confirm('Вы уверены, что хотите отключить двухфакторную аутентификацию?')) {
                $.ajax({
                    url: '{% url "set_changes_for_profile" %}', // Эндпоинт для отключения
                    type: 'POST',
                    data: {
                        'purpose': 'disable_second_factor', // Указываем цель отключения
                        'csrfmiddlewaretoken': '{{ csrf_token }}'
                    },
                    success: function(response) {
                        alert('Двухфакторная аутентификация успешно отключена.');
                        toggleElements(false); // Блокируем элементы после успешного отключения
                    },
                    error: function() {
                        alert('Произошла ошибка при отключении двухфакторной аутентификации.');
                        $(this).prop('checked', true); // Возвращаем чекбокс в исходное состояние при ошибке
                    }
                });
            } else {
                // Если пользователь отменяет отключение, возвращаем чекбокс в исходное состояние
                $(this).prop('checked', true);
            }
        } else {
            // Включаем элементы, если чекбокс активен
            toggleElements(true);
        }
    });

    // Показ формы, соответствующей текущему выбранному методу из базы данных
    let currentMethod = $('#methodSelect').val();
    if (currentMethod) {
        $('.second-factor-form').hide(); // Скрываем все формы
        if (currentMethod === 'OTP') {
            $('#otpForm').show(); // Показываем форму для OTP
        } else if (currentMethod === 'Quiz') {
            $('#quizForm').show(); // Показываем форму для Quiz
        } else if (currentMethod === 'Test') {
            $('#testForm').show(); // Показываем форму для Test
        }
    }

    // Переключение видимости форм в зависимости от выбранного метода
    $('#methodSelect').on('change', function() {
        let selectedMethod = $(this).val();
        $('.second-factor-form').hide(); // Скрываем все формы
        if (selectedMethod === 'OTP') {
            $('#otpForm').show(); // Показываем форму для OTP
        } else if (selectedMethod === 'Quiz') {
            $('#quizForm').show(); // Показываем форму для Quiz
        } else if (selectedMethod === 'Test') {
            $('#testForm').show(); // Показываем форму для Test
        }
    });

    function toggleSection(linkId, sectionToShow, sectionsToHide = []) {
        $(linkId).on('click', function(e) {
            e.preventDefault(); // 
            sectionsToHide.forEach(section => $(section).hide()); // секцияларды жасырамыз
            $(sectionToShow).toggle(); // белгіленген секцияның көріну қабілетін ауыстырамыз
        });
    }
    
    // Показ/скрытие секций
    toggleSection('#two-factor-link', '#two-factor-section', ['#password-change-section']);
    toggleSection('#password-change-link', '#password-change-section', ['#two-factor-section']);
    // Функция для отображения ошибок в форме
    function displayError(form, message) {
        let errorContainer = form.find('.error_container');
        if (!errorContainer.length) {
            // Если контейнера для ошибок нет, создаем его
            errorContainer = $('<div class="error_container text-danger mt-2"></div>');
            form.append(errorContainer);
        }
        errorContainer.text(message); // Устанавливаем текст ошибки
    }

    // Общая функция для отправки формы через AJAX
    function submitForm(form, url, purpose) {
        let data = form.serialize();
        if (purpose) {
            data = data + '&purpose=' + purpose; // Добавляем цель запроса
        }
        $.ajax({
            url: url, // URL для отправки данных
            type: 'POST',
            data: data,
            success: function(response) {
                if (response.status === 'success') {
                    alert('Настройки успешно сохранены!');
                    window.location.reload(); // Перезагружаем страницу
                } else if (response.status === 'error') {
                    displayError(form, response.message); // Показываем сообщение об ошибке
                }
            },
            error: function(xhr, status, error) {
                displayError(form, 'Произошла ошибка: ' + (xhr.responseText || error));
            }
        });
    }

    // Обработчики отправки форм

    // Форма настройки OTP
    $('#otpForm').on('submit', function(e) {
        e.preventDefault(); // Предотвращаем стандартное поведение отправки формы
        submitForm($(this), '{% url "set_changes_for_profile" %}', 'second_factor'); // Отправляем данные
    });

    // Форма настройки Quiz
    $('#quizForm').on('submit', function(e) {
        e.preventDefault();
        submitForm($(this), '{% url "set_changes_for_profile" %}', 'second_factor');
    });

    // Форма смены пароля
    $('#passwordChangeForm').on('submit', function(e) {
        e.preventDefault();
        submitForm($(this), '{% url "set_changes_for_profile" %}');
    });
});
