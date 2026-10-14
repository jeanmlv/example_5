# example_5

Get-ChildItem $env:TEMP -File -Recurse -ErrorAction SilentlyContinue |
Sort-Object Length -Descending |
Select-Object -First 20 Name, @{Name="SizeGB";Expression={[math]::Round($_.Length/1GB,2)}}, FullName

Get-ChildItem $env:TEMP -File -Recurse -ErrorAction SilentlyContinue |
Measure-Object Length -Sum |
Select-Object Count, @{Name="TotalGB";Expression={[math]::Round($_.Sum/1GB,2)}}
