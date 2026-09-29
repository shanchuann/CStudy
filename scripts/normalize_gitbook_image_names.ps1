$ErrorActionPreference = 'Stop'
$repo = 'D:\Code\C++code\TheGitbookLibrary\C语言圣经'
$assetDir = Join-Path $repo '.gitbook\assets\book-images\c-learning'
$files = Get-ChildItem $assetDir -File | Sort-Object Name
$map = @{}
$index = 1
foreach ($file in $files) {
    if ($file.Name -match '^[A-Za-z0-9._-]+$') { continue }
    $newName = ('c-learning-{0:D2}{1}' -f $index, $file.Extension.ToLowerInvariant())
    $target = Join-Path $assetDir $newName
    Move-Item -LiteralPath $file.FullName -Destination $target
    $map[$file.Name] = $newName
    $index++
}

foreach ($md in Get-ChildItem $repo -Filter '*.md' -File) {
    $text = [IO.File]::ReadAllText($md.FullName, [Text.Encoding]::UTF8)
    foreach ($old in $map.Keys) {
        $text = $text.Replace(".gitbook/assets/book-images/c-learning/$old", ".gitbook/assets/book-images/c-learning/$($map[$old])")
    }
    [IO.File]::WriteAllText($md.FullName, $text, [Text.UTF8Encoding]::new($false))
}
Write-Output "normalized $($map.Count) image names"
