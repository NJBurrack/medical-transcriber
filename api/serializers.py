from rest_framework import serializers

class TreatmentRequestSerializer(serializers.Serializer):
    description = serializers.CharField(max_length=5000)

class ICDRequestSerializer(serializers.Serializer):
    treatment = serializers.CharField(max_length=5000)
