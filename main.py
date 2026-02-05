from graph.orchestrator import app

vb_code = """
Public Class Form1

    Private Sub Form1_Load(sender As Object, e As EventArgs) Handles MyBase.Load
        cmbLoanType.Items.Add("Conventional")
        cmbLoanType.Items.Add("FHA")
        cmbLoanType.Items.Add("VA")
        cmbLoanType.SelectedIndex = 0
    End Sub

    Private Sub btnFundLoan_Click(sender As Object, e As EventArgs) Handles btnFundLoan.Click
        Try
            Dim loanAmount As Double = Convert.ToDouble(txtLoanAmount.Text)
            Dim creditScore As Integer = Convert.ToInt32(txtCreditScore.Text)
            Dim loanType As String = cmbLoanType.Text

            If Not IsEligibleForFunding(loanAmount, creditScore, loanType) Then
                lblResult.Text = "Loan is NOT eligible for funding"
                Exit Sub
            End If

            Dim fundedAmount As Double = CalculateFundedAmount(loanAmount, loanType)

            lblResult.Text = "Loan FUNDED: $" & fundedAmount.ToString("0.00")

            LogFunding(loanAmount, fundedAmount, loanType, creditScore)

        Catch ex As Exception
            MessageBox.Show("Invalid input values", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error)
        End Try
    End Sub

    ' Business rules embedded in UI code (classic legacy)
    Private Function IsEligibleForFunding(amount As Double, creditScore As Integer, loanType As String) As Boolean

        If loanType = "Conventional" Then
            If creditScore < 620 Then
                Return False
            End If
        ElseIf loanType = "FHA" Then
            If creditScore < 580 Then
                Return False
            End If
        ElseIf loanType = "VA" Then
            If creditScore < 600 Then
                Return False
            End If
        End If

        If amount > 1000000 Then
            Return False
        End If

        Return True
    End Function

    Private Function CalculateFundedAmount(amount As Double, loanType As String) As Double
        Dim fundedAmount As Double = amount

        ' Funding adjustments based on loan type
        If loanType = "FHA" Then
            fundedAmount = amount * 0.97
        ElseIf loanType = "VA" Then
            fundedAmount = amount * 1.0
        ElseIf loanType = "Conventional" Then
            fundedAmount = amount * 0.98
        End If

        Return fundedAmount
    End Function

    ' Simulated legacy audit logging
    Private Sub LogFunding(requestedAmount As Double, fundedAmount As Double, loanType As String, creditScore As Integer)

        Dim logLine As String =
            DateTime.Now.ToString() & "|" &
            loanType & "|" &
            creditScore & "|" &
            requestedAmount & "|" &
            fundedAmount

        My.Computer.FileSystem.WriteAllText(
            "C:\temp\loan_funding.log",
            logLine & Environment.NewLine,
            True
        )
    End Sub

End Class


"""

result = app.invoke({"vb_code": vb_code})

for k, v in result.items():
    print(f"\n===== {k.upper()} =====\n")
    print(v)
