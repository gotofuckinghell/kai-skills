Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Storage.StorageFile,Windows.Storage,ContentType=WindowsRuntime]
$null = [Windows.Media.Ocr.OcrEngine,Windows.Foundation,ContentType=WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder,Windows.Foundation,ContentType=WindowsRuntime]
$null = [Windows.Globalization.Language,Windows.Foundation,ContentType=WindowsRuntime]

function Await($WinRtTask, $ResultType) {
    $asTask = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
    $asTaskGeneric = $asTask.MakeGenericMethod($ResultType)
    $netTask = $asTaskGeneric.Invoke($null, @($WinRtTask))
    $netTask.Wait(-1) | Out-Null
    $netTask.Result
}

param(
    [Parameter(Mandatory=$true)][string]$InDir,
    [Parameter(Mandatory=$true)][string]$OutFile
)

$files = Get-ChildItem -LiteralPath $InDir -Filter *.png | Sort-Object Name

# CRITICAL: force the Russian engine. The default user-profile engine picks
# en-US and transliterates Cyrillic into Latin mojibake.
$ruLang = [Windows.Globalization.Language]::new('ru')
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($ruLang)
if ($engine -eq $null) { $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages() }

$sb = New-Object System.Text.StringBuilder
foreach ($f in $files) {
    $path = $f.FullName
    try {
        $file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($path)) ([Windows.Storage.StorageFile])
        $stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
        $decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
        $bitmap = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
        $result = Await ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
        [void]$sb.AppendLine("===== $($f.BaseName) =====")
        [void]$sb.AppendLine($result.Text)
        Write-Output ("OK: " + $f.Name)
    } catch {
        Write-Output ("ERR: " + $f.Name + " " + $_.Exception.Message)
    }
    $stream.Dispose()
}

# Always write to a UTF-8 file: console stdout mangles Cyrillic regardless of engine.
[System.IO.File]::WriteAllText($OutFile, $sb.ToString(), [System.Text.Encoding]::UTF8)
Write-Output "DONE -> $OutFile"
