from rest_framework import serializers
from userside.models import CustomUser
from .models import Room

class UserSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField(read_only =True)
    class Meta:
        model = CustomUser
        fields = ['id','username','profile_pic','last_message']

    def get_last_message(self,obj):
        user =self.context['user']
        currentUser = CustomUser.objects.get(id=user)
        room = Room.objects.filter(users=currentUser).filter(users=obj).first()
        if room:
            return {'message':room.last_message,'time':room.last_message_time}
        else:
            return ''