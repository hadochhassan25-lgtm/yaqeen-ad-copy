import os, sys, time

PYTHON = sys.executable
SCRIPT = os.path.join(os.path.dirname(__file__), "..", "services", "key_manager.py")
PARENT = os.path.dirname(SCRIPT)
TASK_NAME = "YaqeenKeyRefresh"

print("[Setup] PowerShell command to install Task Scheduler (copy & paste):")
print()
cmd = (
    '$action = New-ScheduledTaskAction -Execute '
    + f'"{PYTHON}" '
    + '-Argument "-c '
    + f'\\'import sys; sys.path.insert(0, \\\\\\'{PARENT}\\\\\\"\'); '
    + 'from key_manager import fetch_free_keys; fetch_free_keys()\\""; '
    + '$t = (Get-Date).AddMinutes(1); '
    + '$trigger = New-ScheduledTaskTrigger -Once -At $t -RepetitionInterval (New-TimeSpan -Hours 2) -RepetitionDuration (New-TimeSpan -Days 30); '
    + f'Register-ScheduledTask -TaskName "{TASK_NAME}" -Action $action -Trigger $trigger -User "$env:USERNAME" -Force'
)
print(cmd)
print()
print("To run now:")
print(f'  Start-ScheduledTask -TaskName "{TASK_NAME}"')
print()
print("To delete:")
print(f'  Unregister-ScheduledTask -TaskName "{TASK_NAME}" -Confirm:$false')
