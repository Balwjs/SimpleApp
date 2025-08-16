from __future__ import annotations

from nicegui import ui
import httpx
import asyncio

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

@ui.page('/risk')
async def risk_page() -> None:
    _header_nav('risk')
    
    ui.add_head_html('<title>Risk Management - SimpleApp Trading</title>')
    
    # Create UI elements as class variables so they can be accessed by functions
    class RiskUI:
        def __init__(self):
            self.daily_loss_label = None
            self.position_loss_label = None
            self.profit_target_label = None
            self.kill_switch_label = None
            self.risk_alerts_container = None
            self.risk_metrics_table = None
    
    risk_ui = RiskUI()
    
    with ui.column().classes('w-full p-6 bg-gray-50'):
        # Page Title
        ui.label('⚠️ Risk Management Dashboard').classes('text-3xl font-bold text-gray-800 mb-6')
        
        # Risk Status Overview
        with ui.card().classes('w-full mb-6'):
            ui.label('📊 Risk Status Overview').classes('text-xl font-bold text-gray-700 mb-4')
            
            with ui.grid(columns=4).classes('w-full gap-4'):
                # Daily Loss Status
                with ui.column().classes('text-center'):
                    daily_loss_icon = ui.icon('warning').classes('text-4xl text-green-500')
                    risk_ui.daily_loss_label = ui.label('Daily Loss: ₹0.00').classes('text-lg font-bold')
                    daily_loss_limit = ui.label('Limit: ₹500.00').classes('text-sm text-gray-600')
                
                # Position Risk Status
                with ui.column().classes('text-center'):
                    position_risk_icon = ui.icon('check_circle').classes('text-4xl text-green-500')
                    risk_ui.position_loss_label = ui.label('Position Risk: ₹0.00').classes('text-lg font-bold')
                    position_risk_limit = ui.label('Limit: ₹100.00').classes('text-sm text-gray-600')
                
                # Profit Target Status
                with ui.column().classes('text-center'):
                    profit_target_icon = ui.icon('trending_up').classes('text-4xl text-green-500')
                    risk_ui.profit_target_label = ui.label('Profit Target: ₹0.00').classes('text-lg font-bold')
                    profit_target_limit = ui.label('Target: ₹200.00').classes('text-sm text-gray-600')
                
                # Kill Switch Status
                with ui.column().classes('text-center'):
                    kill_switch_icon = ui.icon('power_settings_new').classes('text-4xl text-green-500')
                    risk_ui.kill_switch_label = ui.label('Kill Switch: INACTIVE').classes('text-lg font-bold')
                    kill_switch_status = ui.label('Status: Normal').classes('text-sm text-gray-600')
        
        # Risk Metrics Table
        with ui.card().classes('w-full mb-6'):
            ui.label('📈 Risk Metrics').classes('text-xl font-bold text-gray-700 mb-4')
            
            risk_ui.risk_metrics_table = ui.table(columns=[
                {'name': 'metric', 'label': 'Risk Metric', 'field': 'metric'},
                {'name': 'current', 'label': 'Current Value', 'field': 'current'},
                {'name': 'limit', 'label': 'Limit/Target', 'field': 'limit'},
                {'name': 'status', 'label': 'Status', 'field': 'status'},
                {'name': 'action', 'label': 'Action Required', 'field': 'action'}
            ], rows=[]).classes('w-full')
        
        # Risk Alerts
        with ui.card().classes('w-full mb-6'):
            ui.label('🚨 Risk Alerts').classes('text-xl font-bold text-gray-700 mb-4')
            
            risk_ui.risk_alerts_container = ui.column().classes('w-full gap-2')
            
            # Add some default alerts
            with risk_ui.risk_alerts_container:
                ui.label('✅ All risk parameters within normal limits').classes('text-green-600 font-medium')
        
        # Emergency Controls
        with ui.card().classes('w-full mb-6'):
            ui.label('🚨 Emergency Controls').classes('text-xl font-bold text-gray-700 mb-4')
            
            with ui.row().classes('w-full justify-center gap-4'):
                ui.button('🚨 ACTIVATE KILL SWITCH', on_click=lambda: activate_emergency_stop(risk_ui)).classes('bg-red-600 text-white px-6 py-3 text-lg font-bold')
                ui.button('🔓 DEACTIVATE KILL SWITCH', on_click=lambda: deactivate_emergency_stop(risk_ui)).classes('bg-green-600 text-white px-6 py-3 text-lg font-bold')
                ui.button('📊 Refresh Risk Data', on_click=lambda: load_risk_data(risk_ui)).classes('bg-blue-500 text-white px-6 py-3')
        
        # Navigation Links
        with ui.row().classes('w-full justify-center gap-4 mt-6'):
            ui.button('📊 Dashboard', on_click=lambda: ui.navigate.to('/')).classes('bg-blue-500 text-white px-4 py-2')
            ui.button('⚙️ Settings', on_click=lambda: ui.navigate.to('/settings')).classes('bg-purple-500 text-white px-4 py-2')
            ui.button('📈 Trading', on_click=lambda: ui.navigate.to('/trading')).classes('bg-green-500 text-white px-4 py-2')
            ui.button('📋 Orders', on_click=lambda: ui.navigate.to('/orders')).classes('bg-indigo-500 text-white px-4 py-2')
    
    # Load initial risk data
    await load_risk_data(risk_ui)
    
    # Set up auto-refresh timer
    ui.timer(3.0, lambda: asyncio.create_task(load_risk_data(risk_ui)))

