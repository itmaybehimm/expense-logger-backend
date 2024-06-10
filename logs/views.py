from rest_framework.views import APIView
from .custompermissions import IsVerified
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .serializers import LogSerialzier, ItemSerializer
from .models import Log, Item
from django.core.paginator import Paginator

# Create your views here.


class LogGroupView(APIView):
    permission_classes = [IsVerified]
    user_not_found_message = {'message': 'one or more username not valid'}
    # pagination_class = CustomPagination

    def post(self, request):
        data = request.data.copy()

        log_serializer = LogSerialzier(data=data, context={'request': request})

        try:
            if (not log_serializer.is_valid()):
                return Response(log_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            log_serializer.save()
            return Response(log_serializer.data, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response(self.user_not_found_message, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'message': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        logs = Log.objects.filter(
            created_by=request.user).order_by('-date_created', '-id')
        query_parms = request.query_params

        paginator = Paginator(logs, per_page=4)
        page = query_parms['p'] if query_parms.get('p') else 1
        page_object = paginator.get_page(page)

        logs_serializer = LogSerialzier(page_object, many=True)
        return Response(logs_serializer.data, status=status.HTTP_200_OK)


class LogView(APIView):
    permission_classes = [IsVerified]
    log_not_found_message = {'message': 'log not found'}
    log_deleted_message = {'message': 'log deleted'}

    log_not_authorized_message = {
        'message': 'user can access logs created by them only'}

    def get(self, request, log_id):
        try:
            log = Log.objects.get(pk=log_id)
            if (request.user != log.created_by):
                return Response(self.log_not_authorized_message, status=status.HTTP_403_FORBIDDEN)
            return Response(LogSerialzier(log).data, status=status.HTTP_200_OK)
        except Log.DoesNotExist:
            return Response(self.log_not_found_message, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, log_id):
        try:
            log = Log.objects.get(pk=log_id)
            if (request.user != log.created_by):
                return Response(self.log_not_authorized_message, status=status.HTTP_403_FORBIDDEN)
            log.delete()
            return Response(self.log_deleted_message, status=status.HTTP_200_OK)
        except Log.DoesNotExist:
            return Response(self.log_not_found_message, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, log_id):
        try:
            log = Log.objects.get(pk=log_id)

            if (request.user != log.created_by):
                return Response(self.log_not_authorized_message, status=status.HTTP_403_FORBIDDEN)

            data = request.data.copy()
            log_serializer = LogSerialzier(
                log, data=data, context={'request': request}, partial=True)

            try:
                if (not log_serializer.is_valid()):
                    return Response(log_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                log_serializer.save()
                return Response(log_serializer.data, status=status.HTTP_201_CREATED)

            except User.DoesNotExist:
                return Response(self.user_not_found_message, status=status.HTTP_404_NOT_FOUND)

            except Exception as e:
                return Response({'message': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)

        except Log.DoesNotExist:
            return Response(self.log_not_found_message, status=status.HTTP_404_NOT_FOUND)


class ItemGroupView(APIView):
    permission_classes = [IsVerified]

    def get(self, request, log_id):
        try:
            log = Log.objects.get(pk=log_id)
        except Log.DoesNotExist:
            return Response({'message': 'Log not found'}, status=status.HTTP_404_NOT_FOUND)

        users_involved = log.users_involved.all()
        if (not request.user in users_involved):
            return Response({'message': 'This user has nothing to do with the log'}, status=status.HTTP_401_UNAUTHORIZED)

        items = log.items.all()
        items_serializer = ItemSerializer(items, many=True)
        return Response(items_serializer.data, status=status.HTTP_200_OK)

    def post(self, request, log_id):
        try:
            log = Log.objects.get(pk=log_id)
        except Log.DoesNotExist:
            return Response({'message': 'Log not found'}, status=status.HTTP_404_NOT_FOUND)

        if (request.user != log.created_by):
            return Response({'message': 'Only creator can add items to log'}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.POST
        items_serializer = ItemSerializer(data=data, context={'log': log})
        if (items_serializer.is_valid()):
            try:
                items_serializer.save()
                return Response(items_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'message': f'{e}'}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(items_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ItemView(APIView):
    permission_classes = [IsVerified]

    def delete(self, request, log_id, item_id):
        try:
            log = Log.objects.get(pk=log_id)
        except Log.DoesNotExist:
            return Response({'message': 'Log not found'}, status=status.HTTP_404_NOT_FOUND)
        if (request.user != log.created_by):
            return Response({'message': 'Log can only be deleted by creator'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            Item.objects.get(pk=item_id).delete()
            return Response({'message': 'Item deleted scucessfully'}, status=status.HTTP_200_OK)

        except Item.DoesNotExist:
            return Response({'message': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, log_id, item_id):
        try:
            log = Log.objects.get(pk=log_id)
        except Log.DoesNotExist:
            return Response({'message': 'Log not found'}, status=status.HTTP_404_NOT_FOUND)

        users_involved = log.users_involved.all()
        if (not request.user in users_involved):
            return Response({'message': 'This user has nothing to do with the log'}, status=status.HTTP_401_UNAUTHORIZED)

        item = Item.objects.get(pk=item_id)
        item_serializer = ItemSerializer(item)
        return Response(item_serializer.data, status=status.HTTP_200_OK)
