from os.path import join as pjoin
from shlex import split
from socket import gethostbyname, gethostname
from subprocess import check_output


def mkcert(key_path, cert_path, hostname, ou):
    ssl_command = (
        r"openssl req -x509 -nodes -sha256"
        r' -subj "/C=IT/ST=Lazio/O=MyCompany/OU={ou}/CN={hostname}"'
        r" -newkey ec -pkeyopt ec_paramgen_curve:secp256k1"
        r" -keyout {key_path} -out {cert_path}"
    )

    safe_system(
        ssl_command.format(
            key_path=key_path, cert_path=cert_path, hostname=hostname, ou=ou
        )
    )


def safe_system(cmd):
    return check_output(split(cmd))


def init_certs():
    # Default  settings.
    hostname = gethostbyname(gethostname())
    basedir = '.tmpdir'
    dummy_config = {
        'entityId': 'https://{hostname}/aa/v1/metadata'.format(hostname=hostname),
        'https_key_file': pjoin(basedir, hostname + '.key'),
        'https_cert_file': pjoin(basedir, hostname + '.crt'),
    }
    mkcert(dummy_config['https_key_file'],
           dummy_config['https_cert_file'], hostname, 'AA')
    dummy_config.update({
        "privateKey": open(dummy_config['https_key_file']).read(),
        "x509cert": open(dummy_config['https_cert_file']).read(),
    })
    return dummy_config
