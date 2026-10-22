# Builds clocklib.pyd (the native library) with MinGW gcc from MSYS2.
$ErrorActionPreference = "Stop"
$bin = "C:\msys64\ucrt64\bin"
$python = (Get-Command python).Source
$env:PATH = "$bin;" + $env:PATH
$prefix = & $python -c "import sys; print(sys.base_prefix)"
$version = & $python -c "import sys; print(str(sys.version_info.major) + str(sys.version_info.minor))"

& "$bin\gcc.exe" -shared -O2 -Wall -static-libgcc `
    -o clocklib.pyd native/clocklib.c `
    "-I$prefix\include" "$prefix\python$version.dll" `
    -lgdi32 -luser32
if ($LASTEXITCODE -ne 0) { throw "Build failed" }
Write-Host "Built clocklib.pyd"
