from django import forms
from .models import Post, Comment, Feedback

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['email', 'message', 'image']