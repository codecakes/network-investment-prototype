import requests
def send_email(subject, body, receipient_emails, from_email="postmaster"):
    domain = os.environ['DOMAIN_NAME']
    return requests.post(
        "https://api.mailgun.net/v3/%s/messages" %(domain),
        auth=("api", os.environ['MAILGUN_API_KEY']),
        data={"from": "AviCrypto <mailgun@%s>" %(domain),
              "to": receipient_emails,
              "subject": subject,
              "text": body})