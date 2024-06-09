from django.shortcuts import render

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from . import models
from .models import Vendor, PurchaseOrder, HistoricalPerformance
from .serializer import VendorSerializer, PurchaseOrderSerializer, HistoricalPerformanceSerializer
from django.utils.timezone import now
from rest_framework import viewsets
from datetime import timedelta


class VendorViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        vendor = self.get_object()
        # Calculate performance metrics
        total_orders = vendor.purchase_orders.count()
        if total_orders == 0:
            return Response({
                'on_time_delivery_rate': 0,
                'quality_rating_avg': 0,
                'average_response_time': 0,
                'fulfillment_rate': 0
            })

        on_time_deliveries = vendor.purchase_orders.filter(status='completed', delivery_date__lte=now()).count()
        completed_orders = vendor.purchase_orders.filter(status='completed').count()
        on_time_delivery_rate = (on_time_deliveries / completed_orders) * 100 if completed_orders > 0 else 0

        quality_ratings = vendor.purchase_orders.filter(status='completed', quality_rating__isnull=False)
        quality_rating_avg = quality_ratings.aggregate(avg=models.Avg('quality_rating'))[
            'avg'] if quality_ratings.exists() else 0

        response_times = vendor.purchase_orders.filter(acknowledgment_date__isnull=False)
        average_response_time = \
            response_times.aggregate(avg=models.Avg(models.F('acknowledgment_date') - models.F('issue_date')))[
                'avg'].total_seconds() / 3600 if response_times.exists() else 0

        fulfillment_rate = (completed_orders / total_orders) * 100 if total_orders > 0 else 0

        return Response({
            'on_time_delivery_rate': on_time_delivery_rate,
            'quality_rating_avg': quality_rating_avg,
            'average_response_time': average_response_time,
            'fulfillment_rate': fulfillment_rate
        })


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        vendor_id = self.request.query_params.get('vendor')
        if vendor_id:
            queryset = queryset.filter(vendor_id=vendor_id)
        return queryset

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        purchase_order = self.get_object()
        purchase_order.acknowledgment_date = now()
        purchase_order.save()
        # Trigger performance recalculation
        self.calculate_performance(purchase_order.vendor)
        return Response({'status': 'acknowledged'})

    def calculate_performance(self, vendor):

        try:
            vendor = Vendor.objects.get(pk=vendor)
        except Vendor.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = HistoricalPerformanceSerializer(vendor)
        return Response(serializer.data)


class HistoricalPerformanceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = HistoricalPerformance.objects.all()
    serializer_class = HistoricalPerformanceSerializer
