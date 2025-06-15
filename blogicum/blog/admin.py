from django.contrib import admin
from .models import Category, Comment, Location, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'slug',
                    'is_published', 'created_at')
    list_editable = ('description', 'slug', 'is_published')
    search_fields = ('title',)
    list_filter = ('is_published', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'created_at')
    list_editable = ('is_published',)
    search_fields = ('name',)
    list_filter = ('is_published', 'created_at')
    date_hierarchy = 'created_at'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
        'created_at'
    )
    list_editable = ('is_published',)
    search_fields = ('title', 'text', 'author__username')
    list_filter = ('category', 'location', 'pub_date',
                   'is_published', 'created_at')
    date_hierarchy = 'pub_date'
    filter_horizontal = ()
    raw_id_fields = ('author',)
    prepopulated_fields = {}
    readonly_fields = ('created_at',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'author', 'post', 'created_at', 'short_text')
    search_fields = ('text', 'author__username', 'post__title')
    list_filter = ('created_at', 'author')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)

    def short_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    short_text.short_description = 'Краткий текст'
