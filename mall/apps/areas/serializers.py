from rest_framework import serializers

from areas.models import Area


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ['id','name']

class SubsAreaSerializer(serializers.ModelSerializer):
    subs = AreaSerializer(many=True)

    class Meta:
        model = Area
        fields = ['subs','id','name']