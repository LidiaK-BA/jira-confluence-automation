$ErrorActionPreference = "Stop"
[Console]::InputEncoding = New-Object System.Text.UTF8Encoding($false)
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)

function Send-JsonRpcResponse {
    param(
        [object]$Id,
        [hashtable]$Result,
        [hashtable]$ErrorObject
    )

    $response = @{
        jsonrpc = "2.0"
        id = $Id
    }
    if ($null -ne $ErrorObject) {
        $response.error = $ErrorObject
    }
    else {
        $response.result = $Result
    }

    [Console]::Out.WriteLine(($response | ConvertTo-Json -Compress -Depth 20))
}

while ($null -ne ($line = [Console]::In.ReadLine())) {
    if ([string]::IsNullOrWhiteSpace($line)) {
        continue
    }

    try {
        $request = ConvertFrom-Json -InputObject $line -ErrorAction Stop
    }
    catch {
        Send-JsonRpcResponse -Id $null -ErrorObject @{
            code = -32700
            message = "Parse error"
        }
        continue
    }

    if ($request -isnot [System.Management.Automation.PSCustomObject]) {
        Send-JsonRpcResponse -Id $null -ErrorObject @{
            code = -32600
            message = "Invalid Request"
        }
        continue
    }

    if ([string]::IsNullOrWhiteSpace($request.method)) {
        if ($request.PSObject.Properties.Name -contains "id") {
            Send-JsonRpcResponse -Id $request.id -ErrorObject @{
                code = -32600
                message = "Invalid Request"
            }
        }
        continue
    }

    if ($request.PSObject.Properties.Name -notcontains "id") {
        continue
    }

    switch ($request.method) {
        "initialize" {
            $protocolVersion = "2024-11-05"
            if ($request.params.protocolVersion) {
                $protocolVersion = [string]$request.params.protocolVersion
            }
            Send-JsonRpcResponse -Id $request.id -Result @{
                protocolVersion = $protocolVersion
                capabilities = @{
                    tools = @{}
                }
                serverInfo = @{
                    name = "time-windows"
                    version = "1.0.0"
                }
            }
        }
        "ping" {
            Send-JsonRpcResponse -Id $request.id -Result @{}
        }
        "tools/list" {
            Send-JsonRpcResponse -Id $request.id -Result @{
                tools = @(
                    @{
                        name = "get_time"
                        description = "Return the current timestamp in ISO 8601 UTC format."
                        inputSchema = @{
                            type = "object"
                            properties = @{}
                            additionalProperties = $false
                        }
                    }
                )
            }
        }
        "tools/call" {
            if ($request.params.name -ne "get_time") {
                Send-JsonRpcResponse -Id $request.id -ErrorObject @{
                    code = -32602
                    message = "Unknown tool: $($request.params.name)"
                }
                continue
            }

            Send-JsonRpcResponse -Id $request.id -Result @{
                content = @(
                    @{
                        type = "text"
                        text = [DateTimeOffset]::UtcNow.ToString("o")
                    }
                )
                isError = $false
            }
        }
        default {
            Send-JsonRpcResponse -Id $request.id -ErrorObject @{
                code = -32601
                message = "Method not found: $($request.method)"
            }
        }
    }
}
