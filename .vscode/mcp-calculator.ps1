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
                    name = "calculator-windows"
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
                        name = "calculate"
                        description = "Perform addition, subtraction, multiplication, or division on two numbers."
                        inputSchema = @{
                            type = "object"
                            properties = @{
                                operation = @{
                                    type = "string"
                                    enum = @("add", "subtract", "multiply", "divide")
                                }
                                a = @{
                                    type = "number"
                                }
                                b = @{
                                    type = "number"
                                }
                            }
                            required = @("operation", "a", "b")
                            additionalProperties = $false
                        }
                    }
                )
            }
        }
        "tools/call" {
            if ($request.params.name -ne "calculate") {
                Send-JsonRpcResponse -Id $request.id -ErrorObject @{
                    code = -32602
                    message = "Unknown tool: $($request.params.name)"
                }
                continue
            }

            $arguments = $request.params.arguments
            $numericTypes = @(
                [byte], [sbyte], [int16], [uint16], [int32], [uint32],
                [int64], [uint64], [single], [double], [decimal]
            )
            if ($null -eq $arguments -or
                $arguments.a -is [bool] -or
                $arguments.b -is [bool] -or
                $arguments.a.GetType() -notin $numericTypes -or
                $arguments.b.GetType() -notin $numericTypes) {
                Send-JsonRpcResponse -Id $request.id -ErrorObject @{
                    code = -32602
                    message = "Tool 'calculate' requires numeric 'a' and 'b' arguments."
                }
                continue
            }

            $a = [double]$arguments.a
            $b = [double]$arguments.b
            $operationError = $null
            switch ($arguments.operation) {
                "add" { $value = $a + $b }
                "subtract" { $value = $a - $b }
                "multiply" { $value = $a * $b }
                "divide" {
                    if ($b -eq 0) {
                        $operationError = "Division by zero is not allowed."
                        break
                    }
                    $value = $a / $b
                }
                default {
                    $operationError = "Operation must be add, subtract, multiply, or divide."
                }
            }

            if ($null -ne $operationError) {
                Send-JsonRpcResponse -Id $request.id -ErrorObject @{
                    code = -32602
                    message = $operationError
                }
                continue
            }

            if ([double]::IsInfinity($value) -or [double]::IsNaN($value)) {
                Send-JsonRpcResponse -Id $request.id -ErrorObject @{
                    code = -32602
                    message = "The calculation result is outside the supported numeric range."
                }
                continue
            }

            Send-JsonRpcResponse -Id $request.id -Result @{
                content = @(
                    @{
                        type = "text"
                        text = $value.ToString("R", [Globalization.CultureInfo]::InvariantCulture)
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
