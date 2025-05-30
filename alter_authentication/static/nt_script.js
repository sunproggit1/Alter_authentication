//Функция получения адреса изображения для предпросмотра до отправки на сервер
function readURL(input, preview_object) {
  if (input.files && input.files[0]) {
    var reader = new FileReader();

    reader.onload = function(e) {
      $('#'+preview_object).attr('src', e.target.result);
    }

    reader.readAsDataURL(input.files[0]); // convert to base64 string
  }
}
