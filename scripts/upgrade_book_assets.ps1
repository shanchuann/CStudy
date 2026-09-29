$ErrorActionPreference = 'Stop'
$book = 'D:\Markdown\C语言圣经.md'
$text = [System.IO.File]::ReadAllText($book, [System.Text.Encoding]::UTF8)
$root = 'D:\Markdown\assets\book-images'
$null = New-Item -ItemType Directory -Force -Path (Join-Path $root 'c-learning')
$null = New-Item -ItemType Directory -Force -Path (Join-Path $root 'typora')

$pattern = '!\[([^\]]*)\]\((D:\\Markdown\\asset\\[^)]+|C:\\Users\\15375\\AppData\\Roaming\\Typora\\typora-user-images\\[^)]+)\)'
$text = [regex]::Replace($text, $pattern, {
    param($m)
    $alt = $m.Groups[1].Value
    $source = $m.Groups[2].Value
    if (-not (Test-Path -LiteralPath $source)) {
        return $m.Value
    }
    $bucket = if ($source -like 'D:\Markdown\asset\c-learning*') { 'c-learning' } else { 'typora' }
    $targetName = [IO.Path]::GetFileName($source)
    $target = Join-Path (Join-Path $root $bucket) $targetName
    Copy-Item -LiteralPath $source -Destination $target -Force
    return "![$alt](assets/book-images/$bucket/$targetName)"
})

# This file was referenced by an obsolete local path and is replaced by a text diagram later.
$text = $text -replace '(?m)^!\[进程\]\([^\r\n]+\)\r?\n?', ''

$utf8 = [System.Text.UTF8Encoding]::new($false)
[IO.File]::WriteAllText($book, $text, $utf8)
[IO.File]::WriteAllText('D:\Markdown\C语言圣经-完善版.md', $text, $utf8)
Write-Output 'asset paths normalized'
