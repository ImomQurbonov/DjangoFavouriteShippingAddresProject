from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from customer.models import (
    DiscountProduct, ShippingAddress,
    Country, State, City,
    Favorite, DiscountCategory
)

from customer.serializers import (
    # DiscountProductSerializer,
    ShippingAddressSerializer,
    FavouriteSerializer,
    DiscountCategorySerializer,
    DiscountProductListSerializer,
    DiscountCategoryListserializer
)

from main.models import Product, Category
from main.serializers import ProductListSerializer


class MyFavouriteAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FavouriteSerializer

    def post(self, request):
        user_id = request.user.id
        product_id = request.data.get('product_id')

        if not user_id:
            return Response({'success': False, "error": "user_id is required"})

        if not product_id:
            return Response({'success': False, 'error': 'Input should be integer !'})

        try:
            Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({'success': False, 'error': 'Product not found !!!'})

        try:
            favorite = Favorite.objects.get(user_id=user_id, product_id=product_id)
            favorite.delete()
            return Response({'success': True, 'detail': 'Removed'})
        except Favorite.DoesNotExist:
            user_product = Favorite.objects.create(
                user_id=user_id,
                product_id=product_id
            )
            user_product.save()
            return Response({'success': True, 'detail': 'Added'})

    def get(self, request):
        user_id = request.user.id

        if not user_id:
            return Response({'success': False, "error": "user_id is required"})

        favorites = Favorite.objects.filter(user_id=user_id)

        if not favorites:
            return Response('My favourite empty !!!')
        product_ids = [favorite.product_id for favorite in favorites]
        products = Product.objects.filter(pk__in=product_ids)
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


class ShippignAddressAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ShippingAddressSerializer

    def post(self, request):
        phone_number = request.data.get('phone_number')
        postal_code = request.data.get('postal_code')
        street_address = request.data.get('street_address')
        house_number = request.data.get('house_number')
        state_name = request.data.get('state')
        city_name = request.data.get('city')
        country_name = request.data.get('country')
        user = request.user.id

        if not user:
            return Response({'success': False, "error": "user_id is required"})

        if phone_number is None or postal_code is None or street_address is None or house_number is None or state_name is None or city_name is None or country_name is None:
            return Response({'success': False, 'error': 'there is empty data.'})

        try:
            country = Country.objects.get(name=country_name)
        except Country.DoesNotExist:
            return Response({'success': False, 'detail': 'such a country does not exist !!!'})

        try:
            state = State.objects.get(state=state_name, country=country)
        except State.DoesNotExist:
            return Response({'success': False, 'detail': 'There is no state in such a country !!!'})

        try:
            city = City.objects.get(city=city_name, state=state.id)
            add_data = ShippingAddress.objects.create(
                user_id=request.user.id,
                phone_number=phone_number,
                postal_code=postal_code,
                street_address=street_address,
                house_number=house_number,
                country_id=country.id,
                state_id=state.id,
                city_id=city.id
            )
            return Response({'success': True, 'detail': 'Added'})
        except City.DoesNotExist:
            return Response({'success': False, 'detail': 'There is no city in such a state !!!'})

    def get(self, request):
        user_id = request.user.id

        if not user_id:
            return Response({'success': False, "error": "user_id is required"})

        data = []
        shipping_addresses = ShippingAddress.objects.filter(user_id=user_id)
        for addresses in shipping_addresses:
            country = Country.objects.get(pk=addresses.country.id)
            state = State.objects.get(pk=addresses.state.id)
            city = City.objects.get(pk=addresses.city.id)
            data.append({
                'phone_number': addresses.phone_number,
                'postal_code': addresses.postal_code,
                'street_address': addresses.street_address,
                'house_number': addresses.house_number,
                'city': city.city,
                'state': state.state,
                'country': country.name
            }
            )
        serializer = ShippingAddressSerializer(data, many=True)
        return Response(serializer.data)


class ShippingAddressUpdateAPIView(GenericAPIView):
    serializer_class = ShippingAddressSerializer

    def put(self, request, shipping_address_id):
        phone_number = request.data.get('phone_number')
        postal_code = request.data.get('postal_code')
        street_address = request.data.get('street_address')
        house_number = request.data.get('house_number')
        state_name = request.data.get('state')
        city_name = request.data.get('city')
        country_name = request.data.get('country')
        user = request.user.id

        if not user:
            return Response({'success': False, "error": "user_id is required"})

        try:
            title = ShippingAddress.objects.get(
                user_id=request.user.id,
                pk=shipping_address_id
            )
        except ObjectDoesNotExist:
            return Response({"error": "ShippingAddress not found"})

        try:
            country = Country.objects.get(name=country_name)
        except Country.DoesNotExist:
            return Response({'success': False, 'detail': 'such a country does not exist !!!'})

        try:
            state = State.objects.get(state=state_name, country=country)
        except State.DoesNotExist:
            return Response({'success': False, 'detail': 'There is no state in such a country !!!'})

        try:
            city = City.objects.get(city=city_name, state=state.id)
            if phone_number:
                title.phone_number = phone_number
            if postal_code:
                title.postal_code = postal_code
            if street_address:
                title.street_address = street_address
            if house_number:
                title.house_number = house_number
            if city:
                title.city = city
            if state:
                title.state = state
            if country:
                title.country = country
            title.save()
            return Response({'success': True, 'detail': 'Update successfully !'})
        except City.DoesNotExist:
            return Response({'success': False, 'detail': 'There is no city in such a state !!!'})

    def delete(self, request, shipping_address_id):
        user = request.user.id

        if not user:
            return Response({'success': False, "error": "user_id is required"})

        try:
            exists_data = ShippingAddress.objects.get(
                user=request.user.id,
                pk=shipping_address_id
            )
            if exists_data:
                exists_data.delete()
            return Response({'success': True, 'detail': 'Data deleted !'})
        except ShippingAddress.DoesNotExist:
            return Response({'success': False})


