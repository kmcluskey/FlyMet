from django import forms
from django.core.mail import send_mail


# make sure this is at the top if it isn't already

# our new form
class ContactForm(forms.Form):
    contact_name = forms.CharField(required=True)
    contact_email = forms.EmailField(required=True)
    content = forms.CharField(
        required=True,
        widget=forms.Textarea
    )



send_mail('Subject here', 'Here is the message.', 'from@example.com', ['to@example.com'], fail_silently=False)