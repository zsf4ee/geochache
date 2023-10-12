from django import forms

class GeoCacheForm(forms.Form):
    name = forms.CharField(label='Name', max_length=50)
    description = forms.CharField(label='Description', max_length=350)
    hint = forms.CharField(label='Hint(Optional)', max_length=150, required=False)
    location = forms.CharField(widget=forms.HiddenInput())
    radius = forms.DecimalField(widget=forms.HiddenInput(),max_digits=6, decimal_places= 3)

class CommentForm(forms.Form):
    text = forms.CharField(label='Comment', max_length=255)