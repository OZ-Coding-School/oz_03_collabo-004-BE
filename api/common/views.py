from common.logger import logger
from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


class HealthCheck(GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        logger.info("GET /api/health")
        return Response(data={"Message": "HELLO"}, status=status.HTTP_200_OK)
