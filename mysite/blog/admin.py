from django.contrib import admin
from .models import Post, Feedback

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at', 'published')
    list_filter = ('created_at', 'updated_at', 'published')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['email', 'message', 'created_at']

admin.site.register(Post, PostAdmin)
