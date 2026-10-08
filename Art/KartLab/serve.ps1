$taskRoot = $PSScriptRoot
$taskPython = 'C:\Users\GBURG-4\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $taskPython -m http.server 8086 --bind 127.0.0.1 --directory $taskRoot
