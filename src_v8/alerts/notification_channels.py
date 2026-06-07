#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Canais de Notificação - Culture Pulse V9.0
Sistema unificado para envio de notificações via múltiplos canais

🎯 FUNCIONALIDADES:
- Email SMTP configurável
- Slack webhook integration
- Webhook endpoints customizados
- Dashboard notifications em tempo real
- Template system para mensagens
- Rate limiting por canal
- Retry logic com backoff
"""

import asyncio
import logging
import smtplib
import json
import time
import aiohttp
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from abc import ABC, abstractmethod
import requests

from .alert_config import NotificationConfig
from .alert_rules import Alert, AlertLevel

logger = logging.getLogger(__name__)

class NotificationChannel(ABC):
    """Interface base para canais de notificação"""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
        self.enabled = True
        self.last_sent = {}
        self.send_count = 0
        self.error_count = 0
    
    @abstractmethod
    async def send_alert(self, alert: Alert) -> bool:
        """Enviar alerta pelo canal"""
        pass
    
    @abstractmethod
    def is_configured(self) -> bool:
        """Verificar se canal está configurado"""
        pass
    
    def can_send(self, alert: Alert) -> bool:
        """Verificar se pode enviar (rate limiting)"""
        # Rate limiting básico: max 10 por minuto por canal
        now = time.time()
        if now - self.last_sent.get('timestamp', 0) < 6:  # 6 segundos entre envios
            return False
        return True
    
    def record_send(self, success: bool):
        """Registrar envio"""
        self.last_sent['timestamp'] = time.time()
        if success:
            self.send_count += 1
        else:
            self.error_count += 1

class EmailChannel(NotificationChannel):
    """Canal de notificação por email"""
    
    def __init__(self, config: NotificationConfig):
        super().__init__(config)
        self.smtp_server = None
    
    def is_configured(self) -> bool:
        """Verificar se email está configurado"""
        return (self.config.email_enabled and 
                self.config.smtp_username and 
                self.config.smtp_password and
                self.config.default_recipients)
    
    async def send_alert(self, alert: Alert) -> bool:
        """Enviar alerta por email"""
        if not self.can_send(alert) or not self.is_configured():
            return False
        
        try:
            # Conectar ao SMTP
            smtp = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port)
            smtp.starttls()
            smtp.login(self.config.smtp_username, self.config.smtp_password)
            
            # Criar mensagem
            msg = self._create_email_message(alert)
            
            # Enviar para todos os destinatários
            for recipient in self.config.default_recipients:
                smtp.send_message(msg, to_addrs=[recipient])
            
            smtp.quit()
            self.record_send(True)
            
            logger.info(f"Email enviado para {len(self.config.default_recipients)} destinatários")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            self.record_send(False)
            return False
    
    def _create_email_message(self, alert: Alert) -> MIMEMultipart:
        """Criar mensagem de email formatada"""
        msg = MIMEMultipart('alternative')
        
        # Headers
        msg['Subject'] = f"[Culture Pulse] {alert.title}"
        msg['From'] = self.config.smtp_username
        msg['To'] = ', '.join(self.config.default_recipients)
        
        # Corpo do email
        text_body = self._create_text_body(alert)
        html_body = self._create_html_body(alert)
        
        msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        
        return msg
    
    def _create_text_body(self, alert: Alert) -> str:
        """Criar corpo de texto do email"""
        return f"""
Culture Pulse - Alerta {alert.level.value.upper()}

Título: {alert.title}
Nível: {alert.level.value}
Tipo: {alert.alert_type.value}
Horário: {alert.timestamp.strftime('%d/%m/%Y %H:%M:%S')}

Mensagem:
{alert.message}

Dados:
{json.dumps(alert.data, indent=2, ensure_ascii=False)}

---
Culture Pulse V9.0 - Sistema de Alertas
        """.strip()
    
    def _create_html_body(self, alert: Alert) -> str:
        """Criar corpo HTML do email"""
        level_colors = {
            'info': '#3498db',
            'warning': '#f39c12',
            'error': '#e74c3c',
            'critical': '#c0392b'
        }
        
        color = level_colors.get(alert.level.value, '#3498db')
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: {color}; color: white; padding: 15px; border-radius: 5px 5px 0 0;">
                    <h2 style="margin: 0;">Culture Pulse - Alerta {alert.level.value.upper()}</h2>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; border: 1px solid #dee2e6; border-radius: 0 0 5px 5px;">
                    <h3 style="color: {color}; margin-top: 0;">{alert.title}</h3>
                    
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #dee2e6;"><strong>Nível:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{alert.level.value}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #dee2e6;"><strong>Tipo:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{alert.alert_type.value}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid #dee2e6;"><strong>Horário:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{alert.timestamp.strftime('%d/%m/%Y %H:%M:%S')}</td>
                        </tr>
                    </table>
                    
                    <div style="margin: 20px 0;">
                        <h4>Mensagem:</h4>
                        <p style="background: white; padding: 15px; border-left: 4px solid {color}; margin: 0;">
                            {alert.message}
                        </p>
                    </div>
                </div>
                
                <div style="margin-top: 20px; font-size: 12px; color: #6c757d; text-align: center;">
                    Culture Pulse V9.0 - Sistema de Alertas
                </div>
            </div>
        </body>
        </html>
        """

