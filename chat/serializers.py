from rest_framework import serializers
from userside.models import CustomUser
from .models import Room

class UserSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField(read_only =True)
    blocked_by = serializers.SerializerMethodField(read_only =True)
    is_blocked = serializers.SerializerMethodField(read_only = True)
    class Meta:
        model = CustomUser
        fields = ['id','username','profile_pic','last_message','blocked_by','is_blocked']

    def get_last_message(self,obj):
        user =self.context['user']
        currentUser = CustomUser.objects.get(id=user)
        room = Room.objects.filter(users=currentUser).filter(users=obj).first()
        if room:
            return {'message':room.last_message,'time':room.last_message_time}
        else:
            return ''
        
    def get_blocked_by(self,obj):
        user = self.context['user']
        currentUser = CustomUser.objects.get(id=user)
        blocked_by_users = currentUser.blocked_by.all()
        return obj in blocked_by_users 
    
    def get_is_blocked(self,obj):
        user = self.context['user']
        currentUser = CustomUser.objects.get(id=user)
        blocked_users = currentUser.blocked_users.all()
        return obj in blocked_users