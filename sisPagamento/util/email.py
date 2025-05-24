import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def enviar_email_relatorio(destinatario: str, assunto: str, corpo: str) -> bool:
    # Configurações do servidor SMTP (exemplo Gmail)
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    REMETENTE = "seu email"
    SENHA = "sua senha"  

    try:
        mensagem = MIMEMultipart()
        mensagem['From'] = REMETENTE
        mensagem['To'] = destinatario
        mensagem['Subject'] = assunto
        mensagem.attach(MIMEText(corpo, 'plain'))

        servidor = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        servidor.starttls()
        servidor.login(REMETENTE, SENHA)
        servidor.send_message(mensagem)
        servidor.quit()
        return True
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        return False
