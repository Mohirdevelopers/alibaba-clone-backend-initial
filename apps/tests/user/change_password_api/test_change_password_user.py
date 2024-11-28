import pytest

from user.models import Group


@pytest.fixture
def change_password_data(request, user_factory):
    old_password = 'FGHJJ#$^%123'
    new_password = '&*^JHFHGF123'
    user = user_factory.create(password=old_password)
    buyer_group = Group.objects.get(name="buyer")
    user.groups.add(buyer_group)
    user.save()

    def valid_user():
        return (
            200, user,
            {
                'old_password': old_password,
                'new_password': new_password,
                'confirm_password': new_password,
            },
        )

    def incorrect_old_password():
        return (
            400, user,
            {
                'old_password': 'fake_old_password',
                'new_password': new_password,
                'confirm_password': new_password,
            },
        )

    def invalid_old_password():
        return (
            400, user,
            {
                'old_password': {},
                'new_password': new_password,
                'confirm_password': new_password,
            },
        )

    def empty_old_password():
        return (
            400, user,
            {
                'old_password': '',
                'new_password': new_password,
                'confirm_password': new_password,
            },
        )

    def required_old_password():
        return (
            400, user,
            {
                'new_password': new_password,
                'confirm_password': new_password,
            },
        )

    def incorrect_new_password():
        return (
            400, user,
            {
                'old_password': old_password,
                'new_password': 'fake_new_password',
                'confirm_password': new_password,
            },
        )

    def check_has_digit():
        return (
            400, user,
            {
                'old_password': old_password,
                'new_password': 'password',
                'confirm_password': new_password,
            },
        )

    def check_min_length():
        return (
            400, user,
            {
                'old_password': old_password,
                'new_password': 'pas12',
                'confirm_password': new_password,
            },
        )

    def invalid_new_password():
        return (
            400, user,
            {
                'old_password': old_password,
                'new_password': {},
                'confirm_password': new_password,
            },
        )

    def empty_new_password():
        return (
            400, user,
            {
                'old_password': old_password,
                'new_password': '',
                'confirm_password': new_password,
            },
        )

    def required_new_password():
        return (
            400, user,
            {
                'old_password': old_password,
                'confirm_password': new_password,
            },
        )

    def incorrect_confirm_password():
        return (
            400, user,
            {
                'old_password': old_password,
                'new_password': new_password,
                'confirm_password': 'fake_confirm_password',
            },
        )

    def invalid_confirm_password():
        return (
            400, user,
            {
                'old_password': old_password,
                'new_password': new_password,
                'confirm_password': {},
            },
        )

    def empty_confirm_password():
        return (
            400, user,
            {
                'old_password': old_password,
                'new_password': new_password,
                'confirm_password': '',
            },
        )

    def required_confirm_password():
        return (
            400, user,
            {
                'old_password': old_password,
                'new_password': new_password,
            },
        )

    def inactive_user():
        user.is_active = False
        user.save()
        return 401, user, {}

    def unauthorized_user():
        return 401, None, {}

    data = {
        'valid_user': valid_user,
        'inactive_user': inactive_user,
        'unauthorized_user': unauthorized_user,
        'incorrect_old_password': incorrect_old_password,
        'check_has_digit': check_has_digit,
        'check_min_length': check_min_length,
        'invalid_old_password': invalid_old_password,
        'empty_old_password': empty_old_password,
        'required_old_password': required_old_password,
        'incorrect_new_password': incorrect_new_password,
        'invalid_new_password': invalid_new_password,
        'empty_new_password': empty_new_password,
        'required_new_password': required_new_password,
        'incorrect_confirm_password': incorrect_confirm_password,
        'invalid_confirm_password': invalid_confirm_password,
        'empty_confirm_password': empty_confirm_password,
        'required_confirm_password': required_confirm_password,
    }
    return data[request.param]


@pytest.mark.django_db
@pytest.mark.parametrize(
    'change_password_data',
    [
        'valid_user',
        'inactive_user',
        'unauthorized_user',
        'incorrect_old_password',
        'check_has_digit',
        'check_min_length',
        'invalid_old_password',
        'empty_old_password',
        'required_old_password',
        'incorrect_new_password',
        'invalid_new_password',
        'empty_new_password',
        'required_new_password',
        'incorrect_confirm_password',
        'invalid_confirm_password',
        'empty_confirm_password',
        'required_confirm_password',
    ],
    indirect=True,
)
def test_change_password(change_password_data, api_client, tokens):
    status_code, user, req_json = change_password_data()
    if user:
        access, _ = tokens(user)
    else:
        access = "fake_access"
    client = api_client(token=access)
    resp = client.put('/api/users/change/password/', data=req_json, format='json')
    assert resp.status_code == status_code

    if status_code == 200:
        resp = client.post(
            '/api/users/login/',
            data={
                'email_or_phone_number': user.phone_number,
                'password': req_json['new_password'],
            },
            format='json',
        )
        assert resp.status_code == 200
        resp_json = resp.json()
        assert sorted(resp_json.keys()) == sorted(['access', 'refresh'])
