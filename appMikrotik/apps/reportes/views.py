from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.db import connection

# Importamos los modelos de la app core
from core.models import Pago, Cliente, Logs

# ReportLab para la construcción del reporte PDF institucional
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import os
from django.conf import settings

def obtener_fechas_filtro(criterio):
    """ Función auxiliar corregida para calcular rangos con datetimes ingenuos (naive) """
    # Usamos datetime.now() nativo de Python para que coincida con USE_TZ = False
    ahora = datetime.now()
    
    if criterio == '7dias':
        return ahora - timedelta(days=7), ahora
    elif criterio == 'mes':
        # Primer día del mes en curso a las 00:00:00
        inicio_mes = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return inicio_mes, ahora
    elif criterio == 'actualmente' or not criterio:
        # Histórico global sin límite inferior
        return None, ahora
    else:
        # Manejo de meses específicos en formato 'YYYY-MM' (Ej: '2026-06')
        try:
            año, mes = map(int, criterio.split('-'))
            inicio = datetime(año, mes, 1, 0, 0, 0)
            if mes == 12:
                fin = datetime(año + 1, 1, 1, 23, 59, 59) - timedelta(days=1)
            else:
                fin = datetime(año, mes + 1, 1, 23, 59, 59) - timedelta(days=1)
            
            return inicio, fin
        except (ValueError, IndexError):
            return None, ahora

def formatear_moneda_ve(valor):
    """ Formatea un float al estándar de lectura en Venezuela: 1.250,50 """
    try:
        return f"{float(valor or 0.0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except ValueError:
        return "0,00"

@login_required
def gestion_reportes(request):
    """ Renderiza la interfaz web del módulo de reportería analítica """
    return render(request, 'gestion_reportes.html')

