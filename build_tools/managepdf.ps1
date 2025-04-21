# Add required assemblies for Windows Forms
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Global zoom factor for PictureBox preview and global variable to store latest PDF file path
$global:zoomFactor = 1.0
$global:latestPDF = $null

# Create the form
$form = New-Object System.Windows.Forms.Form
$form.Text = "Image to PDF Converter"
$form.Size = New-Object System.Drawing.Size(950, 700)
$form.StartPosition = "CenterScreen"
$form.BackColor = [System.Drawing.Color]::White
$form.AllowDrop = $true

# Drag-and-drop overlay label (hidden by default)
$dragOverlay = New-Object System.Windows.Forms.Label
$dragOverlay.Text = "Drop files here"
$dragOverlay.Font = New-Object System.Drawing.Font("Arial",16,[System.Drawing.FontStyle]::Bold)
$dragOverlay.ForeColor = [System.Drawing.Color]::White
$dragOverlay.BackColor = [System.Drawing.Color]::FromArgb(128,0,0,0)
$dragOverlay.AutoSize = $false
$dragOverlay.TextAlign = 'MiddleCenter'
$dragOverlay.Size = New-Object System.Drawing.Size(400, 100)
$dragOverlay.Location = New-Object System.Drawing.Point(([int](($form.ClientSize.Width - $dragOverlay.Width) / 2)), ([int](($form.ClientSize.Height - $dragOverlay.Height) / 2)))
$dragOverlay.Visible = $false
$form.Controls.Add($dragOverlay)

# Label for instructions
$label = New-Object System.Windows.Forms.Label
$label.Text = "Convert Images (JPG, PNG) to PDF"
$label.Font = New-Object System.Drawing.Font("Arial", 14, [System.Drawing.FontStyle]::Bold)
$label.Size = New-Object System.Drawing.Size(900, 30)
$label.Location = New-Object System.Drawing.Point(25, 10)
$label.TextAlign = "MiddleCenter"
$form.Controls.Add($label)

# Button to select images
$btnSelect = New-Object System.Windows.Forms.Button
$btnSelect.Text = "Select Images"
$btnSelect.Size = New-Object System.Drawing.Size(180, 40)
$btnSelect.Location = New-Object System.Drawing.Point(25, 50)
$btnSelect.Font = New-Object System.Drawing.Font("Arial", 10, [System.Drawing.FontStyle]::Bold)
$form.Controls.Add($btnSelect)

# Checkbox for separate PDFs
$chkSeparate = New-Object System.Windows.Forms.CheckBox
$chkSeparate.Text = "Save each image as a separate PDF"
$chkSeparate.Font = New-Object System.Drawing.Font("Arial", 10)
$chkSeparate.Location = New-Object System.Drawing.Point(25, 100)
$chkSeparate.Size = New-Object System.Drawing.Size(300, 25)
$form.Controls.Add($chkSeparate)

# PDF Margin (Border) option
$lblMargin = New-Object System.Windows.Forms.Label
$lblMargin.Text = "Margin (px):"
$lblMargin.Font = New-Object System.Drawing.Font("Arial", 10)
$lblMargin.Location = New-Object System.Drawing.Point(350, 100)
$lblMargin.Size = New-Object System.Drawing.Size(80, 25)
$form.Controls.Add($lblMargin)

$numMargin = New-Object System.Windows.Forms.NumericUpDown
$numMargin.Minimum = 0
$numMargin.Maximum = 100
$numMargin.Value = 10
$numMargin.Font = New-Object System.Drawing.Font("Arial", 10)
$numMargin.Location = New-Object System.Drawing.Point(430, 100)
$numMargin.Size = New-Object System.Drawing.Size(60, 25)
$form.Controls.Add($numMargin)

# PDF Orientation option
$lblOrient = New-Object System.Windows.Forms.Label
$lblOrient.Text = "Orientation:"
$lblOrient.Font = New-Object System.Drawing.Font("Arial", 10)
$lblOrient.Location = New-Object System.Drawing.Point(510, 100)
$lblOrient.Size = New-Object System.Drawing.Size(80, 25)
$form.Controls.Add($lblOrient)

