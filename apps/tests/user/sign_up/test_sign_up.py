import pytest

from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def signup_data(request, user_factory, mocker):
    password = 'jsh767jHJHdskd'
    phone_number = "+998911110011"
    user = user_factory.create(password=password, is_verified=False)
    resp = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone_number': phone_number,
        'email': user.email,
        'user_trade_role': 'buyer',
        'gender': user.gender,
        'password': password,
        'confirm_password': password,
    }

    def valid_data():
        redis_conn = mocker.Mock()
        redis_conn.exists.return_value = False

        return (
            201, redis_conn, 200, resp
        )

    def valid_data_with_existing_user():
        redis_conn = mocker.Mock()
        redis_conn.exists.return_value = True
        redis_conn.get.return_value = b'asfasdI&UIKJHKLHJkjhasklfh9839klajhk'

        return (
            201, redis_conn, None, resp
        )

    def phone_number_exists():
        user.is_verified = True
        user.save()
        resp.update({'phone_number': user.phone_number})

        return (
            409, None, None, resp
        )

    def email_exists():
        user.is_verified = True
        user.save()
        resp.update({'email': user.email})

        return (
            409, None, None, resp
        )

    def phone_number_exists_with_not_existing_user():
        """
        Bu yerda user.views.redis_conn.exists() True qaytarishini taminlaydi
        """

        redis_conn = mocker.Mock()
        redis_conn.exists.return_value = True
        redis_conn.get.return_value = b'asfasdI&UIKJHKLHJkjhasklfh9839klajhk'
        resp.update({'phone_number': user.phone_number})
        user.delete()

        return (
            201, redis_conn, None, resp
        )

    def invalid_first_name():
        resp.update({'first_name': {'foo': 'bar'}})

        return (
            400, None, None, resp
        )

    def empty_first_name():
        resp.update({'first_name': ''})

        return (
            400, None, None, resp
        )

    def required_first_name():
        resp.pop('first_name')

        return (
            400, None, None, resp
        )

    def invalid_last_name():
        resp.update({'last_name': {'foo': 'bar'}})

        return (
            400, None, None, resp
        )

    def empty_last_name():
        resp.update({'last_name': ''})

        return (
            400, None, None, resp
        )

    def required_last_name():
        resp.pop('last_name')

        return (
            400, None, None, resp
        )

    def invalid_password():
        resp.update({'password': {'foo': 'bar'}})

        return (
            400, None, None, resp
        )

    def check_has_digit():
        resp.update({'password': 'password'})

        return (
            400, None, None, resp
        )

    def check_min_length():
        resp.update({'password': 'pas12'})

        return (
            400, None, None, resp
        )

    def empty_password():
        resp.update({'password': ''})

        return (
            400, None, None, resp
        )

    def required_password():
        resp.pop('password')

        return (
            400, None, None, resp
        )

    def invalid_confirm_password():
        resp.update({'confirm_password': {'foo': 'bar'}})

        return (
            400, None, None, resp
        )

    def empty_confirm_password():
        resp.update({'confirm_password': ''})

        return (
            400, None, None, resp
        )

    def required_confirm_password():
        resp.pop('confirm_password')

        return (
            400, None, None, resp
        )

    def not_match_passwords():
        resp.update({'confirm_password': 'fake_password'})

        return (
            400, None, None, resp
        )

    data = {
        'valid_data': valid_data,
        'valid_data_with_existing_user': valid_data_with_existing_user,
        'phone_number_exists': phone_number_exists,
        'email_exists': email_exists,
        'phone_number_exists_with_not_existing_user': phone_number_exists_with_not_existing_user,
        'invalid_first_name': invalid_first_name,
        'empty_first_name': empty_first_name,
        'required_first_name': required_first_name,
        'invalid_last_name': invalid_last_name,
        'empty_last_name': empty_last_name,
        'required_last_name': required_last_name,
        'invalid_password': invalid_password,
        'check_has_digit': check_has_digit,
        'check_min_length': check_min_length,
        'empty_password': empty_password,
        'required_password': required_password,
        'invalid_confirm_password': invalid_confirm_password,
        'empty_confirm_password': empty_confirm_password,
        'required_confirm_password': required_confirm_password,
        'not_match_passwords': not_match_passwords,
    }
    return data[request.param]


@pytest.mark.django_db
@pytest.mark.parametrize(
    'signup_data',
    [
        'valid_data',
        'valid_data_with_existing_user',
        'phone_number_exists',
        'email_exists',
        'phone_number_exists_with_not_existing_user',
        'invalid_first_name',
        'empty_first_name',
        'required_first_name',
        'invalid_last_name',
        'empty_last_name',
        'required_last_name',
        'invalid_password',
        'check_has_digit',
        'check_min_length',
        'empty_password',
        'required_password',
        'invalid_confirm_password',
        'empty_confirm_password',
        'required_confirm_password',
        'not_match_passwords',
    ],
    indirect=True,
)
def test_signup(signup_data, api_client, mocker):
    client = api_client()
    status_code, redis_conn, email_status, req_json = signup_data()

    """
    Bu yerda moker funksiyasi yordamida redis_conn, generate_otp, send_email 
    funksiyalari mock qilinadi. Yani siz mocker orqali yuborgan malumotlar ishlatiladi.

    user.views.redis_conn   
    user.views.generate_otp
    user.views.send_email

    Mock ishlatishdan sabab ushbu funksiyalar ishlashi talab qilinmaydi.

    """

    mocker.patch('user.views.redis_conn', redis_conn)
    mocker.patch('user.views.generate_otp', return_value=('123456', '1v8z0Of5sJ0XI3cpNcHWrofrHZfY0oGJZbvGW4siTs0'))
    mocker.patch('user.views.send_email', return_value=email_status)

    resp = client.post('/api/users/register/', data=req_json, format='json')

    """
    Responsedan qaytgan status code, kutilayotgan status kodga teng ekanligi tekshirish.
    """
    assert resp.status_code == status_code

    if status_code == 201:
        resp_json = resp.json()
        assert sorted(resp_json.keys()) == sorted(['phone_number', 'otp_secret'])

        user = User.objects.get(phone_number=req_json['phone_number'])
        assert user.first_name == req_json['first_name']
        assert user.last_name == req_json['last_name']
        assert user.is_verified is False
