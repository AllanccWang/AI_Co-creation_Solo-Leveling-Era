#Requires AutoHotkey v2.0

!a:: { ; Alt + A as the trigger hotkey
    ; Wait for clipboard to have content (up to 2 seconds)
    if !ClipWait(2) {
        MsgBox("⚠️ Clipboard not updated. Please check if Copyfish successfully captured the text.")
        return
    }

    text := A_Clipboard
    if (StrLen(text) = 0) {
        MsgBox("📭 Clipboard is empty. Please use Copyfish to capture text first.")
        return
    }

    ; Simulate Alt+Q (to trigger Edge Translate or other extension)
    Send("!q")
    Sleep(500) ; Wait for the extension to load

    ; Paste and submit
    Send(text)
    Send("{Enter}")
}
