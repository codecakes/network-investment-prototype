import requests
def send_email_mailgun(subject, body, receipient_emails, from_email="postmaster"):
    uri = 'https://api.mailgun.net/v3/avicrypto.us/messages'
    key = 'key-1055741f06d43a548bf5def6962b536a'
    data = {"from": "AviCrypto <mail@avicrypto.us>",
              "to": receipient_emails,
              "subject": subject,
              "text": body}
    return requests.post(
        uri,auth=("api", key),
        data=data)