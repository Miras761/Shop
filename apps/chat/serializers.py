from rest_framework import serializers
from .models import Dialog, ChatMessage, Notification
from apps.users.serializers import UserSerializer


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    sender_avatar = serializers.SerializerMethodField()
    sender_phone = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = ['id', 'dialog', 'sender', 'sender_name', 'sender_avatar',
                  'sender_phone', 'text', 'image', 'image_url',
                  'is_read', 'created_at', 'is_mine']
        read_only_fields = ['sender', 'created_at', 'is_read']
        extra_kwargs = {'image': {'write_only': True}}

    def get_sender_name(self, obj):
        u = obj.sender
        full = f"{u.first_name} {u.last_name}".strip()
        return full or u.username

    def get_sender_avatar(self, obj):
        request = self.context.get('request')
        if obj.sender.avatar and request:
            return request.build_absolute_uri(obj.sender.avatar.url)
        return None

    def get_sender_phone(self, obj):
        return obj.sender.phone or None

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_is_mine(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.sender == request.user
        return False

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        msg = super().create(validated_data)
        # Обновляем время диалога
        msg.dialog.save()
        # Создаём уведомление для получателя
        dialog = msg.dialog
        recipient = dialog.get_other_participant(msg.sender)
        sender_name = self.get_sender_name(msg)
        Notification.objects.create(
            user=recipient,
            type='message',
            text=f'{sender_name}: {msg.text[:60] or "📷 Фото"}',
            dialog=dialog,
        )
        return msg


class DialogSerializer(serializers.ModelSerializer):
    other_user = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    listing_title = serializers.SerializerMethodField()

    class Meta:
        model = Dialog
        fields = ['id', 'other_user', 'last_message', 'unread_count',
                  'listing_title', 'listing', 'updated_at']

    def get_other_user(self, obj):
        request = self.context.get('request')
        other = obj.get_other_participant(request.user)
        avatar_url = None
        if other.avatar and request:
            avatar_url = request.build_absolute_uri(other.avatar.url)
        full_name = f"{other.first_name} {other.last_name}".strip()
        return {
            'id': other.id,
            'name': full_name or other.username,
            'username': other.username,
            'phone': other.phone or None,
            'city': other.city or '',
            'avatar_url': avatar_url,
            'rating': other.rating,
        }

    def get_last_message(self, obj):
        msg = obj.messages.last()
        if not msg:
            return None
        return {
            'text': msg.text or '📷 Фото',
            'created_at': msg.created_at,
            'is_mine': msg.sender == self.context['request'].user,
            'is_read': msg.is_read,
        }

    def get_unread_count(self, obj):
        request = self.context.get('request')
        return obj.unread_count(request.user)

    def get_listing_title(self, obj):
        return obj.listing.title if obj.listing else None


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'type', 'text', 'dialog', 'is_read', 'created_at']
