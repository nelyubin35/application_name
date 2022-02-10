import datetime

from rest_framework import serializers

from .models import ChallengeMember


class CreateChallengeSerializer(serializers.Serializer):
    """Serializer for creating challenge."""

    name = serializers.CharField(max_length=200)
    goal = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=500)
    requirements = serializers.CharField(max_length=500)
    bet = serializers.IntegerField(min_value=0)
    finish_datetime = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    def validate_finish_datetime(self, finish_datetime):
        """Checks that finish_datetime > current_datetime."""
        if finish_datetime > datetime.datetime.now():
            return finish_datetime
        raise serializers.ValidationError('This is past datetime.')


class BaseChallengeSerializer(serializers.Serializer):
    """Base serializer that contain main info about challenge."""
    name = serializers.CharField(max_length=200)
    goal = serializers.CharField(max_length=200)
    bet = serializers.IntegerField(min_value=0)
    finish_datetime = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    def to_representation(self, instance):
        """Adds extra field"""
        representation = super().to_representation(instance)
        user = instance.creator
        members_amount = ChallengeMember.objects.all()\
            .filter(challenge=instance).count()
        bets_sum = instance.balance.coins_amount

        representation['challenge_id'] = instance.id
        representation['creator'] = user.username
        representation['members_amount'] = members_amount
        representation['bets_sum'] = bets_sum
        return representation


class GetChallengesListSerializer(BaseChallengeSerializer):
    """Serializer for getting active challenges list."""
    pass


class GetDitailChallengeInfoSerializer(BaseChallengeSerializer):
    """Serializer for getting detail challenge information."""
    description = serializers.CharField(max_length=500)
    requirements = serializers.CharField(max_length=500)


    def to_representation(self, instance):
        """Add exstra fields"""
        representation = super().to_representation(instance)
        try:
            video_example_path = instance.video_example.path
        except ValueError:
            video_example_path = None
        representation['video_example_path'] = video_example_path
        return representation





