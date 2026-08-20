$lines = Get-Content -Path 'c:\Users\Monfared\Desktop\abarham_quick\index.html'
$match = $lines | Select-String 'Service Worker' | Select-Object -First 1
$index = $match.LineNumber - 1
$insert = @(
    '    // Dev-only unregister',
    '    if (location.hostname === ''localhost'' || location.hostname === ''127.0.0.1'' || location.search.includes(''dev=1'')) {',
    '        navigator.serviceWorker.getRegistrations().then(registrations => {',
    '            for (let registration of registrations) {',
    '                registration.unregister();',
    '            }',
    '        });',
    '    '
)
$newLines = $lines[0..$index] + $insert + $lines[($index+1)..$lines.Length]
Set-Content -Encoding UTF8 -Path 'c:\Users\Monfared\Desktop\abarham_quick\index.html' -Value $newLines