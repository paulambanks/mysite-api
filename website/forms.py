from django import forms
from .models import Post, TaggedPost, SharedPost, Tag
from tinymce.widgets import TinyMCE


class TinyMCEWidget(TinyMCE):
    def use_required_attribute(self, *args):
        return False


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'content', 'privacy',)
        widgets = {
            'content': TinyMCE(attrs={
                'required': True,
                'cols': 80,
                'rows': 30
                }
            )
        }


class TagPostForm(forms.ModelForm):

    class Meta:
        model = TaggedPost
        fields = ('tag', )


class SharedPostForm(forms.ModelForm):

    class Meta:
        model = SharedPost
        fields = ('user',)


class ContactForm(forms.Form):
    subject = forms.CharField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)
    name = forms.CharField(required=True)
    email = forms.CharField(required=False)

