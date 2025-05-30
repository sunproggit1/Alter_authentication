let otp_request_type = "first"

// проверка ввода поля телефона
const input = document.querySelector("input");

const regex = /^[0-9]+$/;

let phone_is_ok = false; //индикатор правильности введенного телефона

function getCookie(name) {
  var cookies = document.cookie.split(';');
  for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();
      if (cookie.startsWith(name + '=')) {
          return decodeURIComponent(cookie.substring(name.length + 1));
      }
  }
  return null;
}
  
// Функция для установки cookie
function setCookie(name, value, days, sameSite = 'Lax', isSecure = true) {
  var expires = "";
  if (days) {
      var date = new Date();
      date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
      expires = "; expires=" + date.toUTCString();
  }
  var secureFlag = isSecure ? "; Secure" : "";
  var sameSitePolicy = "; SameSite=" + sameSite;
  document.cookie = name + "=" + encodeURIComponent(value) + expires + sameSitePolicy + secureFlag + "; path=/";
}
  
function refreshCSRFToken() {
  const csrfToken = getCookie('csrftoken');
  
  $.ajax({
      url: '{% url "get_csrf_token" %}',  // URL эндпоинта для получения нового CSRF токена
      type: 'GET',
      headers: {
          'X-CSRFToken': csrfToken
      },
      success: function(data) {
          // Обновляем CSRF токен в cookie
          document.cookie = `csrftoken=${data.new_csrf_token}; path=/`;
      }
  });
}



  $(document).ready(function(){})


  // Обработчик клика на переключатель
  $('#backToPasswordIcon').on('click', function() {
      showPasswordField();
  });


// Показать поле password и скрыть форму OTP
function showPasswordField() {
  $('#otp-field').hide();
  $('#main_password_field').show();
  $('#btn_show_otp').removeClass('active');
  $('#btn_show_pswrd').addClass('active');
}

function showOtpField(){
  $('#otp-field').show();
  $('#main_password_field').hide();
  $('#btn_show_otp').addClass('active');
  $('#btn_show_pswrd').removeClass('active');
}



// // Назначаем обработчик события для кнопки "авторизоваться через смс код?"
// $('#one_time_password_form_submit_btn').on('click', function(event){
//     event.preventDefault();
//     if (timeLeft <= 0){
//       $('#one_time_password_form').submit();
//       scenario('otp_input');
//     }else{
//       alert("дождитесь окончания таймера")
//     }
// });
function otp_form_submit(form){
  let action_url = form.attr('action');
  $.ajax({
    url: action_url,
    type: "POST",
    data: form.serialize(),
    beforeSend: function(){
    },
    success: function(response) {
        $('#one_time_password_login_form input[name="phone"]').val(
        $('#one_time_password_form input[name="phone"]').val()
        )
        $('#one_time_password_form_message').empty().append(response);
        startTimer(60);
        // $('#one_time_password_form').reset();

    },
    error: function(jqXHR, textStatus, errorThrown) {
        if (onError) onError(jqXHR, textStatus, errorThrown);
    }
    });
}


$('#one_time_password_form').on('submit',function(event){
    event.preventDefault();
    
let form = $(this);
  if (timeLeft <= 0){
    otp_form_submit(form);
    scenario('otp_input');
  }else{
    alert("дождитесь окончания таймера")
  }

})




/////////////////////////////////////Таймер повторной отправки смс на телефон

// Получаем элемент, в котором будем отображать таймер
var timerElement = document.getElementById("timer");

// Устанавливаем начальное значение таймера (в секундах)
var timeLeft = 0;
var countdown;

// Функция, обновляющая отображение таймера
function updateTimer() {
  $('#one_time_password_form_submit_btn').text("переотправить код через: " + timeLeft + " секунд")
                                          .addClass('text-muted')
                                          .removeClass('text-primary')
}

// Запускаем таймер с обратным отсчетом
function startTimer(interval=undefined) {
  console.log('startTimer = ' + interval);
  console.log(interval)
  if(interval){
    timeLeft = interval;
  }
  countdown = setInterval(function() {
  timeLeft--; // Уменьшаем время на 1 секунду
  updateTimer(); // Обновляем отображение

  if (timeLeft <= 0) {
      clearInterval(countdown); // Останавливаем таймер, когда время истекло
      $('#one_time_password_form_submit_btn').text("повторно отправить код по смс")
                                            .addClass('text-primary')
                                            .removeClass('text-muted')
    }
  }, 1000); // Обновляем каждую секунду
}



// Обработка сценариев на странице
function scenario(type){
  console.log('scenario: ' + type)
  if(type=="wrong_sms_code"){
    $('#id_username').focus();
  }else if (type=="otp_input"){
    $('#id_username').attr('readonly','readonly');
    $('#id_username_hint').hide();
    $('#id_username_reset').show();
    $('#one_time_password_form_submit_btn').show().addClass('pulsating-text').removeClass('text-muted');
    $('#id_otp').removeAttr('disabled').focus().val("");;
  }else if (type=="otp_before_input"){
    $('#id_username').attr('readonly','readonly');
    $('#id_username_hint').hide();
    $('#one_time_password_form_submit_btn').show().addClass('pulsating-text').removeClass('text-muted');
    $('#id_otp').removeAttr('disabled').focus().val("");;
  }else if (type=="username_reset"){
    $('#id_username').removeAttr('readonly').focus().val('');
    $('#id_username_hint').hide();
    $('#id_username_reset').hide();
    $('#one_time_password_form_submit_btn').hide();
  }

}
