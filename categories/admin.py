from django.contrib import admin
from .models import Category, Domain, Item


# Inline pour afficher les domaines dans la catégorie
class DomainInline(admin.StackedInline):
    model = Domain
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'created_date', 'items_count', 'domains_count')
    search_fields = ('code', 'title')
    inlines = [DomainInline]


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'description', 'category')
    search_fields = ('code', 'title')
    list_filter = ('category',)
    filter_horizontal = ('items',)  # Pour gérer les items ManyToMany facilement dans l'admin


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'description')
    search_fields = ('code', 'title')
