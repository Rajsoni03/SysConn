# Data Directory

This directory contains data files used by the `SysConn` project.

## Structure

- Store datasets, configuration files, or other resources required by the application.
- Do not commit sensitive or large files to version control.

## Config File

- `config.json`: Main configuration file for the application. It includes settings such as authentication tokens, sudo passwords, and other configurable parameters.

### Example

```json
{
    "AUTH_TOKEN": "your-auth-token",
    "SUDO_PASSWORD": "your-sudo-password"
}
```

## Notes

- Ensure sensitive information is not committed to version control.
- Refer to the main project README for deployment instructions.