"""
Google Search Console Checker
Verifica si existen URLs rankeando para keywords antes de generar contenido
Usa OAuth2 flow para autenticación
"""

import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional, Tuple
import os

class GSCChecker:
    """Cliente para verificar keywords en Google Search Console"""
    
    SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
    
    def __init__(self, site_url: str = "https://www.pccomponentes.com/"):
        """
        Inicializa el checker de GSC
        
        Args:
            site_url: URL del sitio en GSC (con www)
        """
        self.site_url = site_url
        self.service = None
    
    @staticmethod
    def init_oauth_flow(client_config: dict, redirect_uri: str = "http://localhost:8501") -> Flow:
        """
        Inicializa el flujo OAuth2
        
        Args:
            client_config: Configuración del cliente OAuth2
            redirect_uri: URI de redirección
        
        Returns:
            Flow object configurado
        """
        flow = Flow.from_client_config(
            client_config,
            scopes=GSCChecker.SCOPES,
            redirect_uri=redirect_uri
        )
        return flow
    
    def authenticate_with_credentials(self, credentials_dict: dict) -> bool:
        """
        Autentica usando credenciales almacenadas
        
        Args:
            credentials_dict: Diccionario con token, refresh_token, etc.
        
        Returns:
            True si autenticación exitosa
        """
        try:
            credentials = Credentials(
                token=credentials_dict.get('token'),
                refresh_token=credentials_dict.get('refresh_token'),
                token_uri=credentials_dict.get('token_uri'),
                client_id=credentials_dict.get('client_id'),
                client_secret=credentials_dict.get('client_secret'),
                scopes=GSCChecker.SCOPES
            )
            
            self.service = build('searchconsole', 'v1', credentials=credentials)
            return True
            
        except Exception as e:
            st.error(f"Error autenticando: {str(e)}")
            return False
    
    def check_keyword_comprehensive(
        self,
        keyword: str,
        periods: List[int] = [1, 7, 28],
        position_threshold: int = 30,
        impressions_threshold: int = 50
    ) -> Dict:
        """
        Verificación comprehensiva con keyword + variaciones
        
        Args:
            keyword: Keyword principal a verificar
            periods: Períodos a consultar en días
            position_threshold: Alertar si posición < X
            impressions_threshold: Alertar si impresiones > X (en 28d)
        
        Returns:
            Diccionario con resultados y alertas
        """
        if not self.service:
            return {"error": "No autenticado"}
        
        # 1. Generar variaciones de la keyword
        variations = self._generate_keyword_variations(keyword)
        
        # 2. Consultar cada variación
        all_results = {}
        urls_aggregate = {}  # Agregar URLs encontradas
        
        for variation in variations:
            for days in periods:
                try:
                    result = self._query_gsc(variation, days)
                    
                    # Almacenar resultado
                    key = f"{variation}_{days}d"
                    all_results[key] = result
                    
                    # Agregar URLs por período
                    if result['urls']:
                        for url_data in result['urls']:
                            url = url_data['url']
                            if url not in urls_aggregate:
                                urls_aggregate[url] = {
                                    '24h': None,
                                    '7d': None,
                                    '28d': None,
                                    'variations_found': set()
                                }
                            
                            period_key = f"{days}d" if days > 1 else "24h"
                            urls_aggregate[url][period_key] = {
                                'position': url_data['position'],
                                'impressions': url_data['impressions'],
                                'clicks': url_data['clicks'],
                                'ctr': url_data['ctr']
                            }
                            urls_aggregate[url]['variations_found'].add(variation)
                
                except Exception as e:
                    st.warning(f"Error consultando '{variation}' ({days}d): {str(e)}")
        
        # 3. Analizar y filtrar URLs relevantes
        alerts = self._analyze_and_alert(
            urls_aggregate,
            position_threshold,
            impressions_threshold
        )
        
        return {
            'keyword': keyword,
            'variations_checked': variations,
            'urls_found': urls_aggregate,
            'alerts': alerts,
            'periods': periods,
            'raw_results': all_results
        }
    
    def _generate_keyword_variations(self, keyword: str) -> List[str]:
        """
        Genera variaciones de la keyword para búsqueda amplia
        
        Args:
            keyword: Keyword principal
        
        Returns:
            Lista de variaciones a buscar
        """
        variations = [keyword.lower()]  # Exacta en minúsculas
        
        # Extraer términos clave
        terms = keyword.lower().split()
        
        # Si tiene más de 2 palabras, crear variaciones
        if len(terms) >= 3:
            # Variación 1: Primeras 2 palabras
            variations.append(' '.join(terms[:2]))
            
            # Variación 2: Últimas 2 palabras
            variations.append(' '.join(terms[-2:]))
            
            # Variación 3: Términos más relevantes (marcas, números)
            relevant_terms = [t for t in terms if len(t) > 3 or any(c.isdigit() for c in t)]
            if len(relevant_terms) >= 2:
                variations.append(' '.join(relevant_terms[:2]))
        
        # Eliminar duplicados manteniendo orden
        return list(dict.fromkeys(variations))
    
    def _query_gsc(self, query: str, days: int) -> Dict:
        """
        Consulta GSC API para una query y período específicos
        
        Args:
            query: Query exacta a buscar
            days: Días hacia atrás desde hoy
        
        Returns:
            Diccionario con URLs y métricas
        """
        # Calcular fechas
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Preparar request
        request = {
            'startDate': start_date.strftime('%Y-%m-%d'),
            'endDate': end_date.strftime('%Y-%m-%d'),
            'dimensions': ['page'],
            'dimensionFilterGroups': [{
                'filters': [{
                    'dimension': 'query',
                    'operator': 'equals',
                    'expression': query
                }]
            }],
            'rowLimit': 100
        }
        
        # Ejecutar query
        response = self.service.searchanalytics().query(
            siteUrl=self.site_url,
            body=request
        ).execute()
        
        # Procesar resultados
        urls_data = []
        total_impressions = 0
        total_clicks = 0
        
        if 'rows' in response:
            for row in response['rows']:
                url = row['keys'][0]
                impressions = row['impressions']
                clicks = row['clicks']
                ctr = row['ctr'] * 100
                position = row['position']
                
                urls_data.append({
                    'url': url,
                    'impressions': impressions,
                    'clicks': clicks,
                    'ctr': round(ctr, 2),
                    'position': round(position, 1)
                })
                
                total_impressions += impressions
                total_clicks += clicks
            
            # Ordenar por impresiones
            urls_data.sort(key=lambda x: x['impressions'], reverse=True)
        
        return {
            'urls': urls_data,
            'total_impressions': total_impressions,
            'total_clicks': total_clicks,
            'period_days': days,
            'query': query
        }
    
    def _analyze_and_alert(
        self,
        urls_aggregate: Dict,
        position_threshold: int,
        impressions_threshold: int
    ) -> List[Dict]:
        """
        Analiza URLs encontradas y genera alertas según umbrales
        
        Args:
            urls_aggregate: URLs agregadas con métricas
            position_threshold: Umbral de posición
            impressions_threshold: Umbral de impresiones
        
        Returns:
            Lista de alertas con nivel de severidad
        """
        alerts = []
        
        for url, data in urls_aggregate.items():
            # Convertir set a list para serialización
            data['variations_found'] = list(data['variations_found'])
            
            # Obtener métricas del período más largo (28d)
            metrics_28d = data.get('28d')
            if not metrics_28d:
                continue
            
            position = metrics_28d['position']
            impressions = metrics_28d['impressions']
            clicks = metrics_28d['clicks']
            
            # Determinar nivel de alerta
            alert_level = self._determine_alert_level(
                position, impressions, clicks,
                position_threshold, impressions_threshold
            )
            
            if alert_level:
                alerts.append({
                    'url': url,
                    'level': alert_level,
                    'position': position,
                    'impressions': impressions,
                    'clicks': clicks,
                    'variations': data['variations_found'],
                    'data_24h': data.get('24h'),
                    'data_7d': data.get('7d'),
                    'data_28d': metrics_28d,
                    'recommendation': self._get_recommendation(alert_level, position, impressions)
                })
        
        # Ordenar por severidad y luego por impresiones
        severity_order = {'critical': 0, 'warning': 1, 'info': 2}
        alerts.sort(key=lambda x: (severity_order[x['level']], -x['impressions']))
        
        return alerts
    
    def _determine_alert_level(
        self,
        position: float,
        impressions: int,
        clicks: int,
        position_threshold: int,
        impressions_threshold: int
    ) -> Optional[str]:
        """
        Determina nivel de alerta según métricas
        
        Returns:
            'critical', 'warning', 'info' o None
        """
        # CRITICAL: Posición alta + impresiones significativas
        if position <= 10 and impressions >= impressions_threshold * 2:
            return 'critical'
        
        # CRITICAL: Cualquier posición en página 1 con tráfico
        if position <= 10 and clicks > 0:
            return 'critical'
        
        # WARNING: Posición aceptable + impresiones sobre umbral
        if position <= position_threshold and impressions >= impressions_threshold:
            return 'warning'
        
        # WARNING: Posición alta pero pocas impresiones
        if position <= 10 and impressions < impressions_threshold:
            return 'warning'
        
        # INFO: Posición baja pero con algo de tráfico
        if position > position_threshold and impressions >= impressions_threshold / 2:
            return 'info'
        
        return None
    
    def _get_recommendation(
        self,
        alert_level: str,
        position: float,
        impressions: int
    ) -> str:
        """
        Genera recomendación según nivel de alerta
        """
        if alert_level == 'critical':
            if position <= 5:
                return "⛔ URL en TOP 5 con tráfico significativo. EVITA crear contenido nuevo - actualiza esta URL existente"
            else:
                return "⚠️ URL en página 1 generando clicks. Actualizar contenido existente es más seguro que crear nuevo"
        
        elif alert_level == 'warning':
            if position <= 10:
                return "⚠️ URL en página 1 pero con poco tráfico. Considera optimizar esta URL antes de crear contenido nuevo"
            else:
                return "💡 URL rankeando con tráfico moderado. Evalúa si actualizar o crear contenido complementario"
        
        elif alert_level == 'info':
            return "ℹ️ URL con visibilidad baja. Puedes crear contenido nuevo o mejorar esta URL"
        
        return ""


