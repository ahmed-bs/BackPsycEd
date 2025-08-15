from rest_framework import serializers
from .models import Goal, SubObjective
from ProfileDomain.models import ProfileDomain
from ProfileDomain.serializers import ProfileDomainSerializer
from profiles.models import Profile
from profiles.serializers import ProfileSerializer

class SubObjectiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubObjective
        fields = ['id', 'description', 'is_completed']
        read_only_fields = ['id']

class GoalSerializer(serializers.ModelSerializer):
    sub_objectives = SubObjectiveSerializer(many=True, required=False)

    domain_id = serializers.PrimaryKeyRelatedField(
        queryset=ProfileDomain.objects.all(), source='domain', write_only=True, required=False, allow_null=True
    )
    domain = ProfileDomainSerializer(read_only=True)

    profile_id = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.all(), source='profile', write_only=True
    )
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = Goal
        fields = [
            'id', 'profile_id', 'profile', 'domain_id', 'domain', 'title', 'title_ar', 'description', 'description_ar',
            'target_date', 'priority', 'sub_objectives', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'profile']

    def create(self, validated_data):
        sub_objectives_data = validated_data.pop('sub_objectives', [])
        goal = Goal.objects.create(**validated_data) 
        for sub_objective_data in sub_objectives_data:
            SubObjective.objects.create(goal=goal, **sub_objective_data)
        return goal

    def update(self, instance, validated_data):
        sub_objectives_data = validated_data.pop('sub_objectives', None)

        if 'domain' in validated_data:
            instance.domain = validated_data.pop('domain') 
        if 'profile' in validated_data:
            instance.profile = validated_data.pop('profile')

        instance.title = validated_data.get('title', instance.title)
        instance.title_ar = validated_data.get('title_ar', instance.title_ar)
        instance.description = validated_data.get('description', instance.description)
        instance.description_ar = validated_data.get('description_ar', instance.description_ar)
        instance.target_date = validated_data.get('target_date', instance.target_date)
        instance.priority = validated_data.get('priority', instance.priority)
        instance.save()

        if sub_objectives_data is not None:
            existing_sub_objective_ids = [sub.id for sub in instance.sub_objectives.all()]
            incoming_sub_objective_ids = []
            for sub_objective_data in sub_objectives_data:
                sub_objective_id = sub_objective_data.get('id')
                if sub_objective_id:
                    SubObjective.objects.filter(id=sub_objective_id, goal=instance).update(
                        description=sub_objective_data['description'],
                        is_completed=sub_objective_data['is_completed']
                    )
                    incoming_sub_objective_ids.append(sub_objective_id)
                else:
                    SubObjective.objects.create(goal=instance, **sub_objective_data)

            sub_objectives_to_delete_ids = list(set(existing_sub_objective_ids) - set(incoming_sub_objective_ids))
            SubObjective.objects.filter(id__in=sub_objectives_to_delete_ids).delete()

        return instance