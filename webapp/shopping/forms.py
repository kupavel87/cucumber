from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, DateTimeField, HiddenField, SelectField, FieldList, FormField, FloatField
from wtforms.validators import DataRequired, ValidationError

roles = [('1', 'Нет прав'), ('2', 'Чтение'), ('3', 'Редактирование'), ('4', 'Управление')]


class RoleForm(FlaskForm):
    id = StringField('list_id', render_kw={"class": "form-control", "hidden": ""})
    name = StringField('Имя', render_kw={
                       "class": "form-control-plaintext form-control-label-sm col-7", "readonly": ""})
    role = SelectField('Роль', choices=roles, render_kw={"class": "form-control col-5"})


class CreateShoppingListForm(FlaskForm):
    list_id = StringField('list_id', render_kw={"class": "form-control", "hidden": ""})
    name = StringField('Название', validators=[DataRequired()], render_kw={
                       "class": "form-control", "onClick": "this.select();"})
    favorit = BooleanField('Важный', default=False, render_kw={'class': 'form-check-input'})
    private = BooleanField('Личный', default=True, render_kw={'class': 'form-check-input'})
    search = StringField('Поиск', render_kw={"class": "form-control"})
    access = FieldList(FormField(RoleForm))
    submit = SubmitField('submit', render_kw={"class": "btn btn-success"})

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        if len(args):
            self.name.data = args[0]
            self.list_id.data = kwargs.pop('list_id', '')
            self.favorit.data = kwargs.pop('favorit', False)
            self.private.data = kwargs.pop('private', True)
            users_role = kwargs.pop('access', '')
            for user in kwargs.pop('users', []):
                role = RoleForm()
                role.id = user.id
                role.name = user.username
                if users_role:
                    role.role = users_role.get(user.id, 1)
                else:
                    role.role = 1
                self.access.append_entry(role)


class CreateShoppingItemForm(FlaskForm):
    id = StringField('id', validators=[DataRequired()], render_kw={"class": "form-control", "hidden": ""})
    list_id = SelectField('Список', validators=[DataRequired()], coerce=int, render_kw={"class": "form-control"})
    catalog_id = SelectField('Категория', validators=[DataRequired()], coerce=int, render_kw={"class": "form-control"})
    quantity = FloatField('Количество', validators=[DataRequired()], render_kw={"class": "form-control"})
    submit = SubmitField('Сохранить', render_kw={"class": "btn btn-success"})


class OpenDetail(FlaskForm):
    id = StringField('list_id', validators=[DataRequired()], render_kw={"class": "form-control", "hidden": ""})
    submit = SubmitField('Открыть', render_kw={"class": "btn btn-success"})


class DeleteList(FlaskForm):
    id = StringField('list_id', validators=[DataRequired()], render_kw={"class": "form-control", "hidden": ""})
    submit = SubmitField('Удалить', render_kw={"class": "btn btn-danger"})


class ClearList(FlaskForm):
    id = StringField('list_id', validators=[DataRequired()], render_kw={"class": "form-control", "hidden": ""})
    submit = SubmitField('Очистить', render_kw={"class": "btn btn-danger"})
