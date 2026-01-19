#!/usr/bin/env pwsh

Write-Output "Treinando modelo..."
docker-compose run --rm train

Write-Output "Iniciando a API..."
docker-compose up -d api

Write-Output "Verificando API..."
do {
    Write-Output "Aguardando API..."
    Start-Sleep -Seconds 2
} until (Test-NetConnection -ComputerName localhost -Port 5000 -InformationLevel Quiet)

Write-Output "Iniciando Streamlit..."
docker-compose up -d streamlit

