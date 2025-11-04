def get_accept_text_template(timestamp: str, recipient: str, store: str) -> str:
        """수락 텍스트 템플릿"""
        return f"""{store} 주문이 픽업 확정되었습니다.
픽업 시간에 가게를 방문하시기 바랍니다.
발송 시간: {timestamp}
수신자: {recipient}"""

def get_accept_html_template(timestamp: str, recipient: str, store: str) -> str:
        """수락 HTML 템플릿"""
        return f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>주문 수락</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}

                a {{
                    color: #333 !important;
                    text-decoration: none;
                }}

                .ii a[href] {{
                    color: #333 !important;
                }}

                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    background-color: #e9e9e2;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    padding: 20px;
                }}

                .container {{
                    background-color: #e9e9e2;
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
                    background-color: #e9e9e2;
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
                    display: inline-block;
                    background-color: #8AE234;
                    color: #333;
                    text-decoration: none;
                    padding: 15px 40px;
                    font-size: 18px;
                    font-weight: bold;
                    border-radius: 8px;
                    transition: background-color 0.3s ease;
                }}

                .confirm-button:hover {{
                    background-color: #7ACC2D;
                    color: #333;
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
                        <span class="party-icon">🎉</span>
                        픽업이 확정되었습니다!
                    </h1>
                </div>
                
                <div class="content">
                    <p class="message">
                        {store} 주문이 픽업 확정되었습니다.<br>
                        픽업 시간에 가게를 방문하시기 바랍니다.
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
                        <a href="https://www.cheap-bob.store/c/noti" class="confirm-button">
                            주문 확인하기
                        </a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """