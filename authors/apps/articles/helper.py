import sendgrid
from decouple import config
from sendgrid.helpers.mail import(
    Email,
    Mail,
    Content
)


def share_article(subject_and_host, sender, receiver_email, content):
    """
    This method formats how subject and content
    :param subject_and_host: subject and host list
    :param sender: senders email
    :param receiver_email: email address for the recipient
    :param content: the slug being shared
    :return:
    """
    subject = "{} shared an article with you via Authors Haven".format(subject_and_host[0])
    content = Content(
                        "text/plain",
                        "Hey there, \n {} "
                        "via Authors Haven service has shared an article with you. "
                        "Please click the link below to view the article."
                        "\nhttp://{}{}/".format(subject_and_host[0], subject_and_host[1], content)
                    )
    response = send_mail(sender, receiver_email, subject, content)
    return response


def send_mail(sender_email, receiver_mail, mail_subject, content):
    """
    This method shares sends out the email using send grid.
    :param sender_email: enders email
    :param receiver_mail: receiver's email
    :param mail_subject: rmail subject
    :param content: body to be shared
    :return:
    """
    sg = sendgrid.SendGridAPIClient(apikey=config('SENDGRID_API_KEY'))
    from_email = Email(sender_email)
    to_email = Email(receiver_mail)
    subject = mail_subject

    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    return response