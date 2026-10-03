$ErrorActionPreference = 'Stop'
$source = 'D:\Markdown\C语言圣经.md'
$repo = 'D:\Code\C++code\TheGitbookLibrary\C语言圣经'
$text = [IO.File]::ReadAllText($source, [Text.Encoding]::UTF8)
$utf8 = [Text.UTF8Encoding]::new($false)

$sections = @{}
$matches = [regex]::Matches($text, '(?ms)^## (.+?)\r?\n(.*?)(?=^## |\z)')
foreach ($match in $matches) {
    $sections[$match.Groups[1].Value.Trim()] = $match.Groups[2].Value.Trim()
}

function Write-Page([string]$file, [string]$title, [string]$body, [string]$description) {
    $body = $body.Replace('assets/book-images/', '.gitbook/assets/book-images/')
    $body = $body.Replace('assets/c-language/', '.gitbook/assets/c-language/')
    $page = "---`r`ndescription: $description`r nicon: code`r`n---`r`n`r`n# $title`r`n`r`n$body`r`n"
    $page = $page.Replace("`r n", "`r`n")
    [IO.File]::WriteAllText((Join-Path $repo $file), $page, $utf8)
}

Write-Page 'README.md' '书籍介绍' $sections['书籍介绍'] '这本 C 语言书的写作说明与配套练习。'
Write-Page 'yin-yan.md' '引言' $sections['引言'] 'C 语言的过去、现在与未来。'

$mapping = [ordered]@{
    'C语言编译链接过程' = @('compile.md', '从源文件到可执行文件。')
    'C程序' = @('c-program.md', 'C 源程序的结构。')
    '进制转换' = @('number-systems.md', '二进制、八进制、十进制与十六进制。')
    '数据类型' = @('data-types.md', '整数、浮点数、字符和对象表示。')
    '标识符,变量' = @('identifiers-variables.md', '标识符、变量、作用域和存储。')
    'C语言输入输出' = @('io.md', '标准输入输出与格式化。')
    '常量' = @('constants.md', '字面量、宏常量、枚举和字符串常量。')
    '控制语句，随机数' = @('control-flow.md', '条件、循环、跳转和随机数。')
    '数组' = @('arrays.md', '一维数组、二维数组和字符串数组。')
    '函数' = @('functions.md', '函数参数、返回值和模块化。')
    '可见性和生存期' = @('scope-lifetime.md', '作用域、存储期和程序内存区域。')
    '运算符' = @('operators.md', '算术、逻辑、关系和位运算。')
    '指针' = @('pointers.md', '地址、解引用、数组和动态对象。')
    '函数指针' = @('function-pointers.md', '回调、表驱动和泛型接口。')
    '结构体' = @('structs.md', '结构体、联合体、枚举和布局。')
    '关键字' = @('keywords.md', 'C 语言关键字与存储类别。')
    '动态内存' = @('dynamic-memory.md', 'malloc、calloc、realloc 和 free。')
    '多文件结构' = @('multi-file.md', '头文件、链接和模块边界。')
    '字符串' = @('strings.md', '字符串函数、格式化和安全边界。')
    '内存操作函数' = @('memory-functions.md', 'memset、memcmp、memcpy 和 memmove。')
    '打字母游戏' = @('typing-game.md', '用 C 组织一个小型终端练习程序。')
    '附件' = @('appendix.md', '数据类型、格式字符串、ASCII 和 limits.h。')
}

$summary = @('# C 语言圣经', '', '* [书籍介绍](README.md)', '* [引言](yin-yan.md)')
foreach ($item in $mapping.GetEnumerator()) {
    $title = $item.Key
    if (-not $sections.ContainsKey($title)) { throw "Missing section: $title" }
    Write-Page $item.Value[0] $title $sections[$title] $item.Value[1]
    $summary += "* [$title]($($item.Value[0]))"
}
[IO.File]::WriteAllText((Join-Path $repo 'SUMMARY.md'), ($summary -join "`r`n") + "`r`n", $utf8)

$assets = Join-Path $repo '.gitbook\assets'
$null = New-Item -ItemType Directory -Force -Path $assets
Copy-Item -LiteralPath 'D:\Markdown\assets\book-images' -Destination $assets -Recurse -Force
Copy-Item -LiteralPath 'D:\Markdown\assets\c-language' -Destination $assets -Recurse -Force
Write-Output "synced $($mapping.Count + 2) pages"
