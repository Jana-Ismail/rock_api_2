from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rockapi.models import Rock, Type
from django.contrib.auth.models import User

class RockView(ViewSet):
    """Rock view set"""

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance of a Rock object
        """
        
        rock = Rock()
        
        rock.user = request.auth.user
        rock.type_id = request.data["typeId"]
        rock.weight = request.data["weight"]
        rock.name = request.data["name"]
        
        try:
            rock.save()
            # serializer = RockSerializer(rock, many=False)
            return Response(None, status=status.HTTP_201_CREATED)
            # return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request):
        """Handle GET requests for all rock instances
        
        Returns:
            Response -- JSON serialized array
        """

        try:
            owner_only = request.query_params.get('owner', None)

            rocks = Rock.objects.all()

            if owner_only is not None and owner_only == "current":
                rocks = rocks.filter(user=request.auth.user)
                
            serializer = RockSerializer(rocks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)
    
    def destroy(self, request, pk=None):
        """Handle DELETE requests to remove a rock instance
        
        Returns:
            204 No Content
        """
        try:
            rock = Rock.objects.get(pk=pk)
            if rock.user == request.auth.user:
                rock.delete()
                return Response(None, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'message': 'You do not own that rock, shame!'}, status=status.HTTP_403_FORBIDDEN)

        except Rock.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        

class RockTypeSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = Type
        fields = ( 'label', )

class RockOwnerSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = User
        fields = ( 'first_name', 'last_name', )

class RockSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    type = RockTypeSerializer(many=False)
    user = RockOwnerSerializer(many=False)

    class Meta:
        model = Rock
        fields = ( 'id', 'name', 'weight', 'user', 'type', )