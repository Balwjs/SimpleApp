from __future__ import annotations

from nicegui import ui
import httpx

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

@ui.page('/settings')
async def settings_page() -> None:
    _header_nav('settings')
    
    ui.add_head_html('<title>Settings - SimpleApp Trading</title>')
    
    # Create UI elements as class variables so they can be accessed by functions
    class SettingsUI:
        def __init__(self):
            self.max_daily_loss = None
            self.max_position_loss = None
            self.position_profit_target = None
            self.total_profit_target = None
            self.daily_loss_display = None
            self.position_loss_display = None
            self.profit_target_display = None
            self.total_profit_display = None
            self.status_display = None
    
    settings_ui = SettingsUI()
    
    with ui.column().classes('w-full p-6 bg-gray-50'):
        # Page Title
        ui.label('⚙️ Risk Management Settings').classes('text-3xl font-bold text-gray-800 mb-6')
        
        # Risk Configuration Section
        with ui.card().classes('w-full mb-6'):
            ui.label('🔒 Configure Risk Parameters').classes('text-xl font-bold text-gray-700 mb-4')
            
            with ui.grid(columns=2).classes('w-full gap-6'):
                # Left Column - Input Fields
                with ui.column().classes('gap-4'):
                    ui.label('Max Daily Total Loss (₹)').classes('text-sm font-medium text-gray-600')
                    settings_ui.max_daily_loss = ui.number('500.0', step=0.01).props('outlined dense').classes('w-full')
                    
                    ui.label('Max Daily Loss Per Position (₹)').classes('text-sm font-medium text-gray-600')
                    settings_ui.max_position_loss = ui.number('100.0', step=0.01).props('outlined dense').classes('w-full')
                    
                    ui.label('Per Position Daily Profit Target (₹)').classes('text-sm font-medium text-gray-600')
                    settings_ui.position_profit_target = ui.number('200.0', step=0.01).props('outlined dense').classes('w-full')
                    
                    ui.label('Max Daily Total Profit Target (₹)').classes('text-sm font-medium text-gray-600')
                    settings_ui.total_profit_target = ui.number('1000.0', step=0.01).props('outlined dense').classes('w-full')
                
                # Right Column - Action Buttons
                with ui.column().classes('gap-4 justify-center'):
                    ui.button('💾 Save Settings', on_click=lambda: save_risk_settings(settings_ui)).classes('bg-green-500 text-white px-6 py-2')
                    ui.button('🔒 Lock Settings', on_click=lambda: lock_risk_settings(settings_ui)).classes('bg-orange-500 text-white px-6 py-2')
                    ui.button('🔓 Unlock Settings', on_click=lambda: unlock_risk_settings(settings_ui)).classes('bg-blue-500 text-white px-6 py-2')
        
        # Current Settings Display
        with ui.card().classes('w-full mb-6'):
            ui.label('📊 Current Settings Display').classes('text-xl font-bold text-gray-700 mb-4')
            
            with ui.grid(columns=2).classes('w-full gap-6'):
                # Left Column - Settings Values
                with ui.column().classes('gap-4'):
                    settings_ui.daily_loss_display = ui.label('Max Daily Total: ₹500.00').classes('text-lg text-gray-700')
                    settings_ui.position_loss_display = ui.label('Max Position: ₹100.00').classes('text-lg text-gray-700')
                    settings_ui.profit_target_display = ui.label('Position Target: ₹200.00').classes('text-lg text-gray-700')
                    settings_ui.total_profit_display = ui.label('Total Target: ₹1000.00').classes('text-lg text-gray-700')
                
                # Right Column - Status
                with ui.column().classes('gap-4'):
                    settings_ui.status_display = ui.label('Status: 🔓 UNLOCKED').classes('text-lg font-bold text-green-600')
                    
                    with ui.row().classes('gap-4'):
                        ui.button('🔄 Refresh', on_click=lambda: load_current_settings(settings_ui)).classes('bg-blue-500 text-white')
        
        # Navigation Links
        with ui.row().classes('w-full justify-center gap-4 mt-6'):
            ui.button('📊 Dashboard', on_click=lambda: ui.navigate.to('/')).classes('bg-blue-500 text-white px-4 py-2')
            ui.button('⚠️ Risk', on_click=lambda: ui.navigate.to('/risk')).classes('bg-red-500 text-white px-4 py-2')
            ui.button('💼 Positions', on_click=lambda: ui.navigate.to('/positions')).classes('bg-green-500 text-white px-4 py-2')
            ui.button('📈 Trading', on_click=lambda: ui.navigate.to('/trading')).classes('bg-purple-500 text-white px-4 py-2')
            ui.button('📋 Orders', on_click=lambda: ui.navigate.to('/orders')).classes('bg-indigo-500 text-white px-4 py-2')
    
    # Load current settings on page load
    await load_current_settings(settings_ui)

