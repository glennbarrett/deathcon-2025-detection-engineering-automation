import subprocess

# Invoke-Command can also be used on a remote system with -ComputerName parameter
subprocess.call('C:\\Windows\\SysWOW64\\WindowsPowerShell\\v1.0\\powershell.exe Invoke-Command {ping google.com}', shell=True)