class SlackChannel(NotificationChannel):
    """Canal de notificação via Slack"""
    
    def __init__(self, config: NotificationConfig):
        super().__init__(config)
    
    def is_configured(self) -> bool:
        """Verificar se Slack está configurado"""
        return (self.config.slack_enabled and 
                self.config.slack_webhook_url)
    
    async def send_alert(self, alert: Alert) -> bool:
        """Enviar alerta para Slack"""
        if not self.can_send(alert) or not self.is_configured():
            return False
        
        try:
            payload = self._create_slack_payload(alert)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.slack_webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        self.record_send(True)
                        logger.info("Alerta enviado para Slack")
                        return True
                    else:
                        logger.error(f"Erro Slack: {response.status}")
                        self.record_send(False)
                        return False
                        
        except Exception as e:
            logger.error(f"Erro ao enviar para Slack: {e}")
            self.record_send(False)
            return False
    
    def _create_slack_payload(self, alert: Alert) -> Dict[str, Any]:
        """Criar payload para Slack"""
        level_emojis = {
            'info': ':information_source:',
            'warning': ':warning:',
            'error': ':x:',
            'critical': ':rotating_light:'
        }
        
        level_colors = {
            'info': '#3498db',
            'warning': '#f39c12',
            'error': '#e74c3c',
            'critical': '#c0392b'
        }
        
        emoji = level_emojis.get(alert.level.value, ':bell:')
        color = level_colors.get(alert.level.value, '#3498db')
        
        return {
            "channel": self.config.slack_channel,
            "username": self.config.slack_username,
            "attachments": [
                {
                    "color": color,
                    "title": f"{emoji} {alert.title}",
                    "text": alert.message,
                    "fields": [
                        {
                            "title": "Nível",
                            "value": alert.level.value.upper(),
                            "short": True
                        },
                        {
                            "title": "Tipo", 
                            "value": alert.alert_type.value,
                            "short": True
                        },
                        {
                            "title": "Horário",
                            "value": alert.timestamp.strftime('%d/%m/%Y %H:%M:%S'),
                            "short": True
                        }
                    ],
                    "footer": "Culture Pulse V9.0",
                    "ts": int(alert.timestamp.timestamp())
                }
            ]
        }

class WebhookChannel(NotificationChannel):
    """Canal de notificação via webhook"""
    
    def __init__(self, config: NotificationConfig):
        super().__init__(config)
    
    def is_configured(self) -> bool:
        """Verificar se webhook está configurado"""
        return (self.config.webhook_enabled and 
                self.config.webhook_urls)
    
    async def send_alert(self, alert: Alert) -> bool:
        """Enviar alerta via webhook"""
        if not self.can_send(alert) or not self.is_configured():
            return False
        
        success_count = 0
        payload = self._create_webhook_payload(alert)
        
        try:
            async with aiohttp.ClientSession() as session:
                for url in self.config.webhook_urls:
                    try:
                        async with session.post(
                            url,
                            json=payload,
                            timeout=aiohttp.ClientTimeout(total=self.config.webhook_timeout)
                        ) as response:
                            if response.status in [200, 201, 202]:
                                success_count += 1
                            else:
                                logger.warning(f"Webhook {url} retornou {response.status}")
                                
                    except Exception as e:
                        logger.error(f"Erro webhook {url}: {e}")
            
            success = success_count > 0
            self.record_send(success)
            
            if success:
                logger.info(f"Alerta enviado para {success_count}/{len(self.config.webhook_urls)} webhooks")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro geral webhook: {e}")
            self.record_send(False)
            return False
    
    def _create_webhook_payload(self, alert: Alert) -> Dict[str, Any]:
        """Criar payload para webhook"""
        return {
            "event": "alert_created",
            "alert": alert.to_dict(),
            "system": "culture_pulse_v9",
            "timestamp": datetime.now().isoformat()
        }

class DashboardChannel(NotificationChannel):
    """Canal para notificações no dashboard (em memória)"""
    
    def __init__(self, config: NotificationConfig):
        super().__init__(config)
        self.notifications = []
    
    def is_configured(self) -> bool:
        """Dashboard sempre configurado"""
        return True
    
    async def send_alert(self, alert: Alert) -> bool:
        """Adicionar alerta às notificações do dashboard"""
        notification = {
            'id': alert.id,
            'title': alert.title,
            'message': alert.message,
            'level': alert.level.value,
            'timestamp': alert.timestamp.isoformat(),
            'read': False
        }
        
        self.notifications.append(notification)
        
        # Manter apenas últimas 50 notificações
        if len(self.notifications) > 50:
            self.notifications = self.notifications[-50:]
        
        self.record_send(True)
        return True
    
    def get_notifications(self, unread_only: bool = False) -> List[Dict[str, Any]]:
        """Obter notificações do dashboard"""
        if unread_only:
            return [n for n in self.notifications if not n['read']]
        return self.notifications.copy()
    
    def mark_as_read(self, notification_id: str) -> bool:
        """Marcar notificação como lida"""
        for notification in self.notifications:
            if notification['id'] == notification_id:
                notification['read'] = True
                return True
        return False

