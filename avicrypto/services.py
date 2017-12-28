import requests
uri = 'https://api.mailgun.net/v3/avicrypto.us/messages'
key = 'key-1055741f06d43a548bf5def6962b536a'

def send_email_mailgun(subject, body, receipient_emails, from_email="postmaster"):
    data = {"from": "AviCrypto <mail@avicrypto.us>",
              "to": receipient_emails,
              "subject": subject,
              "text": body}
    return requests.post(
        uri,auth=("api", key),
        data=data)


def support_mail(subject, body, receipient_emails, from_email="postmaster"):
    data = {"from": "AviCrypto <mail@avicrypto.us>",
              "to": receipient_emails,
              "subject": subject,
              "text": body}
    return requests.post(
        uri,auth=("api", key),
        data=data)