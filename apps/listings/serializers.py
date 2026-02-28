from rest_framework import serializers
from .models import Listing, ListingImage, Favorite, Message
from apps.users.serializers import UserSerializer
from apps.categories.serializers import CategorySerializer


class ListingImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ListingImage
        fields = ['id', 'image', 'image_url', 'order']
        extra_kwargs = {'image': {'write_only': True}}

    def get_image_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url


class ListingListSerializer(serializers.ModelSerializer):
    main_image = serializers.SerializerMethodField()
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    seller_city = serializers.CharField(source='seller.city', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = ['id', 'title', 'price', 'is_negotiable', 'city',
                  'condition', 'status', 'views_count', 'created_at',
                  'main_image', 'seller_name', 'seller_city', 'category_name', 'is_favorite']

    def get_main_image(self, obj):
        request = self.context.get('request')
        img = obj.images.first()
        if img and request:
            return request.build_absolute_uri(img.image.url)
        return None

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(user=request.user).exists()
        return False


class ListingDetailSerializer(serializers.ModelSerializer):
    images = ListingImageSerializer(many=True, read_only=True)
    seller = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False)
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = ['id', 'title', 'description', 'price', 'is_negotiable',
                  'category', 'category_id', 'seller', 'city', 'condition',
                  'status', 'views_count', 'created_at', 'updated_at',
                  'images', 'is_favorite']
        read_only_fields = ['seller', 'views_count', 'created_at', 'updated_at']

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(user=request.user).exists()
        return False

    def create(self, validated_data):
        validated_data['seller'] = self.context['request'].user
        listing = Listing.objects.create(**validated_data)
        images = self.context['request'].FILES.getlist('images')
        for i, img in enumerate(images):
            ListingImage.objects.create(listing=listing, image=img, order=i)
        return listing

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'listing', 'sender', 'sender_name', 'recipient', 'text', 'is_read', 'created_at']
        read_only_fields = ['sender', 'created_at']

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)