class NotificationManager:
    """
    Gerenciador principal de notificações (V9.9)
    Integrado com o sistema de planos (plan_config.py).
    """
    
    def __init__(self, config: NotificationConfig):
        self.config = config
        
        # Inicializar canais
        self.channels = {
            'email': EmailChannel(config),
            'slack': SlackChannel(config),
            'webhook': WebhookChannel(config),
            'dashboard': DashboardChannel(config)
        }
        
        # Filtros por nível
        self.level_filters = {
            'email': [AlertLevel.ERROR, AlertLevel.CRITICAL],
            'slack': [AlertLevel.WARNING, AlertLevel.ERROR, AlertLevel.CRITICAL],
            'webhook': [AlertLevel.INFO, AlertLevel.WARNING, AlertLevel.ERROR, AlertLevel.CRITICAL],
            'dashboard': [AlertLevel.INFO, AlertLevel.WARNING, AlertLevel.ERROR, AlertLevel.CRITICAL]
        }
        
        logger.info(f"NotificationManager V9.9 initialized with {len(self.channels)} channels")
    
    def configure(self, config: NotificationConfig):
        """Reconfigurar manager"""
        self.config = config
        for channel in self.channels.values():
            channel.config = config
    
    async def send_alert(self, alert: Alert, user_tier: str = "free"):
        """
        Enviar alerta para todos os canais apropriados,
        respeitando as travas de segurança do plano (V9.9).
        """
        # Carregar permissões do plano
        try:
            from config.plan_config import get_plan
            plan_permissions = get_plan(user_tier)
        except ImportError:
            logger.warning("⚠️ plan_config não encontrado. Usando permissões 'free' por segurança.")
            plan_permissions = {"alerts_email": None, "alerts_teams": False, "alerts_whatsapp": False}

        tasks = []
        
        for channel_name, channel in self.channels.items():
            # 1. Trava de Segurança por Plano (V9.9 Enforcement)
            if channel_name == 'email' and not plan_permissions.get('alerts_email'):
                continue
            if channel_name == 'slack' and not plan_permissions.get('alerts_teams'):
                # Nota: Slack é mapeado como Alerts Teams no dashboard
                continue
            if channel_name == 'webhook' and not plan_permissions.get('api_integration'):
                 continue
            
            # 2. Verificar se canal deve receber este nível de alerta
            if alert.level not in self.level_filters.get(channel_name, []):
                continue
            
            # 3. Verificar se canal está configurado
            if not channel.is_configured():
                continue
            
            # Criar task assíncrona
            task = asyncio.create_task(
                self._send_to_channel(channel_name, channel, alert)
            )
            tasks.append(task)
        
        # Executar todos os envios em paralelo
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            success_count = sum(1 for result in results if result is True)
            logger.info(f"Alerta enviado para {success_count}/{len(tasks)} canais (Tier: {user_tier})")
    
    async def _send_to_channel(self, channel_name: str, channel: NotificationChannel, alert: Alert) -> bool:
        """Enviar para canal específico com retry"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                success = await channel.send_alert(alert)
                if success:
                    return True
                
                # Backoff exponencial
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    
            except Exception as e:
                logger.error(f"Erro canal {channel_name} (tentativa {attempt + 1}): {e}")
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
        
        logger.error(f"Falha ao enviar para {channel_name} após {max_retries} tentativas")
        return False
    
    def get_channel_stats(self) -> Dict[str, Dict[str, Any]]:
        """Obter estatísticas dos canais"""
        stats = {}
        
        for name, channel in self.channels.items():
            stats[name] = {
                'configured': channel.is_configured(),
                'enabled': channel.enabled,
                'send_count': channel.send_count,
                'error_count': channel.error_count,
                'last_sent': channel.last_sent.get('timestamp', 0),
                'success_rate': (
                    channel.send_count / (channel.send_count + channel.error_count)
                    if (channel.send_count + channel.error_count) > 0 else 0
                )
            }
        
        return stats
    
    def get_dashboard_notifications(self, unread_only: bool = False) -> List[Dict[str, Any]]:
        """Obter notificações do dashboard"""
        dashboard_channel = self.channels['dashboard']
        return dashboard_channel.get_notifications(unread_only)
    
    def mark_notification_read(self, notification_id: str) -> bool:
        """Marcar notificação como lida"""
        dashboard_channel = self.channels['dashboard']
        return dashboard_channel.mark_as_read(notification_id)