$comboOrient = New-Object System.Windows.Forms.ComboBox
$comboOrient.Font = New-Object System.Drawing.Font("Arial", 10)
$comboOrient.Items.AddRange(@("Portrait","Landscape"))
$comboOrient.SelectedIndex = 0
$comboOrient.Location = New-Object System.Drawing.Point(590, 100)
$comboOrient.Size = New-Object System.Drawing.Size(120, 25)
$form.Controls.Add($comboOrient)

# Button to convert to PDF
$btnConvert = New-Object System.Windows.Forms.Button
$btnConvert.Text = "Convert to PDF"
$btnConvert.Size = New-Object System.Drawing.Size(180, 40)
$btnConvert.Location = New-Object System.Drawing.Point(25, 135)
$btnConvert.Font = New-Object System.Drawing.Font("Arial", 10, [System.Drawing.FontStyle]::Bold)
$form.Controls.Add($btnConvert)

# Button to reset inputs
$btnReset = New-Object System.Windows.Forms.Button
$btnReset.Text = "Reset"
$btnReset.Size = New-Object System.Drawing.Size(180, 40)
$btnReset.Location = New-Object System.Drawing.Point(215, 135)
$btnReset.Font = New-Object System.Drawing.Font("Arial", 10, [System.Drawing.FontStyle]::Bold)
$form.Controls.Add($btnReset)

# PictureBox for preview
$pictureBox = New-Object System.Windows.Forms.PictureBox
$pictureBox.Size = New-Object System.Drawing.Size(550, 350)
$pictureBox.Location = New-Object System.Drawing.Point(25, 190)
$pictureBox.SizeMode = "Zoom"
$pictureBox.BorderStyle = "FixedSingle"
$form.Controls.Add($pictureBox)

# Rotate button (for current preview)
$btnRotate = New-Object System.Windows.Forms.Button
$btnRotate.Text = "Rotate Image"
$btnRotate.Size = New-Object System.Drawing.Size(150, 30)
$btnRotate.Location = New-Object System.Drawing.Point(590, 190)
$btnRotate.Font = New-Object System.Drawing.Font("Arial", 10, [System.Drawing.FontStyle]::Bold)
$form.Controls.Add($btnRotate)

# Navigation buttons for preview
$btnPrev = New-Object System.Windows.Forms.Button
$btnPrev.Text = "Previous"
$btnPrev.Size = New-Object System.Drawing.Size(150, 30)
$btnPrev.Location = New-Object System.Drawing.Point(25, 550)
$btnPrev.Font = New-Object System.Drawing.Font("Arial", 10, [System.Drawing.FontStyle]::Bold)
$form.Controls.Add($btnPrev)

$btnNext = New-Object System.Windows.Forms.Button
$btnNext.Text = "Next"
$btnNext.Size = New-Object System.Drawing.Size(150, 30)
$btnNext.Location = New-Object System.Drawing.Point(225, 550)
$btnNext.Font = New-Object System.Drawing.Font("Arial", 10, [System.Drawing.FontStyle]::Bold)
$form.Controls.Add($btnNext)

# ListBox for image order
$listBox = New-Object System.Windows.Forms.ListBox
$listBox.Location = New-Object System.Drawing.Point(590, 240)
$listBox.Size = New-Object System.Drawing.Size(280, 200)
$form.Controls.Add($listBox)

# Delete button for removing selected image
$btnDelete = New-Object System.Windows.Forms.Button
$btnDelete.Text = "Delete Image"
$btnDelete.Size = New-Object System.Drawing.Size(150, 30)
$btnDelete.Location = New-Object System.Drawing.Point(590, 450)
$btnDelete.Font = New-Object System.Drawing.Font("Arial", 10, [System.Drawing.FontStyle]::Bold)
$form.Controls.Add($btnDelete)

# Up and Down buttons for reordering
$btnUp = New-Object System.Windows.Forms.Button
$btnUp.Text = "Up"
$btnUp.Size = New-Object System.Drawing.Size(120, 30)
$btnUp.Location = New-Object System.Drawing.Point(750, 450)
$btnUp.Font = New-Object System.Drawing.Font("Arial", 10, [System.Drawing.FontStyle]::Bold)
$form.Controls.Add($btnUp)

