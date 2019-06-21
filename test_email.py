def test_email():
    # using SendGrid's Python Library
    # https://github.com/sendgrid/sendgrid-python

    message = Mail(
        from_email='webmaster@flymet.org',
        to_emails='webmaster@flymet.org',
        subject='Sending with Twilio SendGrid is Fun',
        html_content='<strong>and easy to do anywhere, even with Python</strong>')
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)