def render_gsc_auth_ui(client_config: dict) -> Optional[dict]:
    """
    UI para autenticación OAuth2 con Google Search Console
    
    Args:
        client_config: Configuración del cliente OAuth2
    
    Returns:
        Credenciales si autenticado, None si no
    """
    st.markdown("### 🔐 Autenticación Google Search Console")
    
    # Check si ya está autenticado en session_state
    if 'gsc_credentials' in st.session_state and st.session_state.gsc_credentials:
        st.success("✅ Autenticado correctamente")
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🔄 Re-autenticar"):
                st.session_state.gsc_credentials = None
                st.rerun()
        
        return st.session_state.gsc_credentials
    
    st.info("Necesitas autenticarte con Google para acceder a Search Console")
    
    # Botón de autenticación
    if st.button("🔑 Conectar con Google Search Console", type="primary"):
        try:
            # Crear flow OAuth2
            flow = GSCChecker.init_oauth_flow(client_config)
            
            # Generar URL de autorización
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
            
            # Mostrar instrucciones
            st.markdown("### Pasos para autenticar:")
            st.markdown(f"1. [Click aquí para abrir Google Auth]({auth_url})")
            st.markdown("2. Autoriza el acceso a Search Console")
            st.markdown("3. Copia el código de autorización que aparece")
            
            # Input para código
            auth_code = st.text_input(
                "4. Pega el código aquí:",
                placeholder="4/0AfJoh...",
                key="gsc_auth_code"
            )
            
            if auth_code:
                with st.spinner("Verificando código..."):
                    try:
                        # Exchange code por token
                        flow.fetch_token(code=auth_code)
                        
                        # Guardar credenciales
                        credentials = flow.credentials
                        credentials_dict = {
                            'token': credentials.token,
                            'refresh_token': credentials.refresh_token,
                            'token_uri': credentials.token_uri,
                            'client_id': credentials.client_id,
                            'client_secret': credentials.client_secret,
                            'scopes': credentials.scopes
                        }
                        
                        st.session_state.gsc_credentials = credentials_dict
                        st.success("✅ Autenticación exitosa!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error al verificar código: {str(e)}")
            
        except Exception as e:
            st.error(f"Error iniciando autenticación: {str(e)}")
    
    return None


