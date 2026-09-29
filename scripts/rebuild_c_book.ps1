$ErrorActionPreference = 'Stop'
$base = 'D:\Markdown\C语言圣经-原稿备份.md'
$text = [System.IO.File]::ReadAllText($base, [System.Text.Encoding]::UTF8)

function Read-Fragment([string]$name) {
    return [System.IO.File]::ReadAllText((Join-Path $PSScriptRoot ("book_fragments\" + $name)), [System.Text.Encoding]::UTF8)
}

function Insert-Before([string]$marker, [string]$fragment) {
    $match = [regex]::Match($script:text, '(?m)^' + [regex]::Escape($marker) + '[ \t]*\r?$')
    if (-not $match.Success) { throw "Marker not found: $marker" }
    $script:text = $script:text.Substring(0, $match.Index) + $fragment + "`r`n" + $script:text.Substring($match.Index)
}

function Insert-After([string]$marker, [string]$fragment) {
    $match = [regex]::Match($script:text, '(?m)^' + [regex]::Escape($marker) + '[ \t]*\r?$')
    if (-not $match.Success) { throw "Marker not found: $marker" }
    $end = $match.Index + $match.Length
    if ($script:text.Substring($end, 2) -eq "`r`n") { $end += 2 }
    elseif ($script:text.Substring($end, 1) -eq "`n") { $end += 1 }
    $script:text = $script:text.Substring(0, $end) + "`r`n" + $fragment + $script:text.Substring($end)
}

Insert-Before '## 标识符,变量' (Read-Fragment 'float.md')
Insert-Before '### 7. 逗号运算符' (Read-Fragment 'bitops.md')
Insert-Before '## 可见性和生存期' (Read-Fragment 'recursion.md')
Insert-Before '## 关键字' (Read-Fragment 'structs.md')
Insert-After '## 动态内存' (Read-Fragment 'dynamic.md')
Insert-Before '## 动态内存' (Read-Fragment 'preprocessor.md')
Insert-Before '## 字符串' (Read-Fragment 'files.md')

$utf8 = [System.Text.UTF8Encoding]::new($false)
[System.IO.File]::WriteAllText('D:\Markdown\C语言圣经.md', $text, $utf8)
[System.IO.File]::WriteAllText('D:\Markdown\C语言圣经-完善版.md', $text, $utf8)
Write-Output "rebuilt $($text.Length) chars"
