from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend


class EmailAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # создаем ссылку на текущую модель пользователя
        user_model = get_user_model()
        try:
            # Делаем так, чтобы email использовался как username
            user = user_model.objects.get(email=username)
            # Проверяем, подходит ли пароль
            if user.check_password(password):
                return user
            return None
            # Если не найдена запись, или найдено несколько записей по одному email
        except (user_model.DoesNotExist, user_model.MultipleObjectsReturned):
            return None

    # делаем так, чтобы после входа отображались отображалась кнопка "Выйти", а не "Войти"
    def get_user(self, user_id):
        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None
