from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import exceptions, generics, mixins, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from sublet.models import Amenity, Offer, Sublet
from sublet.permissions import IsSuperUser, OfferOwnerPermission, SubletOwnerPermission
from sublet.serializers import (
    AmenitySerializer,
    OfferSerializer,
    SimpleSubletSerializer,
    SubletSerializer,
)


User = get_user_model()


class Amenities(generics.ListAPIView):
    serializer_class = AmenitySerializer
    queryset = Amenity.objects.all()

    def get(self, request, *args, **kwargs):
        temp = super().get(self, request, *args, **kwargs).data
        response_data = [a["name"] for a in temp]
        return Response(response_data)


class UserFavorites(generics.ListAPIView):
    serializer_class = SimpleSubletSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return user.sublets_favorited


class UserOffers(generics.ListAPIView):
    serializer_class = OfferSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Offer.objects.filter(user=user)


class Properties(viewsets.ModelViewSet):
    """
    list:
    Returns a list of Sublets that match query parameters (e.g., amenities) and belong to the user.

    create:
    Create a Sublet.

    partial_update:
    Update certain fields in the Sublet. Only the owner can edit it.

    destroy:
    Delete a Sublet.
    """

    permission_classes = [SubletOwnerPermission | IsSuperUser]
    serializer_class = SubletSerializer

    def get_queryset(self):
        return Sublet.objects.all()

    # This is currently redundant but will leave for use when implementing image creation
    # def create(self, request, *args, **kwargs):
    #     # amenities = request.data.pop("amenities", [])
    #     new_data = request.data
    #     amenities = new_data.pop("amenities", [])

    #     # check if valid amenities
    #     try:
    #         amenities = [Amenity.objects.get(name=amenity) for amenity in amenities]
    #     except Amenity.DoesNotExist:
    #         return Response({"amenities": "Invalid amenity"}, status=status.HTTP_400_BAD_REQUEST)

    #     serializer = self.get_serializer(data=new_data)
    #     serializer.is_valid(raise_exception=True)
    #     sublet = serializer.save()
    #     sublet.amenities.set(amenities)
    #     sublet.save()
    # return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        """Returns a list of Sublets that match query parameters and user ownership."""
        # Get query parameters from request (e.g., amenities, user_owned)
        params = request.query_params
        amenities = params.getlist("amenities")
        title = params.get("title")
        address = params.get("address")
        subletter = params.get("subletter", "false")  # Defaults to False if not specified
        starts_before = params.get("starts_before", None)
        starts_after = params.get("starts_after", None)
        ends_before = params.get("ends_before", None)
        ends_after = params.get("ends_after", None)
        min_price = params.get("min_price", None)
        max_price = params.get("max_price", None)
        beds = params.get("beds", None)
        baths = params.get("baths", None)

        queryset = Sublet.objects.all().filter(expires_at__gte=timezone.now())

        # Apply filters based on query parameters
        if title:
            queryset = queryset.filter(title__icontains=title)
        if address:
            queryset = queryset.filter(address__icontains=address)
        if amenities:
            queryset = queryset.filter(amenities__name__in=amenities)
        if subletter.lower() == "true":
            queryset = queryset.filter(subletter=request.user)
        if starts_before:
            queryset = queryset.filter(start_date__lt=starts_before)
        if starts_after:
            queryset = queryset.filter(start_date__gt=starts_after)
        if ends_before:
            queryset = queryset.filter(end_date__lt=ends_before)
        if ends_after:
            queryset = queryset.filter(end_date__gt=ends_after)
        if min_price:
            queryset = queryset.filter(min_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(max_price__lte=max_price)
        if beds:
            queryset = queryset.filter(beds=beds)
        if baths:
            queryset = queryset.filter(baths=baths)

        # Serialize and return the queryset
        serializer = SimpleSubletSerializer(queryset, many=True)
        return Response(serializer.data)


class Favorites(mixins.DestroyModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = SubletSerializer
    http_method_names = ["post", "delete"]
    permission_classes = [IsAuthenticated | IsSuperUser]

    def get_queryset(self):
        user = self.request.user
        return user.sublets_favorited

    def create(self, request, *args, **kwargs):
        sublet_id = int(self.kwargs["sublet_id"])
        queryset = self.get_queryset()
        if queryset.filter(id=sublet_id).exists():
            raise exceptions.NotAcceptable("Favorite already exists")
        sublet = get_object_or_404(Sublet, id=sublet_id)
        self.get_queryset().add(sublet)
        return Response(status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        sublet = get_object_or_404(queryset, pk=int(self.kwargs["sublet_id"]))
        self.get_queryset().remove(sublet)
        return Response(status=status.HTTP_204_NO_CONTENT)


class Offers(viewsets.ModelViewSet):
    """
    list:
    Returns a list of all offers for the sublet matching the provided ID.

    create:
    Create an offer on the sublet matching the provided ID.

    destroy:
    Delete the offer between the user and the sublet matching the ID.
    """

    permission_classes = [OfferOwnerPermission | IsSuperUser]
    serializer_class = OfferSerializer

    def get_queryset(self):
        return Offer.objects.filter(sublet_id=int(self.kwargs["sublet_id"])).order_by(
            "created_date"
        )

    def create(self, request, *args, **kwargs):
        data = request.data
        request.POST._mutable = True
        if self.get_queryset().filter(user=self.request.user).exists():
            raise exceptions.NotAcceptable("Offer already exists")
        data["sublet"] = int(self.kwargs["sublet_id"])
        data["user"] = self.request.user.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        filter = {"user": self.request.user.id, "sublet": int(self.kwargs["sublet_id"])}
        obj = get_object_or_404(queryset, **filter)
        # checking permissions here is kind of redundant
        self.check_object_permissions(self.request, obj)
        self.perform_destroy(obj)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        self.check_object_permissions(request, Sublet.objects.get(pk=int(self.kwargs["sublet_id"])))
        return super().list(request, *args, **kwargs)
