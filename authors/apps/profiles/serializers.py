from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    bio = serializers.CharField(allow_blank=True, required=False)
    avatar = serializers.SerializerMethodField()
    reading_stats = serializers.CharField(max_length=100)

    class Meta:
        model = Profile
        fields = ('username', 'bio', 'avatar', 'reading_stats', 'reading_stats')
        read_only_fields = ('username',)
    
    def get_avatar(self, obj):
        if obj.avatar:
            return obj.avatar
        return "https://pixabay.com/en/user-person-people-profile-account-1633249/"
    
    def helper(self, field):
        request = self.context.get('request', None)

        if field == 'following':
            profiles = request.user.profile.following.all()
        elif field == 'followers':
            profiles = request.user.profile.followers.all()

        return [profile.user.username for profile in profiles]
    
    def get_following(self, instance):
        return self.helper('following')
    
    def get_followers(self, instance):
        return self.helper('followers')


class ProfileListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    bio = serializers.CharField(allow_blank=True, required=False)
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('username', 'bio', 'avatar')
        read_only_fields = ('username',)
    
    def get_avatar(self, obj):
        if obj.avatar:
            return obj.avatar
        return "https://pixabay.com/en/user-person-people-profile-account-1633249/"
