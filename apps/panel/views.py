from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.utils import timezone
from django.db.models import Count, Q
from apps.users.models import User
from apps.listings.models import Listing
from apps.chat.models import Dialog, ChatMessage, Notification


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff


class AdminStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        now = timezone.now()
        online_threshold = now - timezone.timedelta(minutes=5)
        return Response({
            'total_users': User.objects.count(),
            'online_users': User.objects.filter(last_seen__gte=online_threshold).count(),
            'banned_users': User.objects.filter(is_banned=True).count(),
            'total_listings': Listing.objects.count(),
            'active_listings': Listing.objects.filter(status='active').count(),
            'total_messages': ChatMessage.objects.count(),
            'new_users_today': User.objects.filter(date_joined__date=now.date()).count(),
            'new_listings_today': Listing.objects.filter(created_at__date=now.date()).count(),
        })


class AdminUsersView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        online_threshold = timezone.now() - timezone.timedelta(minutes=5)
        search = request.query_params.get('search', '')
        users = User.objects.all().order_by('-date_joined')
        if search:
            users = users.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        data = []
        for u in users[:100]:
            avatar_url = None
            if u.avatar:
                try:
                    avatar_url = request.build_absolute_uri(u.avatar.url)
                except:
                    pass
            data.append({
                'id': u.id,
                'username': u.username,
                'full_name': f"{u.first_name} {u.last_name}".strip() or u.username,
                'email': u.email,
                'phone': u.phone,
                'city': u.city,
                'avatar_url': avatar_url,
                'is_online': bool(u.last_seen and u.last_seen >= online_threshold),
                'last_seen': u.last_seen,
                'is_banned': u.is_banned,
                'ban_reason': u.ban_reason,
                'warnings_count': u.warnings_count,
                'is_staff': u.is_staff,
                'listings_count': u.listings.count(),
                'date_joined': u.date_joined,
            })
        return Response(data)


class AdminUserActionView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=404)

        action = request.data.get('action')
        reason = request.data.get('reason', '')

        if action == 'ban':
            user.is_banned = True
            user.ban_reason = reason
            user.is_active = False
            user.save()
            # Уведомление
            Notification.objects.create(
                user=user,
                type='message',
                text=f'⛔ Ваш аккаунт заблокирован. Причина: {reason or "Нарушение правил"}',
            )
            return Response({'status': 'banned', 'message': f'Пользователь {user.username} заблокирован'})

        elif action == 'unban':
            user.is_banned = False
            user.ban_reason = ''
            user.is_active = True
            user.save()
            Notification.objects.create(
                user=user,
                type='message',
                text='✅ Ваш аккаунт разблокирован',
            )
            return Response({'status': 'unbanned'})

        elif action == 'warn':
            user.warnings_count += 1
            user.save()
            Notification.objects.create(
                user=user,
                type='message',
                text=f'⚠️ Предупреждение #{user.warnings_count}: {reason or "Нарушение правил сайта"}',
            )
            return Response({'status': 'warned', 'warnings_count': user.warnings_count})

        elif action == 'message':
            # Написать пользователю от имени системы/админа
            Notification.objects.create(
                user=user,
                type='message',
                text=f'📢 Сообщение от администрации: {reason}',
            )
            return Response({'status': 'sent'})

        elif action == 'make_admin':
            user.is_staff = True
            user.save()
            return Response({'status': 'promoted'})

        elif action == 'remove_admin':
            if user == request.user:
                return Response({'error': 'Нельзя снять права у себя'}, status=400)
            user.is_staff = False
            user.save()
            return Response({'status': 'demoted'})

        return Response({'error': 'Неизвестное действие'}, status=400)


class AdminListingsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        search = request.query_params.get('search', '')
        status_filter = request.query_params.get('status', '')
        listings = Listing.objects.select_related('seller', 'category').prefetch_related('images').order_by('-created_at')
        if search:
            listings = listings.filter(
                Q(title__icontains=search) |
                Q(seller__username__icontains=search)
            )
        if status_filter:
            listings = listings.filter(status=status_filter)

        data = []
        for l in listings[:200]:
            img = l.images.first()
            img_url = None
            if img:
                try:
                    img_url = request.build_absolute_uri(img.image.url)
                except:
                    pass
            data.append({
                'id': l.id,
                'title': l.title,
                'price': str(l.price),
                'status': l.status,
                'condition': l.condition,
                'city': l.city,
                'views_count': l.views_count,
                'created_at': l.created_at,
                'seller_id': l.seller.id,
                'seller_name': l.seller.username,
                'seller_banned': l.seller.is_banned,
                'category': l.category.name if l.category else '',
                'main_image': img_url,
            })
        return Response(data)


class AdminListingActionView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, listing_id):
        try:
            listing = Listing.objects.select_related('seller').get(pk=listing_id)
        except Listing.DoesNotExist:
            return Response({'error': 'Объявление не найдено'}, status=404)

        action = request.data.get('action')
        reason = request.data.get('reason', '')

        if action == 'delete':
            seller = listing.seller
            title = listing.title
            listing.delete()
            Notification.objects.create(
                user=seller,
                type='message',
                text=f'🗑️ Ваше объявление «{title}» удалено администратором. {reason}',
            )
            return Response({'status': 'deleted'})

        elif action == 'archive':
            listing.status = 'archived'
            listing.save()
            Notification.objects.create(
                user=listing.seller,
                type='message',
                text=f'📦 Ваше объявление «{listing.title}» снято с публикации. {reason}',
            )
            return Response({'status': 'archived'})

        elif action == 'activate':
            listing.status = 'active'
            listing.save()
            return Response({'status': 'activated'})

        elif action == 'warn_seller':
            seller = listing.seller
            seller.warnings_count += 1
            seller.save()
            Notification.objects.create(
                user=seller,
                type='message',
                text=f'⚠️ Предупреждение по объявлению «{listing.title}»: {reason}',
            )
            return Response({'status': 'warned'})

        return Response({'error': 'Неизвестное действие'}, status=400)


