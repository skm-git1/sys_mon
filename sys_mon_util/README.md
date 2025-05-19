# System Monitor Utility

A cross-platform system monitoring utility that checks and reports system health status.

## Features

- Disk encryption status monitoring
- OS update status checking
- Antivirus presence and status verification
- System sleep settings compliance checking
- Background daemon with periodic checks
- Remote API reporting
- Cross-platform support (Windows, macOS, Linux)

## Installation

```bash
pip install .
```

## Configuration

Create a `config.yaml` file in the installation directory with the following options:

```yaml
api_endpoint: http://your-api-endpoint/status
check_interval: 900  # 15 minutes in seconds
log_level: INFO
log_file: system_monitor.log
```

## Usage

To run the monitor:

```bash
system_monitor
```

On Windows, you can set up the monitor as a service:

```powershell
# Create a new service (run as Administrator)
New-Service -Name "SystemMonitor" -BinaryPathName "python path\to\system_monitor.py" -Description "System Health Monitor" -StartupType Automatic
```

On Linux/macOS, you can use systemd or launchd to run the monitor as a service.

## Requirements

- Python 3.8 or higher
- See requirements.txt for package dependencies

## License

MIT License
