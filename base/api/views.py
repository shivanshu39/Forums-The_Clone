from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Room
from .serializers import RoomSerializer


# GET, PUT, POST and such requests can be given.
# only the request given to api_view will be allowed
@api_view(['GET']) 
def getRoutes(request):
    routes = [
        'GET /api',
        'GET /api/room',
        'get /api/room/:id'
    ]
    return Response(routes)

@api_view(['GET'])
def getRooms(request):
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    
    return Response(serializer.data)



@api_view(['GET'])
def getRoom(request, pk):
    room = Room.objects.get(id=pk)
    serializer = RoomSerializer(room, many=False)
    
    return Response(serializer.data)