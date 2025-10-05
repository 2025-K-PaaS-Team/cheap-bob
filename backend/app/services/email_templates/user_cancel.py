def get_customer_cancel_text_template(timestamp: str, recipient: str, store: str) -> str:
        """소비자 주문 취소 텍스트 템플릿"""
        return f"""{store}에 대한 주문이 취소되었습니다.
발송 시간: {timestamp}
수신자: {recipient}"""

def get_cusotmer_cancel_html_template(timestamp: str, recipient: str, store: str) -> str:
        """소비자 주문 취소 HTML 템플릿"""
        return f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>소비자 주문 취소</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}

                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    background-color: #f5f5f5;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    padding: 20px;
                }}

                .container {{
                    background-color: white;
                    border-radius: 16px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    max-width: 400px;
                    width: 100%;
                    overflow: hidden;
                }}

                .header {{
                    background-color: #8AE234;
                    padding: 20px;
                    text-align: center;
                }}

                .header h1 {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #333;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 8px;
                }}

                .party-icon {{
                    font-size: 28px;
                }}

                .content {{
                    padding: 40px 30px;
                    background-color: white;
                }}

                .message {{
                    font-size: 18px;
                    line-height: 1.6;
                    color: #333;
                    margin-bottom: 30px;
                }}

                .info-section {{
                    margin-bottom: 30px;
                }}

                .info-item {{
                    margin-bottom: 15px;
                    font-size: 16px;
                    color: #555;
                }}

                .info-item strong {{
                    color: #333;
                }}

                .button-container {{
                    text-align: center;
                    margin-top: 40px;
                }}

                .confirm-button {{
                    background-color: #8AE234;
                    color: #333;
                    border: none;
                    padding: 15px 40px;
                    font-size: 18px;
                    font-weight: bold;
                    border-radius: 8px;
                    cursor: pointer;
                    transition: background-color 0.3s ease;
                }}

                .confirm-button:hover {{
                    background-color: #7ACC2D;
                }}

                @media (max-width: 480px) {{
                    .header h1 {{
                        font-size: 20px;
                    }}
                    
                    .message {{
                        font-size: 16px;
                    }}
                    
                    .info-item {{
                        font-size: 14px;
                    }}
                    
                    .confirm-button {{
                        font-size: 16px;
                        padding: 12px 30px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>
                        주문이 취소되었습니다.
                    </h1>
                </div>
                
                <div class="content">
                    <p class="message">
                        {store}에 대한 주문이 취소되었습니다.
                    </p>
                    
                    <div class="info-section">
                        <div class="info-item">
                            <strong>발송시간:</strong> {timestamp}
                        </div>
                        <div class="info-item">
                            <strong>수신처:</strong> {recipient}
                        </div>
                    </div>
                    
                    <div class="button-container">
                        <button class="confirm-button" onclick="window.location.href='https://cheap-bob.vercel.app'">
                            주문 확인하기
                        </button>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """