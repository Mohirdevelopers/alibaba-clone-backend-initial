import pytest
from decimal import Decimal
from rest_framework import status
from cart.models import Cart, CartItem
from user.models import Group


@pytest.mark.django_db
class TestCartViews:
    @pytest.fixture(autouse=True)
    def setup(self, api_client, tokens, user_factory, product_factory):
        self.user = user_factory()
        buyer_group = Group.objects.get(name="buyer")
        self.user.groups.add(buyer_group)
        self.user.save()

        self.access, _ = tokens(self.user)
        self.client = api_client(token=self.access)

        self.url_get_total = '/api/cart/total/'
        self.url_remove_item = '/api/cart/remove/{product_id}/'
        self.url_empty_cart = '/api/cart/empty/'

        self.product1 = product_factory(title="product1", price=10.12, quantity=10)
        self.product2 = product_factory(title="product2", price=20.43, quantity=20)

        self.cart = Cart.objects.create(user=self.user)
        self.cart_item1 = CartItem.objects.create(cart=self.cart, product=self.product1, quantity=2)
        self.cart_item2 = CartItem.objects.create(cart=self.cart, product=self.product2, quantity=1)

    def test_get_cart_total_view_authenticated(self):
        response = self.client.get(self.url_get_total)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_items'] == 2
        assert response.data['total_quantity'] == 3
        assert response.data['total_price'] == Decimal("40.67")

    def test_get_cart_total_view_no_cart(self, api_client):
        client = api_client(token=self.access)
        Cart.objects.filter(user=self.user).delete()
        response = client.get(self.url_get_total)
        assert response.status_code == status.HTTP_200_OK

    def test_remove_item_view_authenticated(self):
        url = self.url_remove_item.format(product_id=self.product1.id)
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not CartItem.objects.filter(cart=self.cart, product=self.product1).exists()

    def test_remove_item_required_view_authenticated(self):
        url = self.url_remove_item
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_remove_item_view_not_found(self):
        url = self.url_remove_item.format(product_id='non-existent-id')
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_empty_cart_view_authenticated(self):
        response = self.client.delete(self.url_empty_cart)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not CartItem.objects.filter(cart=self.cart).exists()
