from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Handler global de excepciones para la API.
    Garantiza que todos los errores retornen JSON consistente.
    """
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            'error': True,
            'status_code': response.status_code,
            'detail': response.data,
        }
        response.data = error_data
        return response

    # errores no manejados por DRF (ej.: errores de DB)
    return Response({
        'error': True,
        'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
        'detail': 'Error interno del servidor.',
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)