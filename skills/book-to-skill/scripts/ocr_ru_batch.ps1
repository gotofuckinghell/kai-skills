# Russian batch OCR via Windows.Media.Ocr. Usage:
#   powershell -ExecutionPolicy Bypass -File ocr_ru_batch.ps1 <in_dir_png> <out_file.txt>
# Render pages first with pymupdf: pix = doc[i].get_pixmap(dpi=200); pix.save(f'p{i+1:03d}.png')
# CRITICAL: force 'ru' language - default en-US engine transliterates Cyrillic to Latin.
# CRITICAL: write to UTF-8 file, never console (console mangles Unicode).
param(
    [string]$inDir,
    [string]$outFile
)

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

$files = Get-ChildItem -LiteralPath $inDir -Filter *.png | Sort-Object Name
$ruLang = [Windows.Globalization.Language]::new('ru')
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($ruLang)
if ($engine -eq $null) { $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages() }

$sb = New-Object System.Text.StringBuilder
foreach ($f in $files) {
    try {
        $file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($f.FullName)) ([Windows.Storage.StorageFile])
        $stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
        $decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
        $bitmap = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
        $result = Await ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
        [void]$sb.AppendLine("===== $($f.BaseName) =====")
        [void]$sb.AppendLine($result.Text)
        Write-Output ("OK: " + $f.Name)
        $stream.Dispose()
    } catch {
        Write-Output ("ERR: " + $f.Name + " " + $_.Exception.Message)
    }
}
[System.IO.File]::WriteAllText($outFile, $sb.ToString(), [System.Text.Encoding]::UTF8)
Write-Output "DONE -> $outFile"