class AdminChatView(APIView):
    """Просмотр всех диалогов администратором"""
    permission_classes = [IsAdminUser]

    def get(self, request):
        dialogs = Dialog.objects.select_related(
            'participant1', 'participant2', 'listing'
        ).order_by('-updated_at')[:100]

        data = []
        for d in dialogs:
            last = d.messages.last()
            data.append({
                'id': d.id,
                'participant1': {'id': d.participant1.id, 'username': d.participant1.username},
                'participant2': {'id': d.participant2.id, 'username': d.participant2.username},
                'listing_title': d.listing.title if d.listing else None,
                'messages_count': d.messages.count(),
                'last_message': last.text[:60] if last else None,
                'updated_at': d.updated_at,
            })
        return Response(data)


class AdminDialogMessagesView(APIView):
    """Просмотр сообщений диалога администратором"""
    permission_classes = [IsAdminUser]

    def get(self, request, dialog_id):
        try:
            dialog = Dialog.objects.get(pk=dialog_id)
        except Dialog.DoesNotExist:
            return Response({'error': 'Не найдено'}, status=404)

        msgs = dialog.messages.select_related('sender').all()
        data = []
        for m in msgs:
            img_url = None
            if m.image:
                try:
                    img_url = request.build_absolute_uri(m.image.url)
                except:
                    pass
            data.append({
                'id': m.id,
                'sender': m.sender.username,
                'text': m.text,
                'image_url': img_url,
                'created_at': m.created_at,
            })
        return Response({
            'dialog_id': dialog_id,
            'participant1': dialog.participant1.username,
            'participant2': dialog.participant2.username,
            'messages': data,
        })


class UpdateLastSeenView(APIView):
    """Обновить время последнего визита (вызывается с фронта)"""
    def post(self, request):
        if request.user.is_authenticated:
            User.objects.filter(pk=request.user.pk).update(last_seen=timezone.now())
        return Response({'status': 'ok'})


class SupportTicketsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        from apps.chat.models import SupportTicket
        tickets = SupportTicket.objects.select_related('user').all()
        data = []
        for t in tickets:
            data.append({
                'id': t.id,
                'subject': t.subject,
                'message': t.message,
                'status': t.status,
                'created_at': t.created_at,
                'user_id': t.user.id if t.user else None,
                'username': t.user.username if t.user else 'Гость',
                'email': t.email or (t.user.email if t.user else ''),
            })
        return Response(data)

    def patch(self, request, ticket_id):
        from apps.chat.models import SupportTicket
        try:
            ticket = SupportTicket.objects.get(pk=ticket_id)
        except SupportTicket.DoesNotExist:
            return Response({'error': 'Не найдено'}, status=404)
        ticket.status = request.data.get('status', ticket.status)
        ticket.save()
        # Notify user
        if ticket.user:
            from apps.chat.models import Notification
            Notification.objects.create(
                user=ticket.user,
                type='message',
                text=f'✅ Ваш тикет «{ticket.subject}» закрыт администратором',
            )
        return Response({'status': 'updated'})


class GlobalAnnouncementView(APIView):
    def get(self, request):
        from apps.chat.models import GlobalAnnouncement
        ann = GlobalAnnouncement.objects.filter(is_active=True).first()
        if ann:
            return Response({'text': ann.text, 'created_at': ann.created_at})
        return Response({'text': None})

    def post(self, request):
        from apps.chat.models import GlobalAnnouncement, Notification
        from apps.users.models import User
        if not request.user.is_staff:
            return Response({'error': 'Нет прав'}, status=403)
        text = request.data.get('text', '').strip()
        if not text:
            return Response({'error': 'Пустой текст'}, status=400)
        # Деактивируем старые
        GlobalAnnouncement.objects.filter(is_active=True).update(is_active=False)
        ann = GlobalAnnouncement.objects.create(
            text=text, created_by=request.user
        )
        # Рассылаем всем активным пользователям
        users = User.objects.filter(is_active=True).exclude(id=request.user.id)
        notifs = [
            Notification(user=u, type='message', text=f'📢 {text}')
            for u in users
        ]
        Notification.objects.bulk_create(notifs, batch_size=500)
        return Response({'status': 'sent', 'count': len(notifs)})

    def delete(self, request):
        from apps.chat.models import GlobalAnnouncement
        if not request.user.is_staff:
            return Response({'error': 'Нет прав'}, status=403)
        GlobalAnnouncement.objects.filter(is_active=True).update(is_active=False)
        return Response({'status': 'cleared'})


class CreateSupportTicketView(APIView):
    permission_classes = []

    def post(self, request):
        from apps.chat.models import SupportTicket
        subject = request.data.get('subject', '').strip()
        message = request.data.get('message', '').strip()
        email = request.data.get('email', '').strip()
        if not subject or not message:
            return Response({'error': 'Заполните все поля'}, status=400)
        ticket = SupportTicket.objects.create(
            user=request.user if request.user.is_authenticated else None,
            email=email,
            subject=subject,
            message=message,
        )
        return Response({'status': 'created', 'id': ticket.id})
