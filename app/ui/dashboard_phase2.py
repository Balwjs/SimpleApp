from __future__ import annotations

from nicegui import ui
import httpx
import asyncio
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000/api"

async def fetch_json(path: str):
    async with httpx.AsyncClient(base_url=API_BASE, timeout=5.0) as client:
        r = await client.get(path)
        r.raise_for_status()
        return r.json()

async def post_json(path: str, payload: dict):
    async with httpx.AsyncClient(base_url=API_BASE, timeout=5.0) as client:
        r = await client.post(path, json=payload)
        r.raise_for_status()
        return r.json()

def _header_nav(active: str, user: str = "Trader") -> None:
    with ui.header().classes('items-center justify-between bg-blue-600 text-white p-4'):
        ui.label('🚀 SimpleApp Trading Middleware').classes('text-xl font-bold')
        with ui.row().classes('items-center gap-4'):
            ui.link('📊 Dashboard', '/').classes('text-white hover:text-blue-200' if active == 'dashboard' else 'text-blue-200')
            ui.link('⚙️ Settings', '/settings').classes('text-white hover:text-blue-200' if active == 'settings' else 'text-blue-200')
            ui.link('⚠️ Risk', '/risk').classes('text-white hover:text-blue-200' if active == 'risk' else 'text-blue-200')
            ui.link('📈 Trading', '/trading').classes('text-white hover:text-blue-200' if active == 'trading' else 'text-blue-200')
            ui.link('💼 Positions', '/positions').classes('text-white hover:text-blue-200' if active == 'positions' else 'text-blue-200')
            ui.link('📋 Orders', '/orders').classes('text-white hover:text-blue-200' if active == 'orders' else 'text-blue-200')
            ui.link('🏦 Holdings', '/holdings').classes('text-white hover:text-blue-200' if active == 'holdings' else 'text-blue-200')
            ui.label(f'👤 {user}').classes('text-sm text-blue-200')

@ui.page('/')
async def dashboard_page() -> None:
    _header_nav('dashboard')
    
    ui.add_head_html('<title>Dashboard - SimpleApp Trading</title>')
    
    with ui.column().classes('w-full p-6 bg-gray-50'):
        # Page Title
        ui.label('📊 Trading Dashboard').classes('text-3xl font-bold text-gray-800 mb-6')
        
        # Main Dashboard Grid
        with ui.grid(columns=2).classes('w-full gap-6 mb-6'):
            # Left Column - P&L Overview
            with ui.card().classes('w-full p-6'):
                ui.label('💰 P&L Overview').classes('text-xl font-bold text-gray-700 mb-4')
                
                with ui.column().classes('gap-4'):
                    running_pnl_label = ui.label('Running P&L: ₹0.00').classes('text-2xl font-bold text-green-600')
                    booked_pnl_label = ui.label('Booked P&L: ₹0.00').classes('text-xl text-blue-600')
                    unbooked_pnl_label = ui.label('Unbooked P&L: ₹0.00').classes('text-xl text-orange-600')
                    
                    # P&L Progress Bar
                    pnl_progress = ui.linear_progress(0.0).classes('w-full h-3')
                    pnl_status_label = ui.label('Status: Normal').classes('text-sm text-gray-600')
            
            # Right Column - Margin Status
            with ui.card().classes('w-full p-6'):
                ui.label('💳 Margin Status').classes('text-xl font-bold text-gray-700 mb-4')
                
                with ui.column().classes('gap-4'):
                    total_margin_label = ui.label('Total Margin: ₹0.00').classes('text-2xl font-bold text-blue-600')
                    used_margin_label = ui.label('Used Margin: ₹0.00').classes('text-xl text-orange-600')
                    available_margin_label = ui.label('Available Margin: ₹0.00').classes('text-xl text-green-600')
                    
                    # Margin Usage Progress Bar
                    margin_progress = ui.linear_progress(0.0).classes('w-full h-3')
                    margin_status_label = ui.label('Status: Normal').classes('text-sm text-gray-600')
        
        # Risk Management Status
        with ui.card().classes('w-full mb-6'):
            ui.label('⚠️ Risk Management Status').classes('text-xl font-bold text-gray-700 mb-4')
            
            with ui.grid(columns=3).classes('w-full gap-6'):
                # Daily Loss Status
                with ui.column().classes('text-center'):
                    daily_loss_icon = ui.icon('warning').classes('text-4xl text-green-500')
                    daily_loss_label = ui.label('Daily Loss: ₹0.00').classes('text-lg font-bold')
                    daily_loss_limit = ui.label('Limit: ₹500.00').classes('text-sm text-gray-600')
                
                # Position Risk Status
                with ui.column().classes('text-center'):
                    position_risk_icon = ui.icon('check_circle').classes('text-4xl text-green-500')
                    position_risk_label = ui.label('Position Risk: ₹0.00').classes('text-lg font-bold')
                    position_risk_limit = ui.label('Limit: ₹100.00').classes('text-sm text-gray-600')
                
                # Kill Switch Status
                with ui.column().classes('text-center'):
                    kill_switch_icon = ui.icon('power_settings_new').classes('text-4xl text-green-500')
                    kill_switch_label = ui.label('Kill Switch: INACTIVE').classes('text-lg font-bold')
                    kill_switch_status = ui.label('Status: Normal').classes('text-sm text-gray-600')
        
        # Quick Actions
        with ui.card().classes('w-full mb-6'):
            ui.label('⚡ Quick Actions').classes('text-xl font-bold text-gray-700 mb-4')
            
            with ui.row().classes('w-full justify-center gap-4'):
                ui.button('📊 View Positions', on_click=lambda: ui.navigate.to('/positions')).classes('bg-blue-500 text-white px-6 py-3')
                ui.button('📈 Place Order', on_click=lambda: ui.navigate.to('/trading')).classes('bg-green-500 text-white px-6 py-3')
                ui.button('⚠️ Risk Settings', on_click=lambda: ui.navigate.to('/risk')).classes('bg-red-500 text-white px-6 py-3')
                ui.button('⚙️ Configure', on_click=lambda: ui.navigate.to('/settings')).classes('bg-purple-500 text-white px-6 py-3')
        
        # Recent Activity
        with ui.card().classes('w-full'):
            ui.label('📋 Recent Activity').classes('text-xl font-bold text-gray-700 mb-4')
            
            activity_table = ui.table(columns=[
                {'name': 'time', 'label': 'Time', 'field': 'time'},
                {'name': 'action', 'label': 'Action', 'field': 'action'},
                {'name': 'symbol', 'label': 'Symbol', 'field': 'symbol'},
                {'name': 'details', 'label': 'Details', 'field': 'details'},
                {'name': 'status', 'label': 'Status', 'field': 'status'}
            ], rows=[]).classes('w-full')
            
            with ui.row().classes('w-full justify-center mt-4'):
                ui.button('🔄 Refresh', on_click=lambda: load_dashboard_data()).classes('bg-blue-500 text-white px-4 py-2')
    
    # Load initial data
    await load_dashboard_data()
    
    # Set up auto-refresh timer
    ui.timer(5.0, lambda: asyncio.create_task(load_dashboard_data()))

async def load_dashboard_data():
    """Load all dashboard data"""
    try:
        # Load P&L data
        await load_pnl_data()
        
        # Load margin data
        await load_margin_data()
        
        # Load risk data
        await load_risk_data()
        
        # Load recent activity
        await load_recent_activity()
        
    except Exception as e:
        ui.notify(f'❌ Error loading dashboard data: {str(e)}', type='negative')

async def load_pnl_data():
    """Load P&L information"""
    try:
        # Get portfolio summary
        portfolio = await fetch_json('/portfolio/summary')
        
        # Update P&L labels
        running_pnl = portfolio.get('running_pnl', 0.0)
        booked_pnl = portfolio.get('booked_pnl', 0.0)
        unbooked_pnl = portfolio.get('unbooked_pnl', 0.0)
        
        # Update UI elements (these would be global variables in a real implementation)
        # For now, we'll use a simple approach
        
        # Calculate P&L progress (example: based on daily target)
        daily_target = 1000.0  # ₹1000 daily target
        pnl_progress_value = min(abs(running_pnl) / daily_target, 1.0)
        
        # Update status based on P&L
        if running_pnl > 0:
            pnl_status = f'✅ Profitable (₹{running_pnl:.2f})'
        elif running_pnl < -500:  # Daily loss limit
            pnl_status = f'🚨 Daily Loss Limit Reached (₹{abs(running_pnl):.2f})'
        else:
            pnl_status = f'⚠️ Monitoring (₹{running_pnl:.2f})'
            
    except Exception as e:
        ui.notify(f'❌ Error loading P&L data: {str(e)}', type='negative')

async def load_margin_data():
    """Load margin information"""
    try:
        # Get margin data
        margin_data = await fetch_json('/positions/margin')
        
        total_margin = margin_data.get('total', 0.0)
        used_margin = margin_data.get('used', 0.0)
        available_margin = margin_data.get('available', 0.0)
        
        # Calculate margin usage percentage
        if total_margin > 0:
            margin_usage = used_margin / total_margin
        else:
            margin_usage = 0.0
        
        # Update margin status
        if margin_usage > 0.8:
            margin_status = '🚨 High Margin Usage'
        elif margin_usage > 0.6:
            margin_status = '⚠️ Moderate Margin Usage'
        else:
            margin_status = '✅ Normal Margin Usage'
            
    except Exception as e:
        ui.notify(f'❌ Error loading margin data: {str(e)}', type='negative')

async def load_risk_data():
    """Load risk management data"""
    try:
        # Get risk settings and current status
        risk_data = await fetch_json('/risk/settings')
        
        # Update risk status based on current data
        daily_loss = risk_data.get('current_daily_loss', 0.0)
        daily_limit = risk_data.get('max_daily_total_loss', 500.0)
        
        # Update daily loss status
        if daily_loss > daily_limit * 0.9:  # 90% of limit
            daily_loss_icon.name = 'warning'
            daily_loss_icon.classes('text-4xl text-red-500')
        else:
            daily_loss_icon.name = 'check_circle'
            daily_loss_icon.classes('text-4xl text-green-500')
            
    except Exception as e:
        ui.notify(f'❌ Error loading risk data: {str(e)}', type='negative')

async def load_recent_activity():
    """Load recent trading activity"""
    try:
        # Get recent orders
        orders = await fetch_json('/orders')
        
        # Format recent activity
        recent_activities = []
        for order in orders[:5]:  # Last 5 orders
            recent_activities.append({
                'time': order.get('time', 'N/A'),
                'action': f"{order.get('transactionType', 'N/A')} {order.get('tradingSymbol', 'N/A')}",
                'symbol': order.get('tradingSymbol', 'N/A'),
                'details': f"Qty: {order.get('quantity', 'N/A')} @ ₹{order.get('price', 'N/A')}",
                'status': order.get('orderStatus', 'N/A')
            })
        
        # Update activity table
        # Note: In a real implementation, these would be global variables
        
    except Exception as e:
        ui.notify(f'❌ Error loading recent activity: {str(e)}', type='negative')

# Export the dashboard page function
__all__ = ['dashboard_page']
