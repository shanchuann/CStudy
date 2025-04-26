# PowerShell script to copy main.c files from exercises to answer folder
# and rename them with exercise prefix

$exercisesDir = "d:\c language\CStudy\exercises"
$answerDir = "d:\c language\CStudy\answer"

# Get all exercise subdirectories
$exerciseDirs = Get-ChildItem -Path $exercisesDir -Directory

foreach ($dir in $exerciseDirs) {
    $mainPath = Join-Path -Path $dir.FullName -ChildPath "main.c"
    
    if (Test-Path -Path $mainPath) {
        # Extract exercise prefix (e.g. "11_10_virtual_machine")
        $prefix = $dir.Name
        
        # Create new filename (e.g. "11_10_virtual_machine_main.c")
        $newName = "${prefix}_main.c"
        $destPath = Join-Path -Path $answerDir -ChildPath $newName
        
        # Copy the file
        Copy-Item -Path $mainPath -Destination $destPath -Force
        Write-Host "Copied $mainPath to $destPath"
    }
}

Write-Host "All main.c files have been copied and renamed successfully!"