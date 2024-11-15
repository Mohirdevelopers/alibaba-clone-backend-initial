import pytest
from unittest.mock import MagicMock
from enum import Enum


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


@pytest.fixture
def logout_data(request, user_factory, api_client, tokens):
    def valid_without_stored_tokens():
        user = user_factory.create()
        access, refresh = tokens(user)
        return 200, api_client(access), user, access

    def valid_with_stored_tokens():
        user = user_factory.create()
        access, refresh = tokens(user)
        return 200, api_client(access), user, access

    def invalid_with_unauthorized_user():
        return 401, api_client(), MagicMock(id="f0f9f100-3abd-4bbf-88ad-0cfdd6953aca"), None

    data = {
        'valid_without_stored_tokens': valid_without_stored_tokens,
        'valid_with_stored_tokens': valid_with_stored_tokens,
        'invalid_with_unauthorized_user': invalid_with_unauthorized_user,
    }
    return data[request.param]


@pytest.mark.django_db
@pytest.mark.parametrize(
    'logout_data',
    [
        'valid_without_stored_tokens',
        'valid_with_stored_tokens',
        'invalid_with_unauthorized_user',
    ],
    indirect=True,
)
def test_logout(logout_data, mocker, fake_redis, request, tokens):
    status_code, client, user, access = logout_data()
    test_name = request.node.name
    mocker.patch('share.services.TokenService.get_redis_client', return_value=fake_redis)

    if test_name == 'test_logout[valid_with_stored_tokens]':
        _, refresh = tokens(user)
        access_token_key = f'user:{user.id}:{TokenType.ACCESS}'
        refresh_token_key = f'user:{user.id}:{TokenType.REFRESH}'

        fake_redis.sadd(access_token_key, b'fake_token')
        fake_redis.sadd(refresh_token_key, b'fake_token')

    mocker.patch(
        'share.services.TokenService.add_token_to_redis',
        side_effect=lambda user_id, token, token_type, expire_time: fake_redis.sadd(
            f'user:{user_id}:{token_type}', b'fake_token'
        )
    )

    resp = client.post('/api/users/logout/')
    assert resp.status_code == status_code

    if status_code == 200:
        resp = client.get('/api/users/me/')
        assert resp.status_code == 401

    if test_name == 'test_logout[valid_with_stored_tokens]':
        assert fake_redis.smembers(access_token_key) == {b'fake_token'}
        assert fake_redis.smembers(refresh_token_key) == {b'fake_token'}
