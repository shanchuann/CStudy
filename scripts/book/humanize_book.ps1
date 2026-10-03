$ErrorActionPreference = 'Stop'
$book = 'D:\Markdown\C语言圣经.md'
$lines = [System.Collections.Generic.List[string]]::new()
$inFence = $false

foreach ($line in [IO.File]::ReadAllLines($book, [Text.Encoding]::UTF8)) {
    if ($line.TrimStart().StartsWith('```')) {
        $inFence = -not $inFence
        $lines.Add($line)
        continue
    }
    if ($inFence -or $line.TrimStart().StartsWith('|') -or $line.TrimStart().StartsWith('![')) {
        $lines.Add($line)
        continue
    }
    $line = $line.Replace('此外', '还')
    $line = $line.Replace('值得一提的是，', '注意：')
    $line = $line.Replace('值得注意的是，', '注意：')
    $line = $line.Replace('在实际开发中', '实际开发中')
    $line = $line.Replace('非常浪费实践', '很浪费时间')
    $line = $line.Replace('非常浪费时间', '很浪费时间')
    $line = $line.Replace('关键性的', '关键的')
    $line = $line.Replace('至关重要的', '重要的')
    $line = $line.Replace('确保', '保证')
    $line = $line.Replace('我们可以', '可以')
    $line = $line.Replace('我们将', '本书将')
    $line = $line.Replace('不仅仅是', '不只是')
    $line = $line.Replace('显著地', '明显地')
    $line = $line.Replace('显著', '明显')
    $line = $line.Replace('深刻地体会', '更清楚地理解')
    $line = $line.Replace('以此类推', '按同样的规则继续')
    $line = $line.Replace('swich', 'switch')
    $line = $line.Replace('他与', '它与')
    $line = $line.Replace('多赘述', '多说')
    $lines.Add($line)
}

$text = [string]::Join("`r`n", $lines)
$utf8 = [Text.UTF8Encoding]::new($false)
[IO.File]::WriteAllText($book, $text, $utf8)
[IO.File]::WriteAllText('D:\Markdown\C语言圣经-完善版.md', $text, $utf8)
Write-Output 'humanizer pass complete'
