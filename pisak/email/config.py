"""
Email settings.
"""
import configobj

from pisak import res


"""
Path to a file where all the neccessary setting of an email account are stored.
"""
EMAIL_SETUP = res.get("email_setup.ini")


def get_account_setup():
    """
    Get previously saved email account settings.

    :returns: config object with email settings
    """
    return configobj.ConfigObj(EMAIL_SETUP, encoding='UTF8')


def save_account_setup(server_address, user_address, port_out=587, port_in=993,
                       password=None, keyfile=None, certfile=None):
    """
    Save server and email account settings to a file.

    :param server_address: address of the server that the email account is on
    :param user_address: user address for the email account
    :param port_out: port used for outcoming mail
    :param port_in: port used for incoming mail
    :param password: password to the email account
    :param key file: path to the file containing key
    :param certfile: path to the file containing certificate
    """
    setup = configobj.ConfigObj(EMAIL_SETUP, encoding='UTF8')
    setup["server_address"] = server_address
    setup["user_address"] = user_address
    setup["port_out"] = port_out
    setup["port_in"] = port_in
    if password:
        setup["password"] = encrypt_password(password)
    if keyfile:
        setup["keyfile"] = keyfile
    if certfile:
        setup["certfile"] = certfile
    setup.write()


def decrypt_password(encrypted):
    """
    Decrypt the given encrypted password.

    :param encrypted: encrypted password

    :returns: decrypted password
    """
    if isinstance(encrypted, str):
        return "".join([chr(ord(sign)-1) for sign in list(encrypted)[::-1]])


def encrypt_password(password):
    """
    Not very safe solution. Only for people who really are unable to remember
    their password. Anyone who gets here will be able to decrypt
    the password so we do not need to be very inventive.

    :param password: not encrypted password
    """
    return "".join([chr(ord(sign)+1) for sign in list(password)[::-1]])