$btnDown = New-Object System.Windows.Forms.Button
$btnDown.Text = "Down"
$btnDown.Size = New-Object System.Drawing.Size(120, 30)
$btnDown.Location = New-Object System.Drawing.Point(590, 490)
$btnDown.Font = New-Object System.Drawing.Font("Arial", 10, [System.Drawing.FontStyle]::Bold)
$form.Controls.Add($btnDown)

# Label for status
$statusLabel = New-Object System.Windows.Forms.Label
$statusLabel.Text = ""
$statusLabel.Font = New-Object System.Drawing.Font("Arial", 10, [System.Drawing.FontStyle]::Bold)
$statusLabel.Size = New-Object System.Drawing.Size(900, 30)
$statusLabel.Location = New-Object System.Drawing.Point(25, 600)
$statusLabel.ForeColor = [System.Drawing.Color]::DarkBlue
$form.Controls.Add($statusLabel)

# Progress bar
$progressBar = New-Object System.Windows.Forms.ProgressBar
$progressBar.Size = New-Object System.Drawing.Size(900, 20)
$progressBar.Location = New-Object System.Drawing.Point(25, 640)
$form.Controls.Add($progressBar)

# New Buttons: Preview PDF and Print PDF (hidden by default)
$btnPreviewPDF = New-Object System.Windows.Forms.Button
$btnPreviewPDF.Text = "Preview PDF"
$btnPreviewPDF.Size = New-Object System.Drawing.Size(150, 40)
$btnPreviewPDF.Location = New-Object System.Drawing.Point(25, 680)
$btnPreviewPDF.Font = New-Object System.Drawing.Font("Arial", 10, [System.Drawing.FontStyle]::Bold)
$btnPreviewPDF.Visible = $false
$form.Controls.Add($btnPreviewPDF)

$btnPrintPDF = New-Object System.Windows.Forms.Button
$btnPrintPDF.Text = "Print PDF"
$btnPrintPDF.Size = New-Object System.Drawing.Size(150, 40)
$btnPrintPDF.Location = New-Object System.Drawing.Point(200, 680)
$btnPrintPDF.Font = New-Object System.Drawing.Font("Arial", 10, [System.Drawing.FontStyle]::Bold)
$btnPrintPDF.Visible = $false
$form.Controls.Add($btnPrintPDF)

# Global variables to store selected files, rotations, and current index
$global:selectedFiles = @()
$global:rotations = @{}  # Key: index, Value: rotation angle (0,90,180,270)
$global:currentIndex = 0

# Function to log errors to a file
function Log-Error($message) {
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    "$timestamp : $message" | Out-File -Append -FilePath "error.log"
}

# Function to update the PictureBox and ListBox selection
function Update-PictureBox {
    try {
        if ($global:selectedFiles.Count -gt 0 -and $global:currentIndex -ge 0 -and $global:currentIndex -lt $global:selectedFiles.Count) {
            $img = [System.Drawing.Image]::FromFile($global:selectedFiles[$global:currentIndex])
            # Apply rotation if stored
            if ($global:rotations.ContainsKey($global:currentIndex)) {
                $angle = $global:rotations[$global:currentIndex]
                switch ($angle) {
                    90 { $img.RotateFlip([System.Drawing.RotateFlipType]::Rotate90FlipNone) }
                    180 { $img.RotateFlip([System.Drawing.RotateFlipType]::Rotate180FlipNone) }
                    270 { $img.RotateFlip([System.Drawing.RotateFlipType]::Rotate270FlipNone) }
                }
            }
            # Apply zoom factor
            $newWidth = $img.Width * $global:zoomFactor
            $newHeight = $img.Height * $global:zoomFactor
            $bmp = New-Object System.Drawing.Bitmap($img, [int]$newWidth, [int]$newHeight)
            $pictureBox.Image = $bmp

            $statusLabel.Text = "Image $($global:currentIndex + 1) of $($global:selectedFiles.Count)"
            if ($listBox.Items.Count -gt 0) {
                $listBox.SelectedIndex = $global:currentIndex
            }
        } else {
            $pictureBox.Image = $null
            $statusLabel.Text = "No images selected!"
        }
    }
    catch {
        Log-Error "Error in Update-PictureBox: $($_.Exception.Message)"
        $statusLabel.Text = "Error loading image."
    }
}

