from lxml.etree import parse
from requests import get
from six import StringIO


def create_idp_config(idp_metadata_url):
    def _get_item(item, key=None):
        tag = idp_metadata.findall(item)[0]
        if key:
            return dict(tag.items()).get(key)
        # Return the first text line.
        return next(tag.itertext())

    SSO = '//{urn:oasis:names:tc:SAML:2.0:metadata}SingleSignOnService'
    SLO = '//{urn:oasis:names:tc:SAML:2.0:metadata}SingleLogoutService'
    X509 = '//{http://www.w3.org/2000/09/xmldsig#}X509Certificate'

    idp_metadata = download_idp_metadata(idp_metadata_url)
    return {
        "singleLogoutService": {
            "url": _get_item(SLO, 'Location'),
            "binding": _get_item(SLO, 'Binding')
        },
        "singleSignOnService": {
            "url": _get_item(SSO, 'Location'),
            "binding": _get_item(SSO, 'Binding')
        },
        "entityId": _get_item(".", "entityID"),
        "x509cert": encode_pem(_get_item(X509))
    }


def encode_pem(cert):
    if cert.startswith("-"):
        return cert

    return '\n'.join((
        "-----BEGIN CERTIFICATE-----",
        cert.strip("\n"),
        "-----END CERTIFICATE-----"
    ))


def download_idp_metadata(idp_metadata_url):
    idp_metadata = get(idp_metadata_url, verify=False, timeout=0.01)
    idp_metadata_xml = idp_metadata.content.decode()
    return parse(StringIO(idp_metadata_xml))
