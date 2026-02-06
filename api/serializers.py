from rest_framework import serializers
from .models import EquipmentDataset, Equipment

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = '__all__'

class EquipmentDatasetSerializer(serializers.ModelSerializer):
    items = EquipmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = EquipmentDataset
        fields = ['id', 'filename', 'upload_date', 'summary_stats', 'items']