async def save_risk_settings(settings_ui):
    """Save risk settings to backend"""
    try:
        settings_data = {
            'max_daily_total_loss': float(settings_ui.max_daily_loss.value or 0),
            'max_daily_loss_per_position': float(settings_ui.max_position_loss.value or 0),
            'per_position_daily_profit_target': float(settings_ui.position_profit_target.value or 0),
            'max_daily_total_profit_target': float(settings_ui.total_profit_target.value or 0)
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{API_BASE}/risk/settings',
                json=settings_data,
                headers={'Authorization': 'Bearer dhan_test_token_123'}
            )
            
            if response.status_code == 200:
                ui.notify('✅ Settings saved successfully!', type='positive')
                await load_current_settings(settings_ui)  # Refresh display
            else:
                ui.notify(f'❌ Failed to save settings: {response.text}', type='negative')
                
    except Exception as e:
        ui.notify(f'❌ Error saving settings: {str(e)}', type='negative')

async def lock_risk_settings(settings_ui):
    """Lock risk settings"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{API_BASE}/risk/lock',
                headers={'Authorization': 'Bearer dhan_test_token_123'}
            )
            
            if response.status_code == 200:
                ui.notify('🔒 Settings locked successfully!', type='positive')
                await load_current_settings(settings_ui)
            else:
                ui.notify(f'❌ Failed to lock settings: {response.text}', type='negative')
                
    except Exception as e:
        ui.notify(f'❌ Error locking settings: {str(e)}', type='negative')

async def unlock_risk_settings(settings_ui):
    """Unlock risk settings"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{API_BASE}/risk/unlock',
                headers={'Authorization': 'Bearer dhan_test_token_123'}
            )
            
            if response.status_code == 200:
                ui.notify('🔓 Settings unlocked successfully!', type='positive')
                await load_current_settings(settings_ui)
            else:
                ui.notify(f'❌ Failed to unlock settings: {response.text}', type='negative')
                
    except Exception as e:
        ui.notify(f'❌ Error unlocking settings: {str(e)}', type='negative')

async def load_current_settings(settings_ui):
    """Load current settings from backend"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'{API_BASE}/risk/settings',
                headers={'Authorization': 'Bearer dhan_test_token_123'}
            )
            
            if response.status_code == 200:
                settings = response.json()
                
                # Update input fields
                settings_ui.max_daily_loss.value = settings.get('max_daily_total_loss', 500.0)
                settings_ui.max_position_loss.value = settings.get('max_daily_loss_per_position', 100.0)
                settings_ui.position_profit_target.value = settings.get('per_position_daily_profit_target', 200.0)
                settings_ui.total_profit_target.value = settings.get('max_daily_total_profit_target', 1000.0)
                
                # Update display
                settings_ui.daily_loss_display.text = f'Max Daily Total: ₹{settings.get("max_daily_total_loss", 500.0):.2f}'
                settings_ui.position_loss_display.text = f'Max Position: ₹{settings.get("max_daily_loss_per_position", 100.0):.2f}'
                settings_ui.profit_target_display.text = f'Position Target: ₹{settings.get("per_position_daily_profit_target", 200.0):.2f}'
                settings_ui.total_profit_display.text = f'Total Target: ₹{settings.get("max_daily_total_profit_target", 1000.0):.2f}'
                
                # Update status
                is_locked = settings.get('risk_locked', False)
                if is_locked:
                    settings_ui.status_display.text = 'Status: 🔒 LOCKED'
                    settings_ui.status_display.classes('text-lg font-bold text-red-600')
                else:
                    settings_ui.status_display.text = 'Status: 🔓 UNLOCKED'
                    settings_ui.status_display.classes('text-lg font-bold text-green-600')
                    
            else:
                ui.notify(f'❌ Failed to load settings: {response.text}', type='negative')
                
    except Exception as e:
        ui.notify(f'❌ Error loading settings: {str(e)}', type='negative')

# Export the settings page function
__all__ = ['settings_page']
