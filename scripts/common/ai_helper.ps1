# AI助手 PowerShell 脚本（本地ollama模型推理版）
param([string]$Code, [string]$Desc, [string]$Test)

# 检查ollama是否安装
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host "未检测到ollama，请安装：https://ollama.com" -ForegroundColor Red
    exit 1
}

# 读取默认模型
$modelFile = "$PSScriptRoot/../../AIserver/model/default-model.txt"
if (-not (Test-Path $modelFile)) {
    Write-Host "未找到默认模型配置文件 $modelFile" -ForegroundColor Red
    exit 1
}
$modelName = Get-Content $modelFile -Raw
$modelName = $modelName.Trim()

# 读取题目描述、代码、测试用例
$descText = Get-Content $Desc -Raw
$codeText = Get-Content $Code -Raw
$testText = Get-Content $Test -Raw


# 更鲁棒的 AI 提示词，确保输出完整、可编译、无多余内容的 C 代码
$promptLines = @(
    '你是一个严谨的 C 语言学习助手。请严格遵循以下要求：',
    '1. 只基于下方题目描述、已有代码和测试用例，生成本题的完整、可直接编译的 C 语言代码。',
    '2. 只输出一段代码，必须用 <<CODE>> 开头、<<END>> 结尾包裹，中间只允许 C 代码本身。',
    '3. 代码必须包含 #include 和 int main，且 main 函数必须有 return 0; 和结尾右大括号 }。',
    '4. 不要输出任何解释、标题、JSON、特殊 token、代码块标记、[DONE]、或其它无关内容。',
    '5. 如果无法确定答案，请只输出空标记对：<<CODE>><<END>>。',
    '',
    '【题目描述】',
    $descText,
    '',
    '【已有代码】',
    $codeText,
    '',
    '【测试用例】',
    $testText,
    '',
    '请严格只输出如下格式：',
    '<<CODE>>',
    '（此处是你的完整C代码）',
    '<<END>>'
)
$prompt = $promptLines -join "`n"

Write-Host "正在调用本地AI模型 ($modelName)，请稍候..." -ForegroundColor Cyan
# 调用ollama（通过管道传递prompt）
$result = $prompt | ollama run $modelName

# 清洗：移除代码围栏/流式标记
$resultClean = $result -replace '```c\+\+', '' -replace '```c', '' -replace '```C', '' -replace '```', ''
$resultClean = ($resultClean -split "\r?\n" | Where-Object { $_ -notmatch '^\s*\[DONE\]\s*$' }) -join "`n"


# 优先：提取首个 <<CODE>>...<<END>> 代码块，去除所有标记和特殊 token
$codeOut = ""
$matches = [regex]::Matches($resultClean, '(?s)<<CODE>>(.*?)<<END>>')
if ($matches.Count -gt 0) {
    $codeOut = $matches[0].Groups[1].Value
} else {
    # 回退：从第一行 #include 或 int main 开始提取到末尾
    $lines = $resultClean -split "\r?\n"
    $match = Select-String -InputObject $lines -Pattern '^\s*#include|^\s*int\s+main\s*\(' | Select-Object -First 1
    if ($match) {
        $start0 = [int]$match.LineNumber - 1
        if ($start0 -lt 0) { $start0 = 0 }
        $end0 = [int]$lines.Length - 1
        if ($end0 -lt $start0) { $end0 = $start0 }
        $codeOut = ($lines[$start0..$end0] -join "`n")
    } else {
        $codeOut = $resultClean
    }
}
# 清理所有 <<CODE>>/<<END>> 标记和特殊 token
$codeOut = $codeOut -replace '(?i)<<\s*CODE\s*>>', '' -replace '(?i)<<\s*END\s*>>', ''
$codeOut = $codeOut -replace '<[｜|\|]begin[▁_ ]of[▁_ ]sentence[｜|\|]>', ''
$codeOut = $codeOut -replace '<s>', '' -replace '</s>', ''
$codeOut = $codeOut.Trim()

# 不再添加历史的 //I'm Ok 标记，直接输出模型给出的完整代码

# 展示：只输出【完整代码】
Write-Host ""  # 空行
Write-Host "================ AI模型反馈 ================" -ForegroundColor Magenta
Write-Host "【完整代码】" -ForegroundColor Cyan
Write-Host $codeOut -ForegroundColor White
Write-Host "============================================" -ForegroundColor Magenta
Write-Host ""  # 空行
$null = Read-Host -Prompt '按 Enter 键继续...'
