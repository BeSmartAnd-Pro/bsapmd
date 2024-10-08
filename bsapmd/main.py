import os
import requests
import yaml
import argparse
import subprocess
import hashlib
import importlib.metadata
from bsapmd import __version__

CONFIG_PATH = "/etc/besmartandpro/monitoring.yaml"
DEFAULT_URL_TEMPLATE = "https://monitoring.besmartand.pro/smallend/{token}/certyfikat/{cert_id}"

def load_config():
    """Load configuration from YAML file."""

    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as file:
            return yaml.safe_load(file)
    return {}

def get_token_from_env():
    """Get token from environment variable."""
    return os.getenv("MONITORING_BESMARTANDPRO_TOKEN")

def calculate_checksum(file_path):
    """Calculate the SHA256 checksum of the given file."""
    sha256_hash = hashlib.sha256()

    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        return None

def download_certificate(token, cert_id):
    """Download certificate from server and return its content."""
    url = DEFAULT_URL_TEMPLATE.format(token=token, cert_id=cert_id)
    response = requests.get(url)

    if response.status_code == 200:
        print(f"Successfully downloaded certificate {cert_id}.")
        return response.content
    else:
        print(f"Failed to download certificate {cert_id}, status: {response.status_code}")
        response.raise_for_status()

def save_certificate(cert_content, cert_path):
    """Save certificate content to file."""
    with open(cert_path, "wb") as file:
        file.write(cert_content)
    print(f"Certificate saved to {cert_path}.")

def restart_hook_service(hook):
    """Restart service using the provided hook."""
    try:
        subprocess.run(hook, shell=True, check=True)
        print("Service successfully restarted.")
    except subprocess.CalledProcessError as e:
        print(f"Error restarting service: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Download certificate(s) and optionally restart service.",
        epilog="You can specify the token, certificate id, and path via environment variables or configuration file."
    )

    parser.add_argument('--token', help='API token for accessing the certificates.')
    parser.add_argument('--cert_id', help='Id of the certificate to download.')
    parser.add_argument('--cert_path', help='Path where the certificate will be saved.')
    parser.add_argument('--restart', help='Path to the hook script for restarting service.')
    parser.add_argument('--version', '-v', action='version', version=f'%(prog)s (c) BeSmartAnd.Pro sp. z o.o. {__version__}')
    
    args = parser.parse_args()

    # Get token from argument, environment variable, or configuration file
    token = args.token or get_token_from_env() or load_config().get('token')
    
    if not token:
        print("No token provided. Use the --token argument, MONITORING_BESMARTANDPRO_TOKEN environment variable, or define it in the configuration file.")
        return

    # Get certificates from arguments or config file
    config = load_config()
    cert_id = args.cert_id or os.getenv("MONITORING_BESMARTANDPRO_CERT_ID")
    cert_path = args.cert_path or os.getenv("MONITORING_BESMARTANDPRO_CERT_PATH")

    if cert_id and cert_path:
        existing_checksum = calculate_checksum(cert_path)
        cert_content = download_certificate(token, cert_id)

        # Calculate checksum of the downloaded certificate
        new_checksum = hashlib.sha256(cert_content).hexdigest()

        if existing_checksum != new_checksum:
            save_certificate(cert_content, cert_path)
            hook = args.restart or config.get('restart_hook')

            if hook:
                restart_hook_service(hook)
        else:
            print(f"Certificate {cert_id} is up-to-date. No download needed.")
    elif 'certificates' in config:
        for cert in config['certificates']:
            id = cert.get('id')
            path = cert.get('path')

            if id and path:
                existing_checksum = calculate_checksum(path)
                cert_content = download_certificate(token, id)

                # Calculate checksum of the downloaded certificate
                new_checksum = hashlib.sha256(cert_content).hexdigest()

                if existing_checksum != new_checksum:
                    save_certificate(cert_content, path)
                    hook = args.restart or config.get('restart_hook')

                    if hook:
                        restart_hook_service(hook)
                else:
                    print(f"Certificate {id} is up-to-date. No download needed.")
            else:
                print("Missing required fields (id/path) for a certificate in the configuration file.")
    else:
        print("No certificate provided. Use --cert_id and --cert_path arguments or define certificates in the configuration file.")

if __name__ == "__main__":
    main()
