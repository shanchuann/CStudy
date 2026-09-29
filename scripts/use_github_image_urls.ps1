$ErrorActionPreference = 'Stop'
$repoRoot = 'D:\Code\C++code\TheGitbookLibrary\C语言圣经'
$rawRoot = 'https://raw.githubusercontent.com/shanchuann/TheGitbookLibrary/main/C%E8%AF%AD%E8%A8%80%E5%9C%A3%E7%BB%8F/.gitbook/assets'

foreach ($md in Get-ChildItem $repoRoot -Filter '*.md' -File) {
    $text = [IO.File]::ReadAllText($md.FullName, [Text.Encoding]::UTF8)
    $text = $text.Replace('](.gitbook/assets/', "]($rawRoot/")
    [IO.File]::WriteAllText($md.FullName, $text, [Text.UTF8Encoding]::new($false))
}
Write-Output 'converted GitBook image references to GitHub raw URLs'
