from rest_framework import serializers

class SubmitCodeSerializer(serializers.Serializer):
    language = serializers.ChoiceField(choices=["py", "c", "cpp"])
    source_code = serializers.CharField()

    # ixtiyoriy: sample testni ham ko'rishni xohlasangiz
    run_sample = serializers.BooleanField(required=False, default=False)