def render_gsc_check_results(results: Dict):
    """
    Renderiza resultados de verificación GSC
    
    Args:
        results: Diccionario con resultados de check_keyword_comprehensive
    """
    keyword = results['keyword']
    alerts = results['alerts']
    urls_found = results['urls_found']
    variations = results['variations_checked']
    
    st.markdown(f"### 🔍 Análisis GSC: `{keyword}`")
    
    # Mostrar variaciones consultadas
    with st.expander("ℹ️ Variaciones consultadas", expanded=False):
        st.write(", ".join([f"`{v}`" for v in variations]))
    
    # Si no hay alertas
    if not alerts:
        st.success("✅ No se encontró contenido existente rankeando significativamente")
        st.caption("Puedes crear contenido nuevo sin riesgo de canibalización")
        return
    
    # Mostrar alertas por nivel
    critical_alerts = [a for a in alerts if a['level'] == 'critical']
    warning_alerts = [a for a in alerts if a['level'] == 'warning']
    info_alerts = [a for a in alerts if a['level'] == 'info']
    
    # CRITICAL
    if critical_alerts:
        st.error(f"⛔ **ATENCIÓN CRÍTICA:** {len(critical_alerts)} URL(s) con ranking significativo")
        
        for alert in critical_alerts:
            with st.expander(
                f"🔴 {alert['url']} - Pos. #{alert['position']:.1f} - {alert['impressions']:,} impresiones",
                expanded=True
            ):
                _render_alert_details(alert)
    
    # WARNING
    if warning_alerts:
        st.warning(f"⚠️ **PRECAUCIÓN:** {len(warning_alerts)} URL(s) con ranking moderado")
        
        for alert in warning_alerts:
            with st.expander(
                f"🟡 {alert['url']} - Pos. #{alert['position']:.1f} - {alert['impressions']:,} impresiones",
                expanded=False
            ):
                _render_alert_details(alert)
    
    # INFO
    if info_alerts:
        with st.expander(f"ℹ️ {len(info_alerts)} URL(s) adicionales con visibilidad baja"):
            for alert in info_alerts:
                st.markdown(f"**{alert['url']}** - Pos. #{alert['position']:.1f}")
                st.caption(alert['recommendation'])
                st.markdown("---")


