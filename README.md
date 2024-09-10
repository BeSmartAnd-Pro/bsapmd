
# BeSmartAndPro Monitoring Downloader

This Python application allows downloading certificates from the BeSmartAndPro monitoring service. It supports fetching certificates using an API token and can restart Apache automatically after downloading the certificates. The application can be configured via command-line arguments, environment variables, or a YAML configuration file.

## Features
- Fetch certificates from a specified URL.
- Supports downloading multiple certificates when using a configuration file.
- Optionally restarts Apache after the download is complete.
- Configurable via environment variables or a configuration file.
- Includes a `--version` flag to display the current version of the application.

## Usage

### 1. Command-line Arguments

You can pass the token, certificate name, and path directly using command-line arguments.

Example:

```bash
bsapmd --token YOUR_TOKEN --cert_id ID --cert_path /path/to/save/cert.pem --restart "/usr/sbin/service apache2 restart"
```

### 2. Environment Variables

The following environment variables are supported:

- `MONITORING_BESMARTANDPRO_TOKEN`: API token for accessing the certificates.
- `MONITORING_BESMARTANDPRO_CERT_ID`: The ID of the certificate to download.
- `MONITORING_BESMARTANDPRO_CERT_PATH`: The path where the certificate will be saved.

Example:

```bash
export MONITORING_BESMARTANDPRO_TOKEN="your_token"
export MONITORING_BESMARTANDPRO_CERT_ID="ID"
export MONITORING_BESMARTANDPRO_CERT_PATH="/etc/ssl/certs/cert1.pem"
bsapmd
```

### 3. Configuration File

You can also configure the application using a YAML file located at `/etc/besmartandpro/monitoring.yaml`. This file allows defining multiple certificates to download.

Example configuration (`/etc/besmartandpro/monitoring.yaml`):

```yaml
token: "your_token"
restart_hook: "/usr/sbin/service apache2 restart"
certificates:
  - id: "ID"
    path: "/etc/ssl/certs/cert1.pem"
  - id: "ID"
    path: "/etc/ssl/certs/cert2.pem"
```

In this case, the application will download both `ID` and `ID` and save them to their respective paths.

### 4. Restart Apache

To automatically restart service after downloading certificates, you can provide a restart command in the configuration file or via the `--restart` argument.

Example:

```bash
bsapmd --restart "/usr/sbin/service apache2 restart"
```

### Help and Version

- Display help:

  ```bash
  bsapmd --help
  ```

- Display version:

  ```bash
  bsapmd --version
  ```

## Example Usages

- Using command-line arguments:

  ```bash
  bsapmd --token "your_token" --cert_id "ID" --cert_path "/etc/ssl/certs/cert1.pem"
  ```

- Using environment variables:

  ```bash
  export MONITORING_BESMARTANDPRO_TOKEN="your_token"
  export MONITORING_BESMARTANDPRO_CERT_ID="ID"
  export MONITORING_BESMARTANDPRO_CERT_PATH="/etc/ssl/certs/cert1.pem"
  bsapmd
  ```

- Using a configuration file to download multiple certificates (which you can always download from URL):

  ```yaml
  token: "your_token"
  restart_hook: "/usr/sbin/service apache2 restart"
  certificates:
    - id: "ID"
      path: "/etc/ssl/certs/cert1.pem"
    - id: "ID"
      path: "/etc/ssl/certs/cert2.pem"
  ```

## License

This project is licensed under the AGPL-3.0 License.