# Function to reset inputs
function Reset-Inputs {
    $global:selectedFiles = @()
    $global:rotations = @{}
    $global:currentIndex = 0
    $listBox.Items.Clear()
    Update-PictureBox
    $progressBar.Value = 0
    $statusLabel.Text = ""
    $global:zoomFactor = 1.0
    $global:latestPDF = $null
    $btnPreviewPDF.Visible = $false
    $btnPrintPDF.Visible = $false
}

# Event: Reset button click
$btnReset.Add_Click({ Reset-Inputs })

# Event: Select images (append new images)
$btnSelect.Add_Click({
    $fileDialog = New-Object System.Windows.Forms.OpenFileDialog
    $fileDialog.Multiselect = $true
    $fileDialog.Filter = "Image Files (*.jpg; *.jpeg; *.png)|*.jpg;*.jpeg;*.png"
    if ($fileDialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
        foreach ($file in $fileDialog.FileNames) {
            if (-not ($global:selectedFiles -contains $file)) {
                $global:selectedFiles += $file
                $listBox.Items.Add([System.IO.Path]::GetFileName($file))
            }
        }
        if ($global:currentIndex -lt 0 -or $global:currentIndex -ge $global:selectedFiles.Count) {
            $global:currentIndex = 0
        }
        Update-PictureBox
    }
})

# Drag-and-Drop Support with overlay
$form.Add_DragEnter({
    param($sender, $e)
    if ($e.Data.GetDataPresent([System.Windows.Forms.DataFormats]::FileDrop)) {
        $e.Effect = [System.Windows.Forms.DragDropEffects]::Copy
        $dragOverlay.Visible = $true
        $dragOverlay.BringToFront()
    }
})
$form.Add_DragLeave({ $dragOverlay.Visible = $false })
$form.Add_DragDrop({
    param($sender, $e)
    $dragOverlay.Visible = $false
    $files = $e.Data.GetData([System.Windows.Forms.DataFormats]::FileDrop, $true)
    $imageFiles = $files | Where-Object { $_ -match '\.(jpg|jpeg|png)$' }
    if ($imageFiles.Count -gt 0) {
        foreach ($file in $imageFiles) {
            if (-not ($global:selectedFiles -contains $file)) {
                $global:selectedFiles += $file
                $listBox.Items.Add([System.IO.Path]::GetFileName($file))
            }
        }
        if ($global:currentIndex -lt 0 -or $global:currentIndex -ge $global:selectedFiles.Count) {
            $global:currentIndex = 0
        }
        Update-PictureBox
    }
})

# Event: Rotate button click
$btnRotate.Add_Click({
    if ($global:selectedFiles.Count -eq 0) {
        $statusLabel.Text = "No image to rotate!"
        return
    }
    if ($global:rotations.ContainsKey($global:currentIndex)) {
        $global:rotations[$global:currentIndex] = ($global:rotations[$global:currentIndex] + 90) % 360
    } else {
        $global:rotations[$global:currentIndex] = 90
    }
    Update-PictureBox
})

# Event: ListBox selection change
$listBox.Add_SelectedIndexChanged({
    if ($listBox.SelectedIndex -ge 0) {
        $global:currentIndex = $listBox.SelectedIndex
        Update-PictureBox
    }
})

# Event: Up button click for reordering
$btnUp.Add_Click({
    $idx = $listBox.SelectedIndex
    if ($idx -gt 0) {
        $temp = $listBox.Items[$idx]
        $listBox.Items[$idx] = $listBox.Items[$idx - 1]
        $listBox.Items[$idx - 1] = $temp
        $tempFile = $global:selectedFiles[$idx]
        $global:selectedFiles[$idx] = $global:selectedFiles[$idx - 1]
        $global:selectedFiles[$idx - 1] = $tempFile
        $tempRot = $global:rotations[$idx]
        $global:rotations[$idx] = $global:rotations[$idx - 1]
        $global:rotations[$idx - 1] = $tempRot
        $global:currentIndex = $idx - 1
        Update-PictureBox
    }
})

