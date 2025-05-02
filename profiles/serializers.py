from django.db import transaction
from template_data.models import TemplateCategory
from .models import Profile
from profile_data.models import ProfileCategory, ProfileDomain, ProfileItem
from rest_framework import serializers

# class ProfileShareSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProfileShare
#         fields = ('id', 'profile', 'shared_with', 'can_read', 'can_write', 'can_update', 'can_delete')

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'
        extra_kwargs = {
            'bio': {'required': False, 'allow_null': True},
            'parent': {'read_only': True},
            'diagnosis': {'required': False, 'allow_null': True},
            'notes': {'required': False, 'allow_null': True},
            'evaluation_score': {'required': False},
            'objectives': {'required': False},
            'progress': {'required': False},
            'recommended_strategies': {'required': False},
            'image_url': {'required': False, 'allow_null': True},
        }
    def assign_template_data_to_profile(profile):
        """
        Copy all template categories, domains, and items to a profile.
        """
        with transaction.atomic():
            template_categories = TemplateCategory.objects.all()
            
            for template_category in template_categories:
                profile_category = ProfileCategory.objects.create(
                    profile=profile,
                    template_category=template_category,
                    name=template_category.name,
                    description=template_category.description
                )
                
                for template_domain in template_category.domains.all():
                    profile_domain = ProfileDomain.objects.create(
                        profile_category=profile_category,
                        template_domain=template_domain,
                        name=template_domain.name,
                        description=template_domain.description
                    )
                    
                    for template_item in template_domain.items.all():
                        # Map TemplateItem code to ProfileItem etat
                        code_to_etat = {
                            'A': 'ACQUIS',
                            'P': 'PARTIEL',
                            'N': 'NON_ACQUIS',
                            'X': 'NON_COTE'
                        }
                        etat = code_to_etat.get(template_item.code, 'NON_COTE')
                        ProfileItem.objects.create(
                            profile_domain=profile_domain,
                            template_item=template_item,
                            name=template_item.name,
                            description=template_item.description,
                            etat=etat
                        )