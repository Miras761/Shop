from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from .models import Dialog, ChatMessage, Notification
from .serializers import DialogSerializer, ChatMessageSerializer, NotificationSerializer
from apps.listings.models import Listing


class DialogListView(generics.ListAPIView):
    """Список всех диалогов текущего пользователя"""
    serializer_class = DialogSerializer

    def get_queryset(self):
        user = self.request.user
        return Dialog.objects.filter(
            Q(participant1=user) | Q(participant2=user)
        ).prefetch_related('messages').select_related(
            'participant1', 'participant2', 'listing'
        )


class DialogStartView(APIView):
    """Создать или получить диалог с пользователем (по объявлению или напрямую)"""
    def post(self, request):
        recipient_id = request.data.get('recipient_id')
        listing_id = request.data.get('listing_id')

        if not recipient_id:
            return Response({'error': 'recipient_id обязателен'}, status=400)

        from apps.users.models import User
        try:
            recipient = User.objects.get(pk=recipient_id)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=404)

        if recipient == request.user:
            return Response({'error': 'Нельзя писать себе'}, status=400)

        listing = None
        if listing_id:
            try:
                listing = Listing.objects.get(pk=listing_id)
            except Listing.DoesNotExist:
                pass

        # participant1 всегда меньший id для уникальности
        p1, p2 = (request.user, recipient) if request.user.id < recipient.id else (recipient, request.user)

        dialog, created = Dialog.objects.get_or_create(
            participant1=p1,
            participant2=p2,
            listing=listing,
        )

        serializer = DialogSerializer(dialog, context={'request': request})
        return Response(serializer.data, status=201 if created else 200)


class DialogMessagesView(generics.ListAPIView):
    """Сообщения конкретного диалога + отметить как прочитанные"""
    serializer_class = ChatMessageSerializer

    def get_queryset(self):
        dialog_id = self.kwargs['dialog_id']
        user = self.request.user
        dialog = Dialog.objects.filter(
            Q(participant1=user) | Q(participant2=user),
            pk=dialog_id
        ).first()
        if not dialog:
            return ChatMessage.objects.none()
        # Отмечаем входящие как прочитанные
        dialog.messages.filter(is_read=False).exclude(sender=user).update(is_read=True)
        # Убираем уведомления по этому диалогу
        Notification.objects.filter(user=user, dialog=dialog).update(is_read=True)
        return dialog.messages.select_related('sender')

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


class SendMessageView(generics.CreateAPIView):
    """Отправить сообщение в диалог"""
    serializer_class = ChatMessageSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx

    def create(self, request, *args, **kwargs):
        dialog_id = self.kwargs['dialog_id']
        user = request.user
        dialog = Dialog.objects.filter(
            Q(participant1=user) | Q(participant2=user),
            pk=dialog_id
        ).first()
        if not dialog:
            return Response({'error': 'Диалог не найден'}, status=404)

        # Принимаем и текст и файл (FormData)
        text = request.data.get('text', '')
        image = request.FILES.get('image')

        if not text and not image:
            return Response({'error': 'Пустое сообщение'}, status=400)

        msg = ChatMessage.objects.create(
            dialog=dialog,
            sender=user,
            text=text,
            image=image,
        )
        dialog.save()  # обновляет updated_at

        # Уведомление получателю
        recipient = dialog.get_other_participant(user)
        sender_name = f"{user.first_name} {user.last_name}".strip() or user.username
        Notification.objects.create(
            user=recipient,
            type='message',
            text=f'{sender_name}: {text[:60] or "📷 Фото"}',
            dialog=dialog,
        )

        serializer = ChatMessageSerializer(msg, context={'request': request})
        return Response(serializer.data, status=201)


class NotificationsView(generics.ListAPIView):
    """Уведомления пользователя"""
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class UnreadCountView(APIView):
    """Количество непрочитанных сообщений и уведомлений"""
    def get(self, request):
        from django.db.models import Q
        user = request.user
        unread_msgs = ChatMessage.objects.filter(
            dialog__in=Dialog.objects.filter(
                Q(participant1=user) | Q(participant2=user)
            ),
            is_read=False
        ).exclude(sender=user).count()

        unread_notifs = Notification.objects.filter(user=user, is_read=False).count()

        return Response({
            'unread_messages': unread_msgs,
            'unread_notifications': unread_notifs,
            'total': unread_msgs + unread_notifs,
        })


class MarkNotificationsReadView(APIView):
    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'status': 'ok'})
