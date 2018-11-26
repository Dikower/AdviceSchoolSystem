import json
import traceback

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotAllowed, QueryDict
from django.shortcuts import HttpResponseRedirect, render
from django.views.decorators.csrf import csrf_protect

from .models import Person
from main.rec_system import Utils

URL_MAIN_PAGE = '/'
utils = Utils()


@csrf_protect
def index(request):
    return render(request, 'main/index.html', context={})


@csrf_protect
def about(request):
    return render(request, 'main/about.html', context={})


@csrf_protect
def func_choose_person(request):
    return render(request, 'main/choose_person.html', context={})


@csrf_protect
def func_set_person(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            user_id = request.POST['user_id']

            person = Person.objects.get(username=request.user.username)
            person.user_id = user_id
            person.save()

            return HttpResponseRedirect('../docs/')
        else:
            return HttpResponseNotAllowed(['POST'])

    else:
        return HttpResponseForbidden


@csrf_protect
def func_login(request):
    url_login = 'main/login.html'
    url_error = 'main/login_error.html'

    if request.user.is_authenticated:
        return HttpResponseRedirect('../docs/')

    else:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']

            if not username:
                return render(request, url_error, context={
                    'title':   'Введите имя пользователя!',
                    'message': 'Попробуйте еще раз'
                })

            if not password:
                return render(request, url_error, context={
                    'title':    'Введите пароль!',
                    'message':  'Попробуйте еще раз',
                    'username': username
                })

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                person = Person.objects.get(username=request.user.username)

                if person.user_id == 0:
                    return HttpResponseRedirect('../choose_person/')

                return HttpResponseRedirect('../docs/')

            else:
                return render(request, url_error, context={
                    'title':    'Неправильный логин или пароль!',
                    'message':  'Попробуйте еще раз',
                    'username': username
                })

        else:
            return render(request, url_login, context={})


@csrf_protect
def func_reg(request):
    url_reg = 'main/reg.html'
    url_error = 'main/reg_error.html'

    if request.user.is_authenticated:
        return HttpResponseRedirect('../docs/')

    else:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            password_again = request.POST['password_again']
            email = request.POST['email']
            teacher = request.POST['status'] == 'teacher'

            # ----------------------------------------
            #            Verify valid form
            # ----------------------------------------

            if not username:
                return render(request, url_error, context={
                    'title':    'Вы не ввели имя пользователя!',
                    'message':  'Попробуйте еще раз',
                    'username': username,
                    'email':    email
                })

            if not password:
                return render(request, url_error, context={
                    'title':    'Вы не ввели пароль!',
                    'message':  'Попробуйте еще раз',
                    'username': username,
                    'email':    email
                })

            if not email:
                return render(request, url_error, context={
                    'title':    'Вы не ввели почту!',
                    'message':  'Попробуйте еще раз',
                    'username': username,
                    'email':    email
                })

            if password != password_again:
                return render(request, url_error, context={
                    'title':    'Пароли не совпадают!',
                    'message':  'Попробуйте еще раз',
                    'username': username,
                    'email':    email
                })

            try:
                if User.objects.get(email=email):
                    return render(request, url_error, context={
                        'title':    'Пользователь с такой почтой уже зарегестрирован!',
                        'message':  'Попробуйте еще раз',
                        'username': username
                    })

            except (Exception, BaseException):
                pass

            try:
                if User.objects.get(username=username):
                    return render(request, url_error, context={
                        'title':   'Имя пользователя занято!',
                        'message': 'Попробуйте еще раз',
                        'email':   email
                    })

            except (Exception, BaseException):
                pass

            # ----------------------------------------

            user = User.objects.create_user(username=username, password=password, email=email)
            person = Person(username=username, teacher=teacher, pupil=not teacher, user_id=0)
            person.save()

            if user is not None:
                login(request, user)
                return HttpResponseRedirect('../choose_person/')

            else:
                return render(request, url_error, context={
                    'title':   '',
                    'message': 'что-то пошло не так :)',
                })

        else:
            return render(request, url_reg, context={})


@csrf_protect
def func_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return HttpResponseRedirect(URL_MAIN_PAGE)


@csrf_protect
def func_change_password(request):
    url_change_password = 'main/change_password.html'
    url_settings_error = 'main/settings_alert.html'
    url_change_password_alert = 'main/change_password_alert.html'

    if request.user.is_authenticated:
        if request.method == 'POST':
            password_new = request.POST['password_new']

            if password_new:
                username = request.user.username
                person = Person.objects.get(username=username)
                status = 'Учитель' if person.teacher else 'Ученик'
                email = request.user.email

                request.user.set_password(password_new)
                request.user.save()

                return render(request, url_settings_error, context={
                    'title':      'Пароль успешно изменен!',
                    'alert_type': 'success',
                    'status':     status,
                    'email':      email
                })

            else:
                return render(request, url_change_password_alert, context={
                    'title':      'Вы не ввели новый пароль!',
                    'message':    'Попробуйте еще раз',
                    'alert_type': 'danger',
                })

        else:
            return render(request, url_change_password, context={})

    else:
        return HttpResponseRedirect('../login/')


@csrf_protect
def docs(request):
    url_docs = 'main/docs.html'

    if request.user.is_authenticated:
        person = Person.objects.get(username=request.user.username)

        if person.user_id == 0:
            return HttpResponseRedirect('../choose_person/')

        return render(request, url_docs, context={})

    else:
        return HttpResponseRedirect('../login/')


@csrf_protect
def panel(request):
    url_panel = 'main/panel.html'

    if request.user.is_authenticated:
        person = Person.objects.get(username=request.user.username)

        if person.user_id == 0:
            return HttpResponseRedirect('../choose_person/')

        return render(request, url_panel, context={
            'marks':    json.dumps(utils.draw_marks(person.user_id), ensure_ascii=False),
            'subjects': json.dumps(utils.draw_subjects(person.user_id), ensure_ascii=False),
        })

    else:
        return HttpResponseRedirect('../login/')


@csrf_protect
def settings(request):
    url_docs = 'main/settings.html'

    if request.user.is_authenticated:
        username = request.user.username
        person = Person.objects.get(username=username)
        status = 'Учитель' if person.teacher else 'Ученик'
        email = request.user.email

        return render(request, url_docs, context={
            'status': status,
            'email':  email
        })

    else:
        return HttpResponseRedirect('../login/')


@csrf_protect
def func_recover_password(request):
    url_recover_password = 'main/recover_password.html'
    url_recover_password_error = 'main/recover_password_error.html'

    if request.user.is_authenticated:
        return HttpResponseRedirect('../docs/')

    else:
        if request.method == 'POST':
            username = request.POST['username']

            try:
                user = User.objects.get(username=username)

            except (Exception, BaseException):
                return render(request, url_recover_password_error, context={
                    'title':      'Пользователь не найден!',
                    'message':    'Попробуйте еще раз',
                    'alert_type': 'danger'
                })

            # new_password = ''.join(map(lambda x: random.choice(string.ascii_letters + string.digits),
            #                            range(random.randint(10, 20))))
            #
            # user.set_password(new_password)
            # user.save()
            #
            # subject, from_email, to = 'Восстановление пароля', 'noreply@example.org', user.email
            # text_content = 'Ваш новый пароль: {}'.format(new_password)
            # html_content = '<p>{}</p>'.format(text_content)
            # msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            # msg.attach_alternative(html_content, "text/html")
            # msg.send()

            # return render(request, url_recover_password_error, context={
            #     'title':      'Успешно отправлено!',
            #     'message':    'Восстановление пароля отправлено на вашу почту',
            #     'alert_type': 'success'
            # })

            return render(request, url_recover_password_error, context={
                'title':      'Восстановление пароля временно отключено!',
                'message':    'Попробуйте воспользоваться этим позже',
                'alert_type': 'warning'
            })


        else:
            return render(request, url_recover_password, context={})


# API

@csrf_protect
def api_load_post_data(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            return HttpResponse(json.dumps(utils.edu_levels, ensure_ascii=False))

        else:
            return HttpResponseNotAllowed(['GET'])

    else:
        return HttpResponseForbidden()


@csrf_protect
def api_docs_get_advice(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            q = QueryDict(request.environ['QUERY_STRING'], mutable=True)
            person = Person.objects.get(username=request.user.username)

            if person.user_id == 0:
                return HttpResponseRedirect('../choose_person/')

            if 'level' in q and 'subject' in q and 'n' in q:
                try:
                    return HttpResponse(json.dumps(
                        utils.get_recommendations(int(person.user_id), q['level'], q['subject'], int(q['n'])),
                        ensure_ascii=False)
                    )

                except (BaseException, Exception):
                    print('------------------------------------------------------')
                    print(traceback.format_exc())
                    print('------------------------------------------------------')
                    return HttpResponseBadRequest()

            else:
                return HttpResponseBadRequest()

        else:
            return HttpResponseNotAllowed(['GET'])

    else:
        return HttpResponseForbidden()


@csrf_protect
def api_public_docs_get_advice(request):
    if request.method == 'GET':
        q = QueryDict(request.environ['QUERY_STRING'], mutable=True)
        if 'level' in q and 'user_id' in q and 'subject' in q and 'n' in q:
            try:
                return HttpResponse(json.dumps(
                    utils.get_recommendations(int(q['user_id']), q['level'], q['subject'], int(q['n'])),
                    ensure_ascii=False)
                )
            except (BaseException, Exception):
                print('------------------------------------------------------')
                print(traceback.format_exc())
                print('------------------------------------------------------')
                return HttpResponseBadRequest()

        else:
            return HttpResponseBadRequest()

    else:
        return HttpResponseNotAllowed(['GET'])
