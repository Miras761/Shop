from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, NumberFilter, CharFilter
from .models import Listing, Favorite, Message
from .serializers import ListingListSerializer, ListingDetailSerializer, MessageSerializer


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
        return [permissions.IsAuthenticated()]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
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