def _render_alert_details(alert: Dict):
    """Renderiza detalles de una alerta"""
    
    # Métricas en columnas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 24h", 
                  f"Pos. #{alert['data_24h']['position']:.1f}" if alert['data_24h'] else "Sin datos",
                  f"{alert['data_24h']['impressions']} imp." if alert['data_24h'] else "")
    
    with col2:
        st.metric("📊 7 días",
                  f"Pos. #{alert['data_7d']['position']:.1f}" if alert['data_7d'] else "Sin datos",
                  f"{alert['data_7d']['impressions']} imp." if alert['data_7d'] else "")
    
    with col3:
        st.metric("📊 28 días",
                  f"Pos. #{alert['position']:.1f}",
                  f"{alert['impressions']:,} imp.")
    
    # Clicks y CTR
    if alert['clicks'] > 0:
        st.info(f"👆 **{alert['clicks']} clicks** en 28 días - CTR: {alert['data_28d']['ctr']}%")
    
    # Variaciones encontradas
    st.caption(f"Encontrada en: {', '.join([f'`{v}`' for v in alert['variations']])}")
    
    # Recomendación destacada
    st.markdown(f"### {alert['recommendation']}")
    
    # Enlace a la URL
    st.markdown(f"[🔗 Ver página en vivo]({alert['url']})")
    
    # Botón para usar esta URL como base
    if st.button(f"✏️ Actualizar esta URL en lugar de crear nueva", key=f"update_{alert['url']}"):
        st.session_state['update_existing_url'] = alert['url']
        st.info(f"Modo actualización activado para: {alert['url']}")
