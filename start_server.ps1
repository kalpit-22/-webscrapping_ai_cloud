# start_server.ps1
Write-Host "Starting llama-server with 14B model and 24K context..." -ForegroundColor Cyan

# Navigate to the llama.cpp directory
Set-Location -Path "D:\llama.cpp"

# Launch the server
.\llama-server.exe `
    -m D:\LLM_hf\Qwen3-14B-Q4_K_M.gguf `
    -ngl 99 `
    -c 24576 `
    -fa on `
    -ctk q8_0 `
    -ctv q8_0 `
    --host 0.0.0.0 `
    --port 8081