async def load_risk_data(risk_ui):
    """Load risk management data"""
    try:
        # Get risk settings and current status
        risk_data = await fetch_json('/risk/settings')
        
        # Get current portfolio risk metrics
        portfolio_risk = await fetch_json('/live-data/risk-metrics')
        
        # Update risk status displays
        current_daily_loss = portfolio_risk.get('current_daily_loss', 0.0)
        current_position_loss = portfolio_risk.get('current_position_loss', 0.0)
        current_profit = portfolio_risk.get('current_profit', 0.0)
        
        # Update daily loss status
        daily_limit = risk_data.get('max_daily_total_loss', 500.0)
        if current_daily_loss > daily_limit * 0.9:  # 90% of limit
            risk_ui.daily_loss_label.text = f'Daily Loss: ₹{current_daily_loss:.2f} ⚠️'
            risk_ui.daily_loss_label.classes('text-lg font-bold text-red-600')
        else:
            risk_ui.daily_loss_label.text = f'Daily Loss: ₹{current_daily_loss:.2f}'
            risk_ui.daily_loss_label.classes('text-lg font-bold text-green-600')
        
        # Update position risk status
        position_limit = risk_data.get('max_daily_loss_per_position', 100.0)
        if current_position_loss > position_limit * 0.9:
            risk_ui.position_loss_label.text = f'Position Risk: ₹{current_position_loss:.2f} ⚠️'
            risk_ui.position_loss_label.classes('text-lg font-bold text-red-600')
        else:
            risk_ui.position_loss_label.text = f'Position Risk: ₹{current_position_loss:.2f}'
            risk_ui.position_loss_label.classes('text-lg font-bold text-green-600')
        
        # Update profit target status
        profit_target = risk_data.get('per_position_daily_profit_target', 200.0)
        if current_profit >= profit_target * 0.9:
            risk_ui.profit_target_label.text = f'Profit Target: ₹{current_profit:.2f} 🎯'
            risk_ui.profit_target_label.classes('text-lg font-bold text-green-600')
        else:
            risk_ui.profit_target_label.text = f'Profit Target: ₹{current_profit:.2f}'
            risk_ui.profit_target_label.classes('text-lg font-bold text-blue-600')
        
        # Update risk metrics table
        update_risk_metrics_table(risk_ui, risk_data, portfolio_risk)
        
        # Update risk alerts
        update_risk_alerts(risk_ui, risk_data, portfolio_risk)
        
    except Exception as e:
        ui.notify(f'❌ Error loading risk data: {str(e)}', type='negative')

def update_risk_metrics_table(risk_ui, risk_data, portfolio_risk):
    """Update the risk metrics table"""
    try:
        metrics_rows = [
            {
                'metric': 'Daily Total Loss',
                'current': f"₹{portfolio_risk.get('current_daily_loss', 0.0):.2f}",
                'limit': f"₹{risk_data.get('max_daily_total_loss', 500.0):.2f}",
                'status': '🟢 Normal' if portfolio_risk.get('current_daily_loss', 0.0) < risk_data.get('max_daily_total_loss', 500.0) * 0.8 else '🟡 Warning' if portfolio_risk.get('current_daily_loss', 0.0) < risk_data.get('max_daily_total_loss', 500.0) else '🔴 Critical',
                'action': 'Monitor' if portfolio_risk.get('current_daily_loss', 0.0) < risk_data.get('max_daily_total_loss', 500.0) * 0.8 else 'Reduce exposure' if portfolio_risk.get('current_daily_loss', 0.0) < risk_data.get('max_daily_total_loss', 500.0) else 'Stop trading'
            },
            {
                'metric': 'Position Loss',
                'current': f"₹{portfolio_risk.get('current_position_loss', 0.0):.2f}",
                'limit': f"₹{risk_data.get('max_daily_loss_per_position', 100.0):.2f}",
                'status': '🟢 Normal' if portfolio_risk.get('current_position_loss', 0.0) < risk_data.get('max_daily_loss_per_position', 100.0) * 0.8 else '🟡 Warning' if portfolio_risk.get('current_position_loss', 0.0) < risk_data.get('max_daily_loss_per_position', 100.0) else '🔴 Critical',
                'action': 'Monitor' if portfolio_risk.get('current_position_loss', 0.0) < risk_data.get('max_daily_loss_per_position', 100.0) * 0.8 else 'Close position' if portfolio_risk.get('current_position_loss', 0.0) < risk_data.get('max_daily_loss_per_position', 100.0) else 'Emergency close'
            },
            {
                'metric': 'Profit Target',
                'current': f"₹{portfolio_risk.get('current_profit', 0.0):.2f}",
                'limit': f"₹{risk_data.get('per_position_daily_profit_target', 200.0):.2f}",
                'status': '🟢 Target reached' if portfolio_risk.get('current_profit', 0.0) >= risk_data.get('per_position_daily_profit_target', 200.0) else '🟡 Approaching' if portfolio_risk.get('current_profit', 0.0) >= risk_data.get('per_position_daily_profit_target', 200.0) * 0.8 else '🔵 Building',
                'action': 'Take profit' if portfolio_risk.get('current_profit', 0.0) >= risk_data.get('per_position_daily_profit_target', 200.0) else 'Monitor' if portfolio_risk.get('current_profit', 0.0) >= risk_data.get('per_position_daily_profit_target', 200.0) * 0.8 else 'Continue building'
            }
        ]
        
        risk_ui.risk_metrics_table.rows = metrics_rows
        risk_ui.risk_metrics_table.update()
        
    except Exception as e:
        ui.notify(f'❌ Error updating risk metrics table: {str(e)}', type='negative')

def update_risk_alerts(risk_ui, risk_data, portfolio_risk):
    """Update risk alerts based on current status"""
    try:
        # Clear existing alerts
        risk_ui.risk_alerts_container.clear()
        
        alerts = []
        
        # Check daily loss limit
        current_daily_loss = portfolio_risk.get('current_daily_loss', 0.0)
        daily_limit = risk_data.get('max_daily_total_loss', 500.0)
        
        if current_daily_loss >= daily_limit:
            alerts.append(('🚨 CRITICAL: Daily loss limit reached!', 'text-red-600 font-bold'))
        elif current_daily_loss >= daily_limit * 0.8:
            alerts.append(('⚠️ WARNING: Approaching daily loss limit', 'text-orange-600 font-medium'))
        
        # Check position loss limit
        current_position_loss = portfolio_risk.get('current_position_loss', 0.0)
        position_limit = risk_data.get('max_daily_loss_per_position', 100.0)
        
        if current_position_loss >= position_limit:
            alerts.append(('🚨 CRITICAL: Position loss limit reached!', 'text-red-600 font-bold'))
        elif current_position_loss >= position_limit * 0.8:
            alerts.append(('⚠️ WARNING: Approaching position loss limit', 'text-orange-600 font-medium'))
        
        # Check profit targets
        current_profit = portfolio_risk.get('current_profit', 0.0)
        profit_target = risk_data.get('per_position_daily_profit_target', 200.0)
        
        if current_profit >= profit_target:
            alerts.append(('🎯 PROFIT TARGET REACHED! Consider taking profit', 'text-green-600 font-bold'))
        elif current_profit >= profit_target * 0.8:
            alerts.append(('📈 Approaching profit target', 'text-blue-600 font-medium'))
        
        # Add default status if no alerts
        if not alerts:
            alerts.append(('✅ All risk parameters within normal limits', 'text-green-600 font-medium'))
        
        # Display alerts
        for alert_text, alert_class in alerts:
            ui.label(alert_text).classes(alert_class)
            
    except Exception as e:
        ui.notify(f'❌ Error updating risk alerts: {str(e)}', type='negative')

async def activate_emergency_stop(risk_ui):
    """Activate emergency stop (kill switch)"""
    try:
        response = await post_json('/kill/activate', {'reason': 'Manual activation from risk dashboard'})
        
        if response:
            ui.notify('🚨 EMERGENCY STOP ACTIVATED! All trading halted.', type='negative')
            risk_ui.kill_switch_label.text = 'Kill Switch: ACTIVE'
            risk_ui.kill_switch_label.classes('text-lg font-bold text-red-600')
            
            # Add emergency alert
            with risk_ui.risk_alerts_container:
                ui.label('🚨 EMERGENCY STOP ACTIVATED - All trading halted!', 'text-red-600 font-bold')
        else:
            ui.notify('❌ Failed to activate emergency stop', type='negative')
            
    except Exception as e:
        ui.notify(f'❌ Error activating emergency stop: {str(e)}', type='negative')

async def deactivate_emergency_stop(risk_ui):
    """Deactivate emergency stop (kill switch)"""
    try:
        response = await post_json('/kill/deactivate', {'reason': 'Manual deactivation from risk dashboard'})
        
        if response:
            ui.notify('✅ Emergency stop deactivated. Trading resumed.', type='positive')
            risk_ui.kill_switch_label.text = 'Kill Switch: INACTIVE'
            risk_ui.kill_switch_label.classes('text-lg font-bold text-green-600')
            
            # Refresh risk data
            await load_risk_data(risk_ui)
        else:
            ui.notify('❌ Failed to deactivate emergency stop', type='negative')
            
    except Exception as e:
        ui.notify(f'❌ Error deactivating emergency stop: {str(e)}', type='negative')

# Export the risk page function
__all__ = ['risk_page']