# Event: Down button click for reordering
$btnDown.Add_Click({
    $idx = $listBox.SelectedIndex
    if ($idx -lt ($listBox.Items.Count - 1) -and $idx -ge 0) {
        $temp = $listBox.Items[$idx]
        $listBox.Items[$idx] = $listBox.Items[$idx + 1]
        $listBox.Items[$idx + 1] = $temp
        $tempFile = $global:selectedFiles[$idx]
        $global:selectedFiles[$idx] = $global:selectedFiles[$idx + 1]
        $global:selectedFiles[$idx + 1] = $tempFile
        $tempRot = $global:rotations[$idx]
        $global:rotations[$idx] = $global:rotations[$idx + 1]
        $global:rotations[$idx + 1] = $tempRot
        $global:currentIndex = $idx + 1
        Update-PictureBox
    }
})

# Event: Delete image button click
$btnDelete.Add_Click({
    $idx = $listBox.SelectedIndex
    if ($idx -ge 0 -and $idx -lt $listBox.Items.Count) {
        try {
            if ($global:selectedFiles.Count -gt 1) {
                if ($idx -eq 0) {
                    $global:selectedFiles = $global:selectedFiles[1..($global:selectedFiles.Count - 1)]
                } elseif ($idx -eq $global:selectedFiles.Count - 1) {
                    $global:selectedFiles = $global:selectedFiles[0..($global:selectedFiles.Count - 2)]
                } else {
                    $global:selectedFiles = $global:selectedFiles[0..($idx - 1)] + $global:selectedFiles[($idx + 1)..($global:selectedFiles.Count - 1)]
                }
            }
            else {
                $global:selectedFiles = @()
            }
            $global:rotations.Remove($idx)
            $newRotations = @{}
            foreach ($key in $global:rotations.Keys) {
                if ($key -gt $idx) {
                    $newRotations[$key - 1] = $global:rotations[$key]
                }
                elseif ($key -lt $idx) {
                    $newRotations[$key] = $global:rotations[$key]
                }
            }
            $global:rotations = $newRotations
            $listBox.Items.RemoveAt($idx)
            if ($listBox.Items.Count -eq 0) {
                $global:currentIndex = -1
            }
            elseif ($idx -ge $listBox.Items.Count) {
                $global:currentIndex = $listBox.Items.Count - 1
            }
            else {
                $global:currentIndex = $idx
            }
            Update-PictureBox
        }
        catch {
            Log-Error "Error in Delete: $($_.Exception.Message)"
            [System.Windows.Forms.MessageBox]::Show("Error deleting image. See error.log for details.","Error",[System.Windows.Forms.MessageBoxButtons]::OK,[System.Windows.Forms.MessageBoxIcon]::Error)
        }
    }
})

# Navigation: Previous and Next buttons
$btnPrev.Add_Click({
    if ($global:currentIndex -gt 0) {
        $global:currentIndex--
        Update-PictureBox
    }
})
$btnNext.Add_Click({
    if ($global:currentIndex -lt ($global:selectedFiles.Count - 1)) {
        $global:currentIndex++
        Update-PictureBox
    }
})

# Zoom using mouse wheel on PictureBox
$pictureBox.Add_MouseWheel({
    param($sender, $e)
    if ($e.Delta -gt 0) {
        $global:zoomFactor += 0.1
    }
    else {
        $global:zoomFactor = [Math]::Max(0.1, $global:zoomFactor - 0.1)
    }
    Update-PictureBox
})

