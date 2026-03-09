from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, NumberFilter, CharFilter
from django.db.models import F
from .models import Listing, Favorite, Message, Warning
from .serializers import ListingListSerializer, ListingDetailSerializer, MessageSerializer, WarningSerializer
from apps.users.models import User
from apps.users.serializers import UserSerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.seller == request.user


class ListingFilter(FilterSet):
    min_price = NumberFilter(field_name='price', lookup_expr='gte')
    max_price = NumberFilter(field_name='price', lookup_expr='lte')
    city = CharFilter(field_name='city', lookup_expr='icontains')
    category = NumberFilter(field_name='category__id')
    condition = CharFilter(field_name='condition')

    class Meta:
        model = Listing
        fields = ['min_price', 'max_price', 'city', 'category', 'condition', 'status']


class ListingListView(generics.ListAPIView):
    serializer_class = ListingListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ListingFilter
    search_fields = ['title', 'description', 'city']
    ordering_fields = ['price', 'created_at', 'views_count']
    ordering = ['-created_at']

    def get_queryset(self):
        return Listing.objects.filter(status='active').select_related('seller', 'category').prefetch_related('images')


class ListingCreateView(generics.CreateAPIView):
    serializer_class = ListingDetailSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


class ListingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Listing.objects.all()
    serializer_class = ListingDetailSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Listing.objects.filter(pk=instance.pk).update(views_count=F('views_count') + 1)
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


class MyListingsView(generics.ListAPIView):
    serializer_class = ListingListSerializer

    def get_queryset(self):
        return Listing.objects.filter(seller=self.request.user).select_related('category').prefetch_related('images')

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


class ArchiveListingView(APIView):
    """Пользователь удаляет своё объявление с указанием причины"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            listing = Listing.objects.get(pk=pk, seller=request.user)
        except Listing.DoesNotExist:
            return Response({'error': 'Не найдено'}, status=404)

        reason = request.data.get('reason', 'other')
        if reason == 'sold':
            listing.status = 'sold'
        else:
            listing.status = 'archived'
        listing.delete_reason = reason
        listing.save()
        return Response({'status': 'ok', 'message': 'Объявление снято с публикации'})


class FavoriteToggleView(APIView):
    def post(self, request, pk):
        try:
            listing = Listing.objects.get(pk=pk)
        except Listing.DoesNotExist:
            return Response({'error': 'Не найдено'}, status=404)

        fav, created = Favorite.objects.get_or_create(user=request.user, listing=listing)
        if not created:
            fav.delete()
            return Response({'status': 'removed'})
        return Response({'status': 'added'})


class FavoritesListView(generics.ListAPIView):
    serializer_class = ListingListSerializer

    def get_queryset(self):
        listing_ids = Favorite.objects.filter(
            user=self.request.user
        ).values_list('listing_id', flat=True)
        return Listing.objects.filter(id__in=listing_ids).select_related('seller', 'category').prefetch_related('images')

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


class MessageCreateView(generics.CreateAPIView):
    serializer_class = MessageSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


class MyMessagesView(generics.ListAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        return Message.objects.filter(
            recipient=self.request.user
        ).select_related('sender', 'listing')


class SellerListingsView(generics.ListAPIView):
    serializer_class = ListingListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        seller_id = self.kwargs['seller_id']
        return Listing.objects.filter(
            seller_id=seller_id, status='active'
        ).select_related('category').prefetch_related('images')

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


# ===== ADMIN VIEWS =====

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)


class AdminListingListView(generics.ListAPIView):
    """Админ видит все объявления"""
    serializer_class = ListingListSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ListingFilter
    search_fields = ['title', 'description', 'city', 'seller__username']
    ordering = ['-created_at']

    def get_queryset(self):
        return Listing.objects.all().select_related('seller', 'category').prefetch_related('images')

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


class AdminDeleteListingView(APIView):
    """Админ удаляет любое объявление"""
    permission_classes = [IsAdminUser]

    def delete(self, request, pk):
        try:
            listing = Listing.objects.get(pk=pk)
        except Listing.DoesNotExist:
            return Response({'error': 'Не найдено'}, status=404)

        listing.status = 'deleted_admin'
        listing.delete_reason = 'admin'
        listing.save()
        return Response({'status': 'ok', 'message': 'Объявление удалено'})


class AdminMessagesView(generics.ListAPIView):
    """Админ видит все сообщения"""
    serializer_class = MessageSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Message.objects.all().select_related('sender', 'recipient', 'listing').order_by('-created_at')


class AdminUsersView(generics.ListAPIView):
    """Админ видит всех пользователей"""
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return User.objects.all().order_by('-date_joined')

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


class AdminSendWarningView(APIView):
    """Админ отправляет предупреждение пользователю"""
    permission_classes = [IsAdminUser]

    def post(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=404)

        reason = request.data.get('reason', '')
        if not reason:
            return Response({'error': 'Укажите причину'}, status=400)

        Warning.objects.create(user=user, admin=request.user, reason=reason)
        return Response({'status': 'ok', 'message': f'Предупреждение отправлено пользователю {user.username}'})


class AdminWarningListView(generics.ListAPIView):
    """Список всех предупреждений"""
    serializer_class = WarningSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Warning.objects.all().select_related('user', 'admin')


class MyWarningsView(generics.ListAPIView):
    """Предупреждения текущего пользователя"""
    serializer_class = WarningSerializer

    def get_queryset(self):
        return Warning.objects.filter(user=self.request.user)
