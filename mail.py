import yfinance as yf
from portfolio import PORTFOLIO
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

import os

SENDER_EMAIL = os.environ.get("sharesam63@gmail.com")
APP_PASSWORD = os.environ.get("pqkgcfmeymhtbnoz")
RECEIVER_EMAIL = os.environ.get("sharesam63@gmail.com")

# ---------- FETCH CURRENT PRICE ----------
def get_current_price(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period="1d")
    return data["Close"].iloc[-1]

total_invested = 0
total_current = 0
rows_html = ""

# ---------- PER STOCK CALCULATION ----------
for stock in PORTFOLIO:
    symbol = stock["symbol"]
    qty = stock["quantity"]
    buy_price = stock["buy_price"]

    current_price = get_current_price(symbol)

    invested = qty * buy_price
    current = qty * current_price
    pnl = current - invested

    total_invested += invested
    total_current += current

    stock_color = "green" if pnl >= 0 else "red"
    stock_status = "PROFIT 🟢" if pnl >= 0 else "LOSS 🔴"

    rows_html += f"""
    <tr>
        <td>{symbol}</td>
        <td>{qty}</td>
        <td>₹{buy_price}</td>
        <td>₹{round(current_price,2)}</td>
        <td style="color:{stock_color};">₹{round(pnl,2)} ({stock_status})</td>
    </tr>
    """

# ---------- TOTAL P/L ----------
total_pnl = round(total_current - total_invested, 2)
color = "green" if total_pnl >= 0 else "red"
status = "TOTAL PROFIT 🟢" if total_pnl >= 0 else "TOTAL LOSS 🔴"

# ---------- EMAIL BODY ----------
html_body = f"""
<h2 style="color:{color};">{status}: ₹{total_pnl:,.2f}</h2>
<p><b>Date:</b> {datetime.now().strftime('%d-%m-%Y')}</p>

<table border="1" cellpadding="8" cellspacing="0">
<tr>
    <th>Stock</th>
    <th>Qty</th>
    <th>Buy Price</th>
    <th>Current Price</th>
    <th>P/L</th>
</tr>
{rows_html}
</table>
"""

# ---------- SEND EMAIL ----------
msg = MIMEMultipart("alternative")
msg["Subject"] = f"Daily Portfolio Report - {status}"
msg["From"] = SENDER_EMAIL
msg["To"] = RECEIVER_EMAIL
msg.attach(MIMEText(html_body, "html"))

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(SENDER_EMAIL, APP_PASSWORD)
    server.send_message(msg)

print("Daily portfolio email sent successfully.")