from django.http import JsonResponse
from rest_framework.decorators import api_view
from base.models import Room
from rest_framework.response import Response
from base.api.serializers import RoomSerializers

def getRoutes(request):
    routes = [
        'this is form apoi',
        'this is seconf value'
    ]
    return JsonResponse(routes, safe= False)

@api_view(['GET'])
def getRooms(response):
    rooms = Room.objects.all()
    serializer = RoomSerializers(rooms, many=True)
    return Response(serializer.data)
    
@api_view(['GET'])
def getRoom(response ,id):
    room = Room.objects.filter(id=id)
    serializer = RoomSerializers(room, many=True)
    return Response(serializer.data)