def api_datos_reportes(request):
    """ API asíncrona que calcula y despacha los crudos estadísticos estructurados en formato JSON """
    filtro = request.GET.get('filtro', 'actualmente')
    fecha_inicio, fecha_fin = obtener_fechas_filtro(filtro)

    # Filtrar el universo de pagos basándonos en los límites temporales calculados
    pagos_filtrados = Pago.objects.filter(fecha__lte=fecha_fin)
    if fecha_inicio:
        pagos_filtrados = pagos_filtrados.filter(fecha__gte=fecha_inicio)

    # Cálculo directo de la tarjeta en USD
    totales = pagos_filtrados.aggregate(total_usd=Sum('montoUSD'))
    tarjeta_usd = float(totales['total_usd'] or 0.0)
    tarjeta_ves = 0.0

    # GRÁFICA 1: Agrupación por método de pago
    g1_consultas = pagos_filtrados.values('metodo').annotate(total_ingresos=Sum('montoUSD'))
    
    metodos_sistema = {
        'Efectivo $': 0.0,
        'Efectivo Bs': 0.0,
        'Transferencia': 0.0,
        'Pago Móvil': 0.0,
        'Zelle': 0.0
    }
    
    for item in g1_consultas:
        if 'metodo' in item and item['metodo'] in metodos_sistema:
            monto_val = item['total_ingresos'] if item['total_ingresos'] is not None else 0.0
            metodos_sistema[item['metodo']] = float(monto_val)
    
    g1_labels = list(metodos_sistema.keys())
    g1_data = list(metodos_sistema.values())

    # GRÁFICA 2: Recaudación distribuida por semanas del mes activo
    semana_data = [0.0, 0.0, 0.0, 0.0]
    
    for pago in pagos_filtrados:
        monto_pago = float(pago.montoUSD) if pago.montoUSD is not None else 0.0
        tasa_bcv = float(pago.tasa) if pago.tasa is not None else 0.0
        
        # Acumulación matemática del contravalor en Bolívares
        tarjeta_ves += (monto_pago * tasa_bcv)

        if pago.fecha:  
            try:
                dia_pago = pago.fecha.day
                if dia_pago <= 7:
                    semana_data[0] += monto_pago
                elif dia_pago <= 14:
                    semana_data[1] += monto_pago
                elif dia_pago <= 21:
                    semana_data[2] += monto_pago
                else:
                    semana_data[3] += monto_pago
            except AttributeError:
                continue

    g_semanas_labels = ["Semana 1", "Semana 2", "Semana 3", "Semana 4+"]

    # GRÁFICA 3: Mapeo de clientes por estado operacional
    g2_consultas = Cliente.objects.filter(borrado=False).values('estado').annotate(total_clientes=Count('id'))
    g2_labels = []
    g2_data = []
    
    for item in g2_consultas:
        if 'estado' in item:
            g2_labels.append(item['estado'])
            g2_data.append(int(item['total_clientes'] or 0))

    # === RECOLECCIÓN PARA GRÁFICA 4: Planes de Internet más Vendidos ===
    g4_consultas = Cliente.objects.filter(borrado=False)\
                                  .values('idPlan__plan')\
                                  .annotate(total=Count('id'))\
                                  .order_by('-total')
    g4_labels = []
    g4_data = []
    for item in g4_consultas:
        nombre_plan = item['idPlan__plan'] if item['idPlan__plan'] else "Sin Plan"
        g4_labels.append(str(nombre_plan))
        g4_data.append(int(item['total'] or 0))

    # === RECOLECCIÓN PARA GRÁFICA 5: Evolución de Ingresos Mensuales ===
    from django.db.models.functions import ExtractMonth, ExtractYear
    g5_consultas = Pago.objects.annotate(
        año=ExtractYear('fecha'), 
        mes=ExtractMonth('fecha')
    ).values('año', 'mes').annotate(total=Sum('montoUSD')).order_by('año', 'mes')

    meses_nombre = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    g5_labels = []
    g5_data = []
    for item in g5_consultas:
        if item['mes']:
            label_mes = f"{meses_nombre[int(item['mes'])-1]} {str(item['año'])[-2:]}"
            g5_labels.append(label_mes)
            g5_data.append(float(item['total'] or 0.0))

    return JsonResponse({
        "tarjetas": {
            "usd": tarjeta_usd,
            "ves": tarjeta_ves
        },
        "ingresos_metodo": {
            "labels": g1_labels,
            "data": g1_data,
            "titulo": "Distribución de Ingresos por Método de Pago ($)"
        },
        "ingresos_semanas": {
            "labels": g_semanas_labels,
            "data": semana_data,
            "titulo": "Recaudación Distribuida por Semanas ($)"
        },
        "clientes_estado": {
            "labels": g2_labels,
            "data": g2_data,
            "titulo": "Estado Actual de la Base de Clientes"
        },
        "planes_vendidos": {
            "labels": g4_labels,
            "data": g4_data,
            "titulo": "Planes de Internet más Vendidos"
        },
        "evolucion_ingresos": {
            "labels": g5_labels if g5_labels else ["Sin Datos"],
            "data": g5_data if g5_data else [0.0],
            "titulo": "Evolución de Ingresos Mensuales ($)"
        }
    })

