from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    bio = serializers.CharField(allow_blank=True, required=False)
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('username', 'bio', 'avatar',)
        read_only_fields = ('username',)

    def get_avatar(seld, obj):
        if obj.avatar:
            return obj.avatar
        return "https://pixabay.com/en/user-person-people-profile-account-1633249/"