class DiscountCategoryListAPIView(GenericAPIView):
    serializer_class = DiscountCategoryListserializer

    def get(self, request):
        discount_category_data = DiscountCategory.objects.filter(start_time__lte=now())
        serializer = DiscountCategoryListserializer(discount_category_data, many=True)
        return Response(serializer.data)


class DiscountProductListAPIView(GenericAPIView):
    serializer_class = DiscountProductListSerializer

    def get(self, request):
        discount_products = DiscountProduct.objects.filter(start_time__lte=now())

        if not discount_products.exists():
            return Response({'success': False, 'error': 'No discount products found.'}, status=404)

        serializer = DiscountProductListSerializer(discount_products, many=True)
        return Response(serializer.data)


class DiscountCategoryAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)  # AdminPermission
    serializer_class = DiscountCategorySerializer

    def post(self, request, category_id):
        percentage = request.data.get('discount_percentage')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')

        try:
            category_instance = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            return Response({"error": "Category does not exist"})

        products = Product.objects.filter(category_id=category_id)

        if not 0 <= float(percentage) <= 100:
            return Response({"error": "Discount percentage should be between 0 and 100"}, status=400)

        DiscountCategory.objects.create(
            category=category_instance,
            discount_percentage=percentage,
            start_time=start_time,
            end_time=end_time,
            img=category_instance.img,
            count_product=category_instance.count_product
        )

        datas = []

        for product in products:
            discounted_price = float(product.price) - (float(product.price) * (float(percentage) / 100))
            discount_product_data = DiscountProduct.objects.create(
                product=product,
                discount_percentage=percentage,
                discounted_price=discounted_price,
                start_time=start_time,
                end_time=end_time,
                rate=product.rate
            )
            datas.append(discount_product_data)

        serializer = DiscountProductSerializer(datas, many=True)
        return Response(serializer.data)

    def patch(self, request, category_id):
        percentage = request.data.get('discount_percentage')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')

        try:
            category_instance = get_object_or_404(Category, pk=category_id)
        except Category.DoesNotExist:
            return Response({"error": "Category does not exist"}, status=404)

        if not category_instance.discountcategory_set.exists():
            return Response('Discount category not found !!!', status=404)

        products_with_discount = DiscountProduct.objects.filter(product__category=category_instance)

        DiscountCategory.objects.filter(category=category_instance).update(
            discount_percentage=percentage,
            start_time=start_time,
            end_time=end_time
        )

        for discount_product_data in products_with_discount:
            if percentage:
                discount_product_data.discount_percentage = percentage
                discount_product_data.discounted_price = discount_product_data.product.price - (
                            discount_product_data.product.price * (float(percentage) / 100))

            if start_time:
                discount_product_data.start_time = start_time
            if end_time:
                discount_product_data.end_time = end_time

            discount_product_data.save()

        return Response({'success': True})

class DiscountProductAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = DiscountProductSerializer

    def post(self, request):
        user = request.user.id
        product_ids = request.data.get("product_ids", [])
        percentage = request.data.get('discount_percentage')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')

        if not user:
            return Response({'success': False, "error": "user_id is required"}, status=400)

        error_products = []

        for product_id in product_ids:
            try:
                product = Product.objects.get(pk=product_id)
            except Product.DoesNotExist:
                error_products.append(product_id)
                continue

            discounted_price = product.price - (product.price * (float(percentage) / 100))

            DiscountProduct.objects.create(
                product=product,
                discount_percentage=percentage,
                discounted_price=discounted_price,
                rate=product.rate,
                sold_quantity=product.sold_quantity,
                start_time=start_time,
                end_time=end_time
            )

        if error_products:
            return Response({'success': False, 'error': error_products}, status=404)
        else:
            return Response({'success': True}, status=201)

    def patch(self, request):
        product_ids = request.data.getlist('product_ids', [])
        percentage = request.data.get('discount_percentage')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')

        error_product = []
        confirm_discount_product = []

        for product_id in product_ids:
            try:
                title = DiscountProduct.objects.get(pk=product_id)
            except Product.DoesNotExist:
                error_product.append(product_id)
                continue

            if percentage:
                title.discount_percentage = percentage
                title.discounted_price = float(title.product.price) - (
                        float(title.product.price) * (float(percentage) / 100))

            if start_time:
                title.start_time = start_time
            if end_time:
                title.end_time = end_time

            title.save()
            confirm_discount_product.append(title)
        serializer = DiscountProductSerializer(confirm_discount_product, many=True)
        return Response(serializer.data, {'success': False, 'error': error_product})


