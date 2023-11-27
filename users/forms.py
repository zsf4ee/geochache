from django import forms

class GeoCacheForm(forms.Form):
    name = forms.CharField(label='Name', max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(label='Description', max_length=350, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Password', required=False, max_length=50, initial="", widget=forms.TextInput(attrs={'class': 'form-control'}))
    location = forms.CharField(widget=forms.HiddenInput())
    radius = forms.DecimalField(label="Radius", widget=forms.HiddenInput(attrs={'class': 'form-control-range'}),max_digits=6, decimal_places= 3)



class CommentForm(forms.Form):
    text = forms.CharField(label='Comment', max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))

class DeclineForm(forms.Form):
    text = forms.CharField(label='Reasoning', max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))

class HintForm(forms.Form):
    text = forms.CharField(label='Hint:', max_length=150)

