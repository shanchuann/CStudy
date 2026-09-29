$ErrorActionPreference = 'Stop'
$repo = 'D:\Code\C++code\TheGitbookLibrary\C语言圣经'
$files = @(
    @{ Path = 'compile.md'; Title = 'C语言编译链接过程' },
    @{ Path = 'c-program.md'; Title = 'C程序' },
    @{ Path = 'number-systems.md'; Title = '进制转换' }
)

$parts = [System.Collections.Generic.List[string]]::new()
foreach ($item in $files) {
    $raw = [IO.File]::ReadAllText((Join-Path $repo $item.Path), [Text.Encoding]::UTF8)
    $body = [regex]::Replace($raw, '(?s)^---\r?\n.*?\r?\n---\r?\n', '')
    $body = [regex]::Replace($body, '(?m)^# ' + [regex]::Escape($item.Title) + '\r?\n?', '')
    $body = $body.Trim()
    $parts.Add("## $($item.Title)`n`n$body")
}

$frontmatter = "---`n`ndescription: C 语言基础：编译、源程序结构与进制转换。`nicon: code`n---`n`n# C语言基础`n`n"
$merged = $frontmatter + ($parts -join "`n`n") + "`n"
[IO.File]::WriteAllText((Join-Path $repo 'c-language-basics.md'), $merged, [Text.UTF8Encoding]::new($false))

$summaryPath = Join-Path $repo 'SUMMARY.md'
$summary = [IO.File]::ReadAllText($summaryPath, [Text.Encoding]::UTF8)
$summary = $summary.Replace("* [C语言编译链接过程](compile.md)`n* [C程序](c-program.md)`n* [进制转换](number-systems.md)", "* [C语言基础](c-language-basics.md)")
[IO.File]::WriteAllText($summaryPath, $summary, [Text.UTF8Encoding]::new($false))

foreach ($item in $files) { Remove-Item -LiteralPath (Join-Path $repo $item.Path) -Force }
Write-Output 'merged compile, program, and number-system chapters'
