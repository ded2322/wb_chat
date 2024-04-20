from sqladmin import ModelView

from core.models.image_models import Image
from core.models.messages_models import Messages
from core.models.users_models import Users


class UserAdmin(ModelView, model=Users):
    column_list = [Users.id, Users.name]
    column_details_exclude_list = [Users.password]
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"


class MessagesAdmin(ModelView, model=Messages):
    column_list = [Messages.user] + [Messages.time_send]
    name = "Сообщение"
    name_plural = "Сообщения"
    icon = "fa-solid fa-message"