# Event: Convert to PDF
$btnConvert.Add_Click({
    if ($global:selectedFiles.Count -eq 0) {
        $statusLabel.Text = "No images selected!"
        return
    }
    
    $margin = $numMargin.Value
    $orientation = $comboOrient.SelectedItem
    $applyGlobalOrientation = ($orientation -eq "Landscape")
    
    try {
        if ($chkSeparate.Checked) {
            $folderDialog = New-Object System.Windows.Forms.FolderBrowserDialog
            if ($folderDialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
                $progressBar.Value = 0
                $total = $global:selectedFiles.Count
                $count = 0
                for ($i = 0; $i -lt $global:selectedFiles.Count; $i++) {
                    $imgFile = $global:selectedFiles[$i]
                    $outFile = [System.IO.Path]::Combine($folderDialog.SelectedPath, ([System.IO.Path]::GetFileNameWithoutExtension($imgFile) + ".pdf"))
                    $rotateOption = ""
                    if ($global:rotations.ContainsKey($i)) {
                        $rotateOption = "-rotate " + $global:rotations[$i]
                    }
                    $borderOption = ""
                    if ($margin -gt 0) {
                        $borderOption = "-border " + $margin + " -bordercolor white"
                    }
                    $orientOption = ""
                    if ($applyGlobalOrientation) {
                        $orientOption = "-rotate 90"
                    }
                    $cmd = "magick `"$imgFile`" $rotateOption $borderOption $orientOption `"$outFile`""
                    Invoke-Expression $cmd
                    $count++
                    $progressBar.Value = ([math]::Round(($count / $total) * 100))
                }
                $statusLabel.Text = "All images saved as separate PDFs."
                [System.Windows.Forms.MessageBox]::Show("PDF conversion complete.","Info",[System.Windows.Forms.MessageBoxButtons]::OK,[System.Windows.Forms.MessageBoxIcon]::Information)
            }
        }
        else {
            $saveDialog = New-Object System.Windows.Forms.SaveFileDialog
            $saveDialog.Filter = "PDF Files (*.pdf)|*.pdf"
            $saveDialog.DefaultExt = "pdf"
            if ($saveDialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
                $outputPDF = $saveDialog.FileName
                $progressBar.Value = 0
                $borderOption = ""
                if ($margin -gt 0) {
                    $borderOption = "-border " + $margin + " -bordercolor white"
                }
                $orientOption = ""
                if ($applyGlobalOrientation) {
                    $orientOption = "-rotate 90"
                }
                $filesString = ($global:selectedFiles | ForEach-Object { "`"$_`" $borderOption $orientOption" }) -join " "
                $cmd = "magick $filesString `"$outputPDF`""
                Invoke-Expression $cmd
                $progressBar.Value = 100
                $statusLabel.Text = "PDF created: $outputPDF"
                [System.Windows.Forms.MessageBox]::Show("PDF conversion complete.","Info",[System.Windows.Forms.MessageBoxButtons]::OK,[System.Windows.Forms.MessageBoxIcon]::Information)
                # Store the latest PDF file path and show preview/print buttons
                $global:latestPDF = $outputPDF
                $btnPreviewPDF.Visible = $true
                $btnPrintPDF.Visible = $true
            }
        }
    }
    catch {
        Log-Error "Error in Conversion: $($_.Exception.Message)"
        [System.Windows.Forms.MessageBox]::Show("Error during PDF conversion. See error.log for details.","Error",[System.Windows.Forms.MessageBoxButtons]::OK,[System.Windows.Forms.MessageBoxIcon]::Error)
    }
    
    Start-Sleep -Seconds 1
    # Uncomment below if you want to auto-reset after conversion
    #Reset-Inputs
})

# Event: Preview PDF button click - open PDF with default viewer
$btnPreviewPDF.Add_Click({
    if ($global:latestPDF -and (Test-Path $global:latestPDF)) {
        Start-Process $global:latestPDF
    }
    else {
        [System.Windows.Forms.MessageBox]::Show("No PDF available to preview.","Warning",[System.Windows.Forms.MessageBoxButtons]::OK,[System.Windows.Forms.MessageBoxIcon]::Warning)
    }
})

# Event: Print PDF button click - use default print verb
$btnPrintPDF.Add_Click({
    if ($global:latestPDF -and (Test-Path $global:latestPDF)) {
        Start-Process -FilePath $global:latestPDF -Verb Print
    }
    else {
        [System.Windows.Forms.MessageBox]::Show("No PDF available to print.","Warning",[System.Windows.Forms.MessageBoxButtons]::OK,[System.Windows.Forms.MessageBoxIcon]::Warning)
    }
})

# Show the form
[void]$form.ShowDialog()
