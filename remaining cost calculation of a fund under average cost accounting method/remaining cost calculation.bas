Attribute VB_Name = "Module3"
Sub remaining_cost_calculation()
Dim i As Integer
Dim j As Integer
Dim z As Integer
Dim names As Variant
Dim dates() As Date
Dim rcs() As Double

'delete old table in the Output sheet
Workbooks("HR_Recruit_VBA_v1.xls").Worksheets("output").Activate
With Workbooks("HR_Recruit_VBA_v1.xls").Worksheets("output")
    .Range(.Cells(5, 2), .Cells(.Cells(5, 2).End(xlDown).Row, .Cells(5, 2).End(xlToRight).Column)).Delete shift:=xlShiftUp
End With

'obtain all the dates on which the remaining costs of shares need to be calculated.
'This is done by searching column B of Task_Data sheet. If the cell in column B starts with "Date" and ends with "=",
'then the next cell in the same row contains one of the dates required.
'All required dates are stored in an array called "dates"
Workbooks("HR_Recruit_VBA_v1.xls").Worksheets("Task_Data").Activate
With Workbooks("HR_Recruit_VBA_v1.xls").Worksheets("Task_Data")
    begin_row = .Cells(1, 2).End(xlDown).Row
    end_row = .Cells(begin_row, 2).End(xlDown).Row
    no_dates = 0
    For i = begin_row To end_row
        If .Cells(i, 2) Like "Date*=" Then
            ReDim Preserve dates(no_dates)
            dates(UBound(dates)) = .Cells(i, 3)
            no_dates = no_dates + 1
        End If
    Next i
    'Copy the names of shares
    .Range(.Cells(end_row + 3, 3), .Cells(end_row + 3, 3).End(xlDown)).Copy
End With

'Names of shares are pasted, duplicates are removed, and then the unique names are sorted in ascending order
Workbooks("HR_Recruit_VBA_v1.xls").Worksheets("output").Activate
With Workbooks("HR_Recruit_VBA_v1.xls").Worksheets("output")
    .Cells(6, 2).PasteSpecial
    .Range(Cells(6, 2), Cells(6, 2).End(xlDown)).RemoveDuplicates Columns:=Array(1)
    .Sort.SetRange .Range(Cells(6, 2), Cells(6, 2).End(xlDown))
    .Sort.Orientation = xlTopToBottom
    .Sort.Apply
    .Cells(5, 2) = "Name"
    For i = LBound(dates) To UBound(dates)
        .Cells(5, 3 + i) = dates(i)
    Next i
    'Unique names are stored in an array called "names"
    names = Application.Transpose(.Range(Cells(6, 2), Cells(6, 2).End(xlDown)))
End With

no_names = UBound(names)
no_rcs = no_names * no_dates
ReDim rcs(no_rcs)

Workbooks("HR_Recruit_VBA_v1.xls").Worksheets("Task_Data").Activate
With Workbooks("HR_Recruit_VBA_v1.xls").Worksheets("Task_Data")
    For i = LBound(names) To UBound(names)
    'Set the cutoff date as the first required date.
    'For each name, search column C of Task_Data sheet for cells with the same name.
    'For each cell with the same name, check the date in the same row.
    'If the date is later than the cutoff date, the remaining cost before factoring in the transaction denoted by the row need to be recorded.
    'Then set the cutoff date as the next required date.
    'Then calculate remaining cost of the name after transaction denoted by the row.
    'All remaining costs that need to be recorded are stored in an array called "rcs"
        Name = names(i)
        Hldgp = 0
        rcp = 0
        Hldg = 0
        rc = 0
        no_date = 0
        For j = 10 To .Cells(10, 2).End(xlDown).Row
            If .Cells(j, 3) = Name Then
                If .Cells(j, 2) > dates(no_date) Then
                    rcs((i - 1) * no_dates + no_date) = rc
                    no_date = no_date + 1
                End If
                Hldgp = Hldg
                rcp = rc
                shrs = .Cells(j, 4)
                Hldg = Hldgp + shrs
                Longsh = Application.WorksheetFunction.Min(IIf(Hldg < 0, 0, 1), IIf(Hldgp < 0, 0, 1))
                shrsSellcv = Longsh * Application.WorksheetFunction.Min(0, shrs) + (1 - Longsh) * Application.WorksheetFunction.Max(0, shrs)
                shrsbuysh = Longsh * Application.WorksheetFunction.Max(0, shrs) + (1 - Longsh) * Application.WorksheetFunction.Min(0, shrs)
                rc = (Hldgp + shrsSellcv) * rcp / IIf(Hldgp = 0, 1, Hldgp) + shrsbuysh * .Cells(j, 5)
            End If
        Next j
        'If the latest transaction date is earlier than one of the required dates,
        'remaining costs on all required dates later than the latest transaction date are equal to the remaining cost right after the latest transaction.
        If no_date <= no_dates - 1 Then
            For unfinished_date = no_date To no_dates - 1
                rcs((i - 1) * no_dates + unfinished_date) = rc
            Next unfinished_date
        End If
    Next i
End With

'Record remaining costs in Output sheet
Workbooks("HR_Recruit_VBA_v1.xls").Worksheets("output").Activate
With Workbooks("HR_Recruit_VBA_v1.xls").Worksheets("output")
    For i = 1 To no_names
        For j = 1 To no_dates
            no_rc = (i - 1) * no_dates + j
            .Cells(5 + i, 2 + j) = rcs(no_rc - 1)
            .Cells(5 + i, 2 + j).NumberFormat = "_(* #,##0.00_);_(* (#,##0.00);_(* ""-""??_);_(@_)"
        Next j
    Next i
End With
End Sub
