#!/usr/bin/env python
#
# Wrapper around spid-testenv.py which:
#  - create certificates
#  - load data from environment

from argparse import ArgumentParser
from os import mkdir
from os.path import exists
from os.path import join as pjoin
from shlex import split
from socket import gethostbyname, gethostname
from subprocess import check_output

import yaml

# Default  settings.
hostname = gethostbyname(gethostname())
basedir = ".tmpdir"


def mkcert(key_path, cert_path, hostname, ou):
    ssl_command = (
        r"openssl req -x509 -nodes -sha256"
        r' -subj "/C=IT/ST=Lazio/O=MyCompany/OU={ou}/CN={hostname}"'
        r" -newkey rsa:2048 -keyout {key_path} -out {cert_path}"
    )

    safe_system(
        ssl_command.format(
            key_path=key_path, cert_path=cert_path, hostname=hostname, ou="IDP"
        )
    )


def safe_system(cmd):
    return check_output(split(cmd))


if __name__ == "__main__":
    # Add parameters to config file.
    parser = ArgumentParser()
    parser.add_argument(
        "-c",
        dest="config",
        help="Path to configuration file.",
        default="./conf/config.yaml",
    )
    parser.add_argument(
        "-ct",
        dest="configuration_type",
        help="Configuration type [yaml|json]",
        default="yaml",
    )
    parser.add_argument(
        "--dummy-config",
        dest="dummy_config",
        action="store_true",
        help="Run with a dummy config with https and self-signed certificates in .tmpdir/",
        default=False,
    )
    parser.add_argument(
        "--insecure-add-sp",
        dest="insecure_sp",
        required=False,
        help="Provision a service provider from metadata url",
        default=False,
    )

    args = parser.parse_args()

    if not exists(basedir):
        mkdir(basedir)

    # If config file does not exists, create a default.
    if args.dummy_config:
        dummy_config = {
            "base_url": None,
            "debug": True,
            "endpoints": {
                "single_logout_service": "/slo",
                "single_sign_on_service": "/sso",
            },
            "host": "0.0.0.0",
            "https": True,
            "https_key_file": pjoin(basedir, hostname + ".key"),
            "https_cert_file": pjoin(basedir, hostname + ".crt"),
            "metadata": {},
            "cert_file": pjoin(basedir, "localhost.crt"),
            "key_file": pjoin(basedir, "localhost.key"),
            "port": 8088,
        }
        dummy_config["base_url"] = "https://{hostname}:{port}".format(
            hostname=hostname, **dummy_config
        )

        if not exists(dummy_config["cert_file"]) and not exists(
            dummy_config["key_file"]
        ):
            mkcert(
                key_path=dummy_config["key_file"],
                cert_path=dummy_config["cert_file"],
                hostname="localhost",
                ou="IDP",
            )

        if not exists(dummy_config["https_cert_file"]) and not exists(
            dummy_config["https_key_file"]
        ):
            mkcert(
                key_path=dummy_config["https_key_file"],
                cert_path=dummy_config["https_cert_file"],
                hostname=hostname,
                ou="Website",
            )

        if args.insecure_sp:
            metadata_path = pjoin(
                basedir, "_" + args.insecure_sp.replace("/", "_") + ".xml"
            )
            safe_system(
                "curl -k {metadata_url} -o {metadata_path}".format(
                    metadata_path=metadata_path, metadata_url=args.insecure_sp
                )
            )
            if not dummy_config.get("metadata"):
                dummy_config["metadata"] = {"local": [], "remote": []}
            dummy_config["metadata"]["local"].append(metadata_path)

        # Write down a dummy config file.
        args.config = pjoin(basedir, "dummy.yaml")
        with open(args.config, "w") as fh:
            yaml.dump(dummy_config, fh, default_flow_style=0)

    argmap = {"-c": "config", "-ct": "configuration_type"}
    cmd_string = "/usr/bin/env python spid-testenv.py"
    for a, v in argmap.items():
        if getattr(args, v):
            cmd_string += " {} {} ".format(a, getattr(args, v))

    safe_system(cmd_string)