@login_required
def descargar_reporte_pdf(request):
    """ Genera y fuerza la descarga de un reporte PDF institucional estructurado con ReportLab """
    criterio = request.GET.get('filtro', 'actualmente')
    fecha_inicio, fecha_fin = obtener_fechas_filtro(criterio)

    # Filtrar el universo transaccional
    pagos_filtrados = Pago.objects.filter(fecha__lte=fecha_fin)
    if fecha_inicio:
        pagos_filtrados = pagos_filtrados.filter(fecha__gte=fecha_inicio)

    # Cálculos globales directos
    agregados = pagos_filtrados.aggregate(total_usd=Sum('montoUSD'))
    total_usd = float(agregados['total_usd'] or 0.0)
    total_ves = 0.0

    for p in pagos_filtrados:
        m_usd = float(p.montoUSD) if p.montoUSD is not None else 0.0
        t_bcv = float(p.tasa) if p.tasa is not None else 0.0
        total_ves += (m_usd * t_bcv)

    # Configuración de cabeceras HTTP de respuesta
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_{criterio}.pdf"'

    # Construcción del Documento ReportLab
    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=65, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()

    # Estilos Personalizados
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=22,
        textColor=colors.HexColor('#1a365d'), spaceAfter=6
    )
    meta_style = ParagraphStyle(
        'DocMeta', parent=styles['Normal'], fontName='Helvetica', fontSize=10,
        textColor=colors.HexColor('#4a5568'), spaceAfter=20
    )
    section_style = ParagraphStyle(
        'SectionHeader', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=14,
        textColor=colors.HexColor('#2c5282'), spaceBefore=15, spaceAfter=10
    )

    # Elementos de Encabezado
    story.append(Paragraph("MikroCore - Reporte Integral de Operaciones", title_style))
    
    texto_filtro = criterio.upper() if '-' in criterio or criterio != 'actualmente' else "HISTÓRICO GLOBAL"
    if criterio == 'mes': texto_filtro = "MES EN CURSO"
    if criterio == '7dias': texto_filtro = "ÚLTIMOS 7 DÍAS"

    # === CONSULTA DE AUDITORÍA: HORA OBTENIDA DESDE EL SERVIDOR DE BASE DE DATOS ===
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT NOW();")
            resultado = cursor.fetchone()
            ahora_servidor = resultado[0]
            if hasattr(ahora_servidor, 'tzinfo') and ahora_servidor.tzinfo is not None:
                ahora_servidor = ahora_servidor.replace(tzinfo=None)
            fecha_emision = ahora_servidor.strftime('%d/%m/%Y %I:%M:%S %p')
    except Exception:
        fecha_emision = datetime.now().strftime('%d/%m/%Y %I:%M:%S %p')

    story.append(Paragraph(f"Filtro Aplicado: {texto_filtro} | Generado el: {fecha_emision}", meta_style))

    # --- TABLA 1: Consolidado Financiero General ---
    story.append(Paragraph("1. Consolidado Financiero General", section_style))
    data_tarjetas = [
        ['Moneda / Caja base', 'Total Recaudado'],
        ['Recaudación en (USD)', f"$ {formatear_moneda_ve(total_usd)}"],
        ['Recaudación en (Bs.)', f"Bs. {formatear_moneda_ve(total_ves)}"]
    ]
    t_tarjetas = Table(data_tarjetas, colWidths=[240, 200])
    t_tarjetas.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a365d')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f7fafc')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_tarjetas)
    story.append(Spacer(1, 15))

    # --- TABLA 2: Rendimiento por Canal de Recepción ---
    data_metodos = [['Método de Pago', 'Monto Equivalente ($)']]
    consultas_metodos = pagos_filtrados.values('metodo').annotate(total=Sum('montoUSD'))
    
    if consultas_metodos.exists():
        for p in consultas_metodos:
            monto_metodo = p['total'] if p['total'] is not None else 0.0
            data_metodos.append([str(p['metodo']), f"$ {formatear_moneda_ve(monto_metodo)}"])
    else:
        data_metodos.append(['No se registraron transacciones', '$ 0,00'])
    
    t_metodos = Table(data_metodos, colWidths=[240, 200])
    t_metodos.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2b6cb0')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#edf2f7')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e0')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(Paragraph("2. Rendimiento por Canal de Recepción", section_style))
    story.append(t_metodos)

    # --- FUNCIÓN CALLBACK CON EL BUSCADOR NATIVO DE DJANGO ---
    def dibujar_fondo(canvas, doc):
        from django.contrib.staticfiles import finders
        canvas.saveState()
        
        # Le pedimos a Django que busque el archivo usando su propio mapa de estáticos
        ruta_logo = finders.find('images/Logo-1.png')
        
        # Coordenadas para ubicarlo arriba a la derecha
        ancho_pagina, alto_pagina = letter
        ancho_logo = 140  
        alto_logo = 35
        x = ancho_pagina - 40 - ancho_logo
        y = alto_pagina - 48
        
        if ruta_logo:
            try:
                canvas.drawImage(ruta_logo, x, y, width=ancho_logo, height=alto_logo, mask='auto')
            except Exception as e:
                canvas.setFont("Helvetica-Bold", 8)
                canvas.setFillColor(colors.HexColor('#e74c3c'))
                canvas.drawString(x - 50, y + 12, "Error: Formato de imagen inválido")
        else:
            # Si ni siquiera Django lo encuentra en sus estáticos, dejará este aviso sutil
            canvas.setFont("Helvetica-Bold", 8)
            canvas.setFillColor(colors.HexColor('#718096'))
            canvas.drawString(x - 60, y + 12, "[ Logo-1.png no mapeado en static ]")
        
        canvas.restoreState()
        
    doc.build(story, onFirstPage=dibujar_fondo, onLaterPages=dibujar_fondo